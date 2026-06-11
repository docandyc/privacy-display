"""
对抗性噪声注入器

基于 FGSM 生成针对 OCR 模型的对抗噪声，并将其分解为
时域互补的 n 个子噪声（∑N_k = 0），确保人眼积分后噪声完全消除。
"""

import numpy as np
import os
from pathlib import Path


class NoiseInjector:
    def __init__(
        self,
        n: int,
        epsilon: float = 8 / 255,
        template_dir: str | None = None,
    ):
        """
        Args:
            n: 子帧数量
            epsilon: 噪声预算 ‖N_base‖_∞ ≤ ε，典型值 8/255
            template_dir: 预计算噪声模板目录
        """
        self.n = n
        self.epsilon = epsilon
        self.template_dir = Path(template_dir) if template_dir else None
        self._templates: dict[str, np.ndarray] = {}

    # ------------------------------------------------------------------
    # 噪声生成
    # ------------------------------------------------------------------

    def generate_fgsm_noise(
        self,
        image: np.ndarray,
        model_name: str = "tesseract",
    ) -> np.ndarray:
        """
        生成 FGSM 对抗噪声（基于预计算梯度方向）。

        对于无法直接反向传播的 OCR（如 Tesseract），采用近似策略：
        沿图像梯度方向施加有界扰动，破坏文字边缘高频信息。

        Args:
            image: float32 (H, W, 3)，值域 [0, 1]
            model_name: 目标 OCR 模型名称

        Returns:
            float32 (H, W, 3) 基础噪声，值域 [-ε, +ε]
        """
        if model_name in self._templates:
            template = self._templates[model_name]
            # 将模板缩放到当前图像尺寸
            if template.shape[:2] != image.shape[:2]:
                import cv2
                template = cv2.resize(template, (image.shape[1], image.shape[0]))
            return template

        # 近似策略：沿 Sobel 梯度方向施加扰动，破坏文字边缘
        return self._gradient_based_noise(image)

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
