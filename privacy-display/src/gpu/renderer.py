"""
GPU 渲染驱动器（基于 moderngl）

在 GPU 着色器中执行掩模应用、噪声叠加与亮度补偿，
生成用于实时显示的子帧序列。
"""

import numpy as np
from pathlib import Path


SHADER_DIR = Path(__file__).parent / "shaders"


class GPURenderer:
    def __init__(self, width: int, height: int, n: int, gamma: float = 4.4):
        """
        Args:
            width, height: 图像分辨率
            n: 子帧数量
            gamma: 亮度补偿系数
        """
        self.width = width
        self.height = height
        self.n = n
        self.gamma = gamma
        self._ctx = None
        self._prog = None
        self._vao = None
        self._fbo = None
        self._initialized = False

    def _init_gl(self) -> None:
        """延迟初始化 OpenGL 上下文（需要在有效 GL 上下文中调用）。"""
        import moderngl as mgl

        self._ctx = mgl.create_standalone_context()
        vert_src = (SHADER_DIR / "mask_apply.vert").read_text()
        frag_src = (SHADER_DIR / "mask_apply.frag").read_text()
        self._prog = self._ctx.program(
            vertex_shader=vert_src,
            fragment_shader=frag_src,
        )

        # 全屏四边形顶点（NDC 坐标 + UV）
        vertices = np.array([
            -1.0, -1.0,  0.0, 0.0,
             1.0, -1.0,  1.0, 0.0,
            -1.0,  1.0,  0.0, 1.0,
             1.0,  1.0,  1.0, 1.0,
        ], dtype=np.float32)
        vbo = self._ctx.buffer(vertices.tobytes())
        self._vao = self._ctx.simple_vertex_array(
            self._prog, vbo, "in_position", "in_texcoord"
        )

        # 帧缓冲区（离屏渲染）
        color_attach = self._ctx.texture((self.width, self.height), 3)
        self._fbo = self._ctx.framebuffer(color_attachments=[color_attach])
        self._initialized = True

    def render_subframe(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        sub_noise: np.ndarray | None = None,
        inversion: bool = False,
    ) -> np.ndarray:
        """
        在 GPU 上渲染单个子帧。

        Args:
            image: uint8 (H, W, 3) 原始图像
            mask: bool (H, W) 掩模
            sub_noise: float32 (H, W, 3) 子噪声，值域 [-ε, ε]
            inversion: 是否输出反色帧

        Returns:
            uint8 (H, W, 3) 渲染后子帧
        """
        if not self._initialized:
            self._init_gl()

        import moderngl as mgl

        # 上传图像纹理
        img_data = np.flip(image, axis=0).astype(np.uint8).tobytes()
        img_tex = self._ctx.texture((self.width, self.height), 3, img_data)
        img_tex.filter = mgl.NEAREST, mgl.NEAREST

        # 上传掩模纹理（R8 单通道）
        mask_u8 = (mask.astype(np.uint8) * 255)
        mask_data = np.flip(mask_u8, axis=0).tobytes()
        mask_tex = self._ctx.texture((self.width, self.height), 1, mask_data)
        mask_tex.filter = mgl.NEAREST, mgl.NEAREST

        # 上传噪声纹理（float32，免量化误差）
        # sub_noise 单位为像素值空间 [-255, 255]，与 SoftwareRenderer 一致；
        # 转换到 shader 的 [0,1] 空间并以 0.5 为中心偏置（shader 中减回）
        if sub_noise is None:
            noise_arr = np.full((self.height, self.width, 3), 0.5, dtype=np.float32)
        else:
            noise_arr = (sub_noise / 255.0 + 0.5).astype(np.float32)
        noise_data = np.flip(noise_arr, axis=0).copy().tobytes()
        noise_tex = self._ctx.texture(
            (self.width, self.height), 3, noise_data, dtype="f4"
        )

        # 绑定纹理
        img_tex.use(0)
        mask_tex.use(1)
        noise_tex.use(2)
        self._prog["u_image"] = 0
        self._prog["u_mask"] = 1
        self._prog["u_noise"] = 2
        self._prog["u_gamma"] = self.gamma
        self._prog["u_inversion"] = inversion

        # 渲染到帧缓冲（顶点为 TRIANGLE_STRIP 布局的全屏四边形）
        self._fbo.use()
        self._ctx.clear(0.0, 0.0, 0.0, 1.0)
        self._vao.render(mgl.TRIANGLE_STRIP)

        # 读回 CPU
        raw = self._fbo.read(components=3, alignment=1)
        result = np.frombuffer(raw, dtype=np.uint8).reshape(self.height, self.width, 3)
        result = np.flip(result, axis=0).copy()

        # 释放纹理
        img_tex.release()
        mask_tex.release()
        noise_tex.release()

        return result

    def render_all_subframes(
        self,
        image: np.ndarray,
        masks: list[np.ndarray],
        sub_noises: list[np.ndarray] | None = None,
        permutation: list[int] | None = None,
    ) -> list[np.ndarray]:
        """
        按置换顺序渲染全部 n 个子帧。

        Returns:
            按 permutation 排序的子帧列表
        """
        if permutation is None:
            permutation = list(range(self.n))

        subframes = []
        for idx in permutation:
            noise = sub_noises[idx] if sub_noises else None
            sf = self.render_subframe(image, masks[idx], noise)
            subframes.append(sf)
        return subframes

    def release(self) -> None:
        if self._ctx:
            self._ctx.release()
            self._initialized = False


class SoftwareRenderer:
    """
    纯软件渲染回退（不依赖 OpenGL）。
    当 moderngl 不可用时使用，性能较低但功能完整。
    """

    def __init__(self, n: int, gamma: float = 4.4):
        self.n = n
        self.gamma = gamma

    def render_subframe(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        sub_noise: np.ndarray | None = None,
        inversion: bool = False,
    ) -> np.ndarray:
        img_f = image.astype(np.float32)
        mask3 = mask[:, :, np.newaxis]
        sf = img_f * mask3
        if sub_noise is not None:
            sf = sf + sub_noise
        sf = np.clip(sf * self.gamma, 0, 255)
        if inversion:
            sf = 255.0 - sf
        return sf.astype(np.uint8)

    def render_all_subframes(
        self,
        image: np.ndarray,
        masks: list[np.ndarray],
        sub_noises: list[np.ndarray] | None = None,
        permutation: list[int] | None = None,
    ) -> list[np.ndarray]:
        if permutation is None:
            permutation = list(range(self.n))
        return [
            self.render_subframe(
                image,
                masks[idx],
                sub_noises[idx] if sub_noises else None,
            )
            for idx in permutation
        ]


def create_renderer(width: int, height: int, n: int, gamma: float = 4.4):
    """工厂函数：优先使用 GPU 渲染器，失败时回退到软件渲染。"""
    try:
        import moderngl  # noqa: F401
        return GPURenderer(width, height, n, gamma)
    except ImportError:
        print("[警告] moderngl 未安装，使用软件渲染器")
        return SoftwareRenderer(n, gamma)
