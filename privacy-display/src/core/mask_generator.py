"""
随机点阵掩模生成器

使用 ChaCha20 CSPRNG 生成统计独立的随机像素分配掩模。
每个周期将图像像素随机分配到 n 个子帧槽位中，满足：
  - 完备性：∑M_k(x,y) = 1 对每个像素成立
  - 互斥性：每像素在 n 个时隙中恰好激活一次
  - 周期独立：相邻周期掩模统计不相关
"""

import numpy as np
from scipy import stats
from Crypto.Cipher import ChaCha20
from Crypto.Hash import HMAC, SHA256
import os
import struct


class MaskGenerator:
    def __init__(self, width: int, height: int, n: int, key: bytes | None = None):
        """
        Args:
            width: 图像宽度（像素）
            height: 图像高度（像素）
            n: 子帧数量（拆分因子）
            key: 32 字节密钥，None 时随机生成
        """
        assert 2 <= n <= 16, "子帧数量 n 须在 [2, 16] 范围内"
        self.width = width
        self.height = height
        self.n = n
        self.key = key if key is not None else os.urandom(32)
        self._cycle_counter = 0
        self._pregenerated_masks: list[list[np.ndarray]] | None = None
        self._pregenerated_permutations: list[list[int]] | None = None
        self._pregenerate_start = 0
        self._pregenerate_cycles = 0

    def _derive_subkey(self, cycle: int) -> bytes:
        """HKDF 风格派生周期相关子密钥，确保不同周期掩模统计独立。"""
        h = HMAC.new(self.key, digestmod=SHA256)
        h.update(struct.pack(">Q", cycle))
        return h.digest()[:32]

    def _generate_index_matrix(self, cycle: int) -> np.ndarray:
        """
        生成随机索引矩阵 R(x,y) ∈ {0, 1, ..., n-1}。

        采用**拒绝采样**消除取模偏置：直接对 uint8 做 `% n`，当 n 不是 2 的
        幂（n∈{3,5,6,7}）时存在系统偏置（如 256 mod 3 = 1，值 0 多出现一次）。
        改为读 ⌈log₂n⌉ 位整数、落在 [n, 2^⌈log₂n⌉) 则丢弃重采，保证严格均匀。
        """
        subkey = self._derive_subkey(cycle)
        nonce = struct.pack(">Q", cycle)[:8]  # 8 字节 nonce
        cipher = ChaCha20.new(key=subkey, nonce=nonce)

        num_pixels = self.width * self.height
        bits = int(np.ceil(np.log2(self.n)))
        ceil_pow2 = 1 << bits  # 2^bits

        # n 为 2 的幂：无偏，直接取（bits 位整数恰好均匀覆盖 [0,n)）
        # n 非 2 的幂：拒绝采样
        out = np.empty(num_pixels, dtype=np.uint8)
        filled = 0
        # 接受率 = n / 2^bits，按此放大请求量并预留冗余
        accept_rate = self.n / ceil_pow2
        round_no = 0
        while filled < num_pixels:
            need = num_pixels - filled
            batch = int(need / accept_rate * 1.3) + 64
            # 以独立 counter 段读取，避免与上一轮重叠
            raw = np.frombuffer(cipher.encrypt(bytes(batch)), dtype=np.uint8)
            vals = raw & (ceil_pow2 - 1)  # 取低 bits 位（n≤16 故 bits≤4）
            accepted = vals[vals < self.n]
            take = min(len(accepted), need)
            out[filled:filled + take] = accepted[:take]
            filled += take
            round_no += 1
            if round_no > 1000:
                raise RuntimeError("拒绝采样未收敛")

        return out.reshape(self.height, self.width)

    def _chi_square_check(self, index_matrix: np.ndarray, p_threshold: float = 0.01) -> bool:
        """卡方均匀性检验，p > p_threshold 表示分布均匀。"""
        counts = np.bincount(index_matrix.ravel(), minlength=self.n)
        expected = np.full(self.n, self.width * self.height / self.n)
        chi2, p_value = stats.chisquare(counts, expected)
        return p_value > p_threshold

    def generate(self, cycle: int | None = None) -> list[np.ndarray]:
        """
        生成 n 个二值掩模矩阵 [M_0, M_1, ..., M_{n-1}]。

        Returns:
            list of ndarray, shape (H, W), dtype bool
            满足 sum(M_k) == ones_matrix（完备性）
        """
        if cycle is None:
            cycle = self._cycle_counter
            self._cycle_counter += 1

        max_retries = 5
        for _ in range(max_retries):
            R = self._generate_index_matrix(cycle)
            if self._chi_square_check(R):
                break
            cycle += 0x1_0000_0000  # 偏移种子重新生成
        else:
            # 超过重试次数时直接使用最后一次结果
            pass

        masks = [(R == k) for k in range(self.n)]
        return masks

    def generate_permutation(self, cycle: int | None = None) -> list[int]:
        """
        用 Fisher-Yates 洗牌生成子帧输出的伪随机置换序列。

        Returns:
            list of int, 长度为 n 的排列，表示子帧输出顺序
        """
        if cycle is None:
            cycle = self._cycle_counter - 1  # 与最新一次 generate 对应

        subkey = self._derive_subkey(cycle ^ 0xFFFF_FFFF)
        nonce = struct.pack(">Q", cycle ^ 0xFFFF_FFFF)[:8]
        cipher = ChaCha20.new(key=subkey, nonce=nonce)

        perm = list(range(self.n))
        for i in range(self.n - 1, 0, -1):
            j = self._uniform_int_from_cipher(cipher, i + 1)
            perm[i], perm[j] = perm[j], perm[i]
        return perm

    @staticmethod
    def _uniform_int_from_cipher(cipher, upper_exclusive: int) -> int:
        """
        从 ChaCha20 字节流中抽取 [0, upper_exclusive) 的无偏整数。

        直接对 uint32 做 `% upper_exclusive` 会在 upper_exclusive 不是
        2 的幂时产生极小但真实存在的取模偏置。这里使用拒绝采样：
        丢弃落在最大可整除区间之外的 uint32，再取模。
        """
        if upper_exclusive <= 0:
            raise ValueError("upper_exclusive must be positive")

        uint32_space = 1 << 32
        limit = uint32_space - (uint32_space % upper_exclusive)

        while True:
            raw = np.frombuffer(cipher.encrypt(bytes(4 * 8)), dtype=np.uint32)
            for value in raw:
                candidate = int(value)
                if candidate < limit:
                    return candidate % upper_exclusive

    def generate_view_differentiated(
        self, cycle: int, regions: tuple[int, int] = (3, 3)
    ) -> list[np.ndarray]:
        """
        视角差异化掩模（交底书 7.2，多相机协同攻击的缓解）。

        将屏幕空间分为 regions=(rows, cols) 个区域，每个区域用不同的区域
        子密钥派生独立的掩模序列。配合 LCD 的视角依赖特性，离轴相机在不同
        区域看到的子帧相位不同，无法对各区域统一帧对齐做时域平均重构；而
        正视用户（人眼积分）不受影响——各区域仍各自满足 ΣM_k=1 完备性。

        Args:
            cycle: 周期编号
            regions: (行数, 列数) 区域划分

        Returns:
            n 个全屏二值掩模，每个区域内部独立随机但全屏仍满足完备/互斥
        """
        rows, cols = regions
        R = np.empty((self.height, self.width), dtype=np.uint8)

        rh = self.height // rows
        rw = self.width // cols

        for r in range(rows):
            for c in range(cols):
                y0, y1 = r * rh, (self.height if r == rows - 1 else (r + 1) * rh)
                x0, x1 = c * rw, (self.width if c == cols - 1 else (c + 1) * rw)
                # 区域专属周期种子：cycle 与区域坐标绑定 → 区域间统计独立
                region_cycle = cycle ^ ((r * 73856093) ^ (c * 19349663)) & 0x7FFFFFFF
                sub = MaskGenerator(x1 - x0, y1 - y0, self.n, key=self.key)
                R[y0:y1, x0:x1] = sub._generate_index_matrix(region_cycle)

        return [(R == k) for k in range(self.n)]

    def pregenerate(self, cycles: int = 1024, start_cycle: int = 0) -> None:
        """
        预生成固定周期窗口内的掩模与置换环形缓冲。

        PoC 仍允许按需生成；该接口对应交底书 4.1.1/5.1 中的 1024 周期
        预生成思路。缓冲内容完全由 key+cycle 决定，因此同一 cycle 的
        预生成结果应与按需生成一致。
        """
        if cycles <= 0:
            raise ValueError("cycles must be positive")

        self._pregenerate_start = int(start_cycle)
        self._pregenerate_cycles = int(cycles)
        self._pregenerated_masks = []
        self._pregenerated_permutations = []

        for offset in range(cycles):
            cycle = start_cycle + offset
            self._pregenerated_masks.append(self.generate(cycle))
            self._pregenerated_permutations.append(self.generate_permutation(cycle))

    def get_pregenerated_masks(self, cycle: int) -> list[np.ndarray]:
        """从预生成环形缓冲读取掩模；返回副本，避免调用方修改缓存。"""
        if self._pregenerated_masks is None or self._pregenerate_cycles <= 0:
            raise RuntimeError("pregenerate() must be called before reading masks")
        idx = (cycle - self._pregenerate_start) % self._pregenerate_cycles
        return [mask.copy() for mask in self._pregenerated_masks[idx]]

    def get_pregenerated_permutation(self, cycle: int) -> list[int]:
        """从预生成环形缓冲读取置换序列。"""
        if self._pregenerated_permutations is None or self._pregenerate_cycles <= 0:
            raise RuntimeError("pregenerate() must be called before reading permutations")
        idx = (cycle - self._pregenerate_start) % self._pregenerate_cycles
        return list(self._pregenerated_permutations[idx])
