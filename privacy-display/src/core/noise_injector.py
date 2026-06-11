"""
对抗性噪声注入器

基于 FGSM/PGD 生成针对 OCR/检测模型的对抗噪声，并将其分解为
时域互补的 n 个子噪声（∑N_k = 0），确保人眼积分后噪声完全消除。
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class TargetModelSpec:
    """目标识别模型的轻量代理配置。"""

    name: str
    family: str
    default_method: str
    edge_axis: str
    texture_frequency: float
    color_weights: tuple[float, float, float]
    pgd_iterations: int = 6
    step_scale: float = 0.35


DEFAULT_TARGET_MODELS: tuple[TargetModelSpec, ...] = (
    TargetModelSpec("tesseract", "ocr", "fgsm", "x", 9.0, (1.0, 1.0, 1.0)),
    TargetModelSpec("easyocr", "ocr", "pgd", "y", 13.0, (0.9, 1.1, 1.0)),
    TargetModelSpec("paddleocr", "ocr", "pgd", "laplace", 17.0, (1.1, 0.9, 1.0)),
    TargetModelSpec("yolov8", "detector", "pgd", "magnitude", 7.0, (1.0, 0.85, 1.15)),
    TargetModelSpec("faster_rcnn", "detector", "pgd", "coarse", 5.0, (1.15, 1.0, 0.85)),
)


class NoiseInjector:
    def __init__(
        self,
        n: int,
        epsilon: float = 8 / 255,
        template_dir: str | None = None,
        target_models: list[str] | None = None,
        max_epsilon: float | None = None,
        online_threshold: float = 0.20,
    ):
        """
        Args:
            n: 子帧数量
            epsilon: 噪声预算 ‖N_base‖_∞ ≤ ε，典型值 8/255
            template_dir: 预计算噪声模板目录
            target_models: 动态轮换的目标模型名称
            max_epsilon: 在线更新允许提升到的最大扰动预算
            online_threshold: 识别成功率高于该阈值时触发在线更新
        """
        self.n = n
        self.epsilon = epsilon
        self.max_epsilon = max_epsilon if max_epsilon is not None else epsilon
        self.online_threshold = online_threshold
        self.template_dir = Path(template_dir) if template_dir else None
        self._templates: dict[str, np.ndarray] = {}
        specs = {spec.name: spec for spec in DEFAULT_TARGET_MODELS}
        names = target_models or [spec.name for spec in DEFAULT_TARGET_MODELS]
        self._target_specs = {name: specs[name] for name in names if name in specs}
        if not self._target_specs:
            self._target_specs = {"tesseract": specs["tesseract"]}
        self._target_order = list(self._target_specs)
        self._rotation_counter = 0
        self._rotation_offset = 0
        self._online_state = {
            name: {
                "recognition_score": 0.0,
                "epsilon_scale": 1.0,
                "frequency_shift": 0.0,
                "preferred_method": self._target_specs[name].default_method,
                "updates": 0,
            }
            for name in self._target_order
        }

    # ------------------------------------------------------------------
    # 噪声生成
    # ------------------------------------------------------------------

    def generate_fgsm_noise(
        self,
        image: np.ndarray,
        model_name: str = "tesseract",
    ) -> np.ndarray:
        """
        生成 FGSM 对抗噪声。

        Tesseract/EasyOCR/PaddleOCR 等 OCR 引擎本身通常不可微；本 PoC
        使用模型特定的 OCR/检测代理梯度来近似端到端攻击方向，并保留
        模板库优先路径。生产级实现应替换为真实可微分影子模型。

        Args:
            image: float32 (H, W, 3)，值域 [0, 1]
            model_name: 目标 OCR 模型名称

        Returns:
            float32 (H, W, 3) 基础噪声，值域 [-ε, +ε]
        """
        template = self._get_template(model_name, image.shape[:2])
        if template is not None:
            return template

        spec = self._get_spec(model_name)
        eps = self._effective_epsilon(spec.name)
        grad = self._surrogate_gradient(image, spec)
        return (eps * np.sign(grad)).clip(-eps, eps).astype(np.float32)

    def generate_pgd_noise(
        self,
        image: np.ndarray,
        model_name: str = "easyocr",
        iterations: int | None = None,
        step_size: float | None = None,
        random_start: bool = True,
        seed: int | None = None,
    ) -> np.ndarray:
        """
        生成 PGD 对抗噪声，满足 L∞ 扰动预算。

        PGD 在 FGSM 的基础上迭代更新：每步沿目标模型代理梯度前进，
        并投影回 [-ε, ε] 约束盒。该接口用于交底书 3.2.2 的 PGD
        噪声模板生成与在线更新。
        """
        template = self._get_template(model_name, image.shape[:2])
        if template is not None:
            return template

        spec = self._get_spec(model_name)
        eps = self._effective_epsilon(spec.name)
        iters = iterations if iterations is not None else spec.pgd_iterations
        alpha = (
            step_size
            if step_size is not None
            else max(eps * spec.step_scale, eps / max(iters, 1))
        )

        rng = np.random.default_rng(seed)
        if random_start:
            perturb = rng.uniform(-eps, eps, image.shape).astype(np.float32)
        else:
            perturb = np.zeros_like(image, dtype=np.float32)

        image_f = image.astype(np.float32)
        for _ in range(max(1, iters)):
            adv = np.clip(image_f + perturb, 0.0, 1.0)
            grad = self._surrogate_gradient(adv, spec)
            perturb = perturb + alpha * np.sign(grad)
            perturb = np.clip(perturb, -eps, eps).astype(np.float32)
        return perturb

    def generate_rotating_noise(
        self,
        image: np.ndarray,
        cycle: int | None = None,
        method: str | None = None,
    ) -> tuple[np.ndarray, str, str]:
        """
        按伪随机/周期序列轮换目标模型并生成噪声。

        Returns:
            (noise, model_name, method)
        """
        model_name = self.select_target_model(cycle)
        selected_method = method or self._online_state[model_name]["preferred_method"]
        if selected_method == "pgd":
            noise = self.generate_pgd_noise(image, model_name=model_name, seed=cycle)
        else:
            noise = self.generate_fgsm_noise(image, model_name=model_name)
        return noise, model_name, selected_method

    def select_target_model(self, cycle: int | None = None) -> str:
        """选择当前周期的目标模型，覆盖 Tesseract/EasyOCR/PaddleOCR/检测模型轮换。"""
        if cycle is None:
            idx = self._rotation_counter
            self._rotation_counter += 1
        else:
            idx = cycle
        return self._target_order[(idx + self._rotation_offset) % len(self._target_order)]

    def update_online_strategy(
        self,
        model_name: str,
        recognition_score: float,
        threshold: float | None = None,
    ) -> dict:
        """
        在线对抗更新：当影子评估发现识别率上升时，提升策略强度。

        该方法不直接运行 OCR，而是接收外部监测得到的识别成功率；若分数
        超过阈值，则切换到 PGD、扰动预算向 max_epsilon 靠近，并改变空间
        频率相位，避免长期固定噪声形态。
        """
        spec = self._get_spec(model_name)
        state = self._online_state[spec.name]
        state["recognition_score"] = float(recognition_score)
        trigger = recognition_score > (
            self.online_threshold if threshold is None else threshold
        )
        if trigger:
            state["updates"] += 1
            state["preferred_method"] = "pgd"
            if self.epsilon > 0:
                max_scale = max(1.0, self.max_epsilon / self.epsilon)
            else:
                max_scale = 1.0
            state["epsilon_scale"] = min(max_scale, state["epsilon_scale"] * 1.25)
            state["frequency_shift"] = (state["frequency_shift"] + 0.17) % 1.0
            self._rotation_offset = (self._rotation_offset + 1) % len(self._target_order)
        return dict(state)

    def get_online_state(self, model_name: str) -> dict:
        """返回指定模型的在线更新状态快照。"""
        return dict(self._online_state[self._get_spec(model_name).name])

    def _get_spec(self, model_name: str) -> TargetModelSpec:
        return self._target_specs.get(model_name, self._target_specs["tesseract"])

    def _effective_epsilon(self, model_name: str) -> float:
        state = self._online_state.get(model_name, {})
        scale = float(state.get("epsilon_scale", 1.0))
        return float(min(self.max_epsilon, self.epsilon * scale))

    def _get_template(self, model_name: str, shape_hw: tuple[int, int]) -> np.ndarray | None:
        if model_name not in self._templates:
            return None
        template = self._templates[model_name]
        if template.shape[:2] != shape_hw:
            import cv2
            template = cv2.resize(template, (shape_hw[1], shape_hw[0]))
        eps = self._effective_epsilon(self._get_spec(model_name).name)
        return np.clip(template.astype(np.float32), -eps, eps)

    def _surrogate_gradient(self, image: np.ndarray, spec: TargetModelSpec) -> np.ndarray:
        """
        模型特定 OCR/检测代理梯度。

        OCR 目标强调文字笔画边缘和高频纹理；检测目标强调连通区域边界和
        coarse objectness。该函数提供可离线运行的可替换影子模型接口。
        """
        import cv2

        image_f = np.clip(image.astype(np.float32), 0.0, 1.0)
        img_uint8 = (image_f * 255).astype(np.uint8)
        gray = cv2.cvtColor(img_uint8, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0

        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        lap = cv2.Laplacian(gray, cv2.CV_32F, ksize=3)
        mag = np.sqrt(gx ** 2 + gy ** 2)

        if spec.edge_axis == "x":
            base = gx + 0.35 * lap
        elif spec.edge_axis == "y":
            base = gy + 0.35 * lap
        elif spec.edge_axis == "laplace":
            base = lap + 0.25 * (gx - gy)
        elif spec.edge_axis == "coarse":
            base = cv2.GaussianBlur(mag, (0, 0), 2.0) + 0.2 * lap
        else:
            base = mag + 0.2 * lap

        h, w = gray.shape
        yy, xx = np.mgrid[0:h, 0:w]
        shift = self._online_state.get(spec.name, {}).get("frequency_shift", 0.0)
        phase = 2 * np.pi * shift
        texture = np.sin(
            (xx + yy * 0.37)
            * spec.texture_frequency
            / max(w, 1)
            * 2
            * np.pi
            + phase
        )
        high_freq = texture.astype(np.float32) * (mag > np.percentile(mag, 55)).astype(np.float32)

        if spec.family == "detector":
            surrogate = 0.65 * base + 0.35 * high_freq
        else:
            surrogate = 0.75 * base + 0.25 * high_freq

        if np.max(np.abs(surrogate)) > 1e-8:
            surrogate = surrogate / (np.max(np.abs(surrogate)) + 1e-8)
        else:
            surrogate = np.ones_like(surrogate, dtype=np.float32)

        weights = np.array(spec.color_weights, dtype=np.float32).reshape(1, 1, 3)
        grad = surrogate[:, :, None] * weights
        return grad.astype(np.float32)

    def _gradient_based_noise(self, image: np.ndarray) -> np.ndarray:
        """
        基于图像空间梯度的近似对抗噪声。
        在文字边缘高频区域集中施加 ε 扰动，最大化 OCR 混淆。
        """
        import cv2

        img_uint8 = (image * 255).clip(0, 255).astype(np.uint8)
        gray = cv2.cvtColor(img_uint8, cv2.COLOR_RGB2GRAY)

        # Sobel 梯度（文字边缘方向）
        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        grad_mag = np.sqrt(gx ** 2 + gy ** 2)

        # 归一化为符号图（-1 或 +1）
        sign_gx = np.sign(gx)
        sign_gy = np.sign(gy)

        # 在梯度强的区域施加有界噪声，其他区域加随机噪声
        rng = np.random.default_rng()
        noise_gray = np.where(
            grad_mag > np.percentile(grad_mag, 60),
            sign_gx * self.epsilon,
            rng.uniform(-self.epsilon * 0.3, self.epsilon * 0.3, gray.shape),
        ).astype(np.float32)

        # 扩展为 3 通道
        noise = np.stack([noise_gray] * 3, axis=-1)
        return np.clip(noise, -self.epsilon, self.epsilon)

    def generate_pytorch_fgsm(
        self,
        image: np.ndarray,
        model_name: str = "vgg11_pretrained",
    ) -> np.ndarray:
        """
        使用**预训练** PyTorch 模型进行 FGSM 梯度攻击（需安装 torch）。

        修复：原实现用 `weights=None`（随机初始化、未训练）的 VGG，其梯度是
        无意义噪声、不构成对抗攻击。改用 ImageNet 预训练权重，对真实学习到的
        视觉特征做有界扰动，这才是有意义的代理对抗（proxy adversarial）。

        说明：真正针对 OCR 的端到端攻击需可微分 OCR（如 CRNN）；此处以预训练
        CNN 特征作代理，破坏 OCR 依赖的低层边缘/纹理特征。配合 split_complementary
        后人眼积分仍可消除（ΣN_k=0）。

        Args:
            image: float32 (H,W,3)，值域 [0,1]
        """
        try:
            import torch
            import torchvision.models as models
            from torchvision.models import VGG11_Weights
        except ImportError:
            return self._gradient_based_noise(image)

        try:
            img_tensor = torch.from_numpy(image.transpose(2, 0, 1)).float().unsqueeze(0)
            img_tensor.requires_grad = True

            # 预训练特征提取器（ImageNet 学到的真实低层特征）
            weights = VGG11_Weights.DEFAULT
            proxy = models.vgg11(weights=weights).features[:8]
            proxy.eval()
            for p in proxy.parameters():
                p.requires_grad = False

            # ImageNet 归一化
            mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
            std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
            normed = (img_tensor - mean) / std

            features = proxy(normed)
            # 最大化特征响应 L2（FGSM：沿增大特征扰动方向，破坏稳定文字特征）
            loss = features.pow(2).mean()
            loss.backward()

            grad = img_tensor.grad.data.squeeze(0).numpy().transpose(1, 2, 0)
            noise = self.epsilon * np.sign(grad)
            return np.clip(noise, -self.epsilon, self.epsilon).astype(np.float32)
        except Exception:
            return self._gradient_based_noise(image)

    # ------------------------------------------------------------------
    # 互补子噪声分配
    # ------------------------------------------------------------------

    def split_complementary(
        self, noise_base: np.ndarray
    ) -> list[np.ndarray]:
        """
        将基础噪声分解为 n 个时域互补子噪声，满足 ∑N_k = 0。

        策略：交替极性分配
          偶数 n：N_k = (-1)^(k+1) * noise_base / (n/2)
          奇数 n：最后一个子噪声设为前 n-1 个的负和
        """
        assert self.n >= 2

        sub_noises = []
        if self.n % 2 == 0:
            amplitude = noise_base / (self.n // 2)
            for k in range(self.n):
                sign = 1 if k % 2 == 0 else -1
                sub_noises.append((sign * amplitude).astype(np.float32))
        else:
            # 奇数：前 n-1 个交替，最后一个补偿
            amplitude = noise_base / ((self.n - 1) // 2)
            for k in range(self.n - 1):
                sign = 1 if k % 2 == 0 else -1
                sub_noises.append((sign * amplitude).astype(np.float32))
            remainder = -sum(sub_noises)
            sub_noises.append(remainder.astype(np.float32))

        # 验证互补性
        total = sum(sub_noises)
        assert np.max(np.abs(total)) < 1e-5, "子噪声互补性验证失败"
        return sub_noises

    def verify_complementarity(self, sub_noises: list[np.ndarray]) -> tuple[bool, float]:
        """验证 ∑N_k = 0，返回 (通过与否, 最大残差)。"""
        total = np.zeros_like(sub_noises[0])
        for n in sub_noises:
            total += n
        max_residual = float(np.max(np.abs(total)))
        return max_residual < 1e-4, max_residual

    # ------------------------------------------------------------------
    # 模板库管理
    # ------------------------------------------------------------------

    def save_template(self, name: str, noise: np.ndarray) -> None:
        """保存预计算噪声模板到磁盘（npz，避免 pickle 的不安全反序列化）。"""
        if self.template_dir is None:
            return
        self.template_dir.mkdir(parents=True, exist_ok=True)
        path = self.template_dir / f"{name}.npz"
        np.savez_compressed(path, noise=noise.astype(np.float32))
        self._templates[name] = noise

    def load_templates(self) -> None:
        """从磁盘加载所有噪声模板（npz）。"""
        if self.template_dir is None or not self.template_dir.exists():
            return
        for path in self.template_dir.glob("*.npz"):
            with np.load(path) as data:
                self._templates[path.stem] = data["noise"]
