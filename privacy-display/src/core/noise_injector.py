"""
对抗性噪声注入器

基于可微影子模型的 FGSM/PGD 生成针对 OCR/检测模型的对抗噪声，并
将其分解为时域互补的 n 个子噪声（∑N_k = 0），确保人眼积分后噪声
完全消除。
"""

import json
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
    TargetModelSpec("yolo26", "detector", "pgd", "magnitude", 7.0, (1.0, 0.85, 1.15)),
    TargetModelSpec("rtdetr", "detector", "pgd", "magnitude", 6.5, (1.0, 0.9, 1.1)),
    TargetModelSpec("faster_rcnn", "detector", "pgd", "coarse", 5.0, (1.15, 1.0, 0.85)),
    TargetModelSpec("retinanet", "detector", "pgd", "coarse", 5.5, (1.1, 1.0, 0.9)),
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
        self._template_metadata: dict[str, dict] = {}
        self._last_gradient_source = "none"
        self._easyocr_gradient_reader = None
        self._easyocr_gradient_model = None
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
        self.load_templates()

    # ------------------------------------------------------------------
    # 噪声生成
    # ------------------------------------------------------------------

    def generate_fgsm_noise(
        self,
        image: np.ndarray,
        model_name: str = "tesseract",
        use_template: bool = True,
    ) -> np.ndarray:
        """
        生成 FGSM 对抗噪声。

        Tesseract/EasyOCR/PaddleOCR 等 OCR 引擎本身通常不可微；本实现
        使用本地可微影子模型计算真实输入梯度，并保留模板库优先路径。
        若 PyTorch 不可用，才回退到传统图像代理梯度。

        Args:
            image: float32 (H, W, 3)，值域 [0, 1]
            model_name: 目标 OCR 模型名称

        Returns:
            float32 (H, W, 3) 基础噪声，值域 [-ε, +ε]
        """
        if use_template:
            template = self._get_template(model_name, image.shape[:2])
            if template is not None:
                self._last_gradient_source = "template"
                return template

        spec = self._get_spec(model_name)
        eps = self._effective_epsilon(spec.name)
        grad = self._target_gradient(image, spec)
        signed = np.where(np.abs(grad) < 1e-6, 0.0, np.sign(grad))
        return (eps * signed).clip(-eps, eps).astype(np.float32)

    def generate_pgd_noise(
        self,
        image: np.ndarray,
        model_name: str = "easyocr",
        iterations: int | None = None,
        step_size: float | None = None,
        random_start: bool = True,
        seed: int | None = None,
        use_template: bool = True,
    ) -> np.ndarray:
        """
        生成 PGD 对抗噪声，满足 L∞ 扰动预算。

        PGD 在 FGSM 的基础上迭代更新：每步沿目标模型代理梯度前进，
        并投影回 [-ε, ε] 约束盒。该接口用于交底书 3.2.2 的 PGD
        噪声模板生成与在线更新。
        """
        if use_template:
            template = self._get_template(model_name, image.shape[:2])
            if template is not None:
                self._last_gradient_source = "template"
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
            grad = self._target_gradient(adv, spec)
            signed = np.where(np.abs(grad) < 1e-6, 0.0, np.sign(grad))
            perturb = perturb + alpha * signed
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

    def build_template(
        self,
        image: np.ndarray,
        model_name: str = "tesseract",
        method: str | None = None,
        name: str | None = None,
        save: bool = True,
    ) -> tuple[np.ndarray, dict]:
        """
        生成并可选保存针对目标模型的对抗噪声模板。

        模板不会从现有模板读取，确保离线训练/更新时基于当前影子模型重新
        计算梯度。返回值包含模板噪声和可审计元数据。
        """
        spec = self._get_spec(model_name)
        selected_method = method or self._online_state[spec.name]["preferred_method"]
        if selected_method == "pgd":
            noise = self.generate_pgd_noise(
                image,
                model_name=spec.name,
                seed=0,
                use_template=False,
            )
        else:
            noise = self.generate_fgsm_noise(
                image,
                model_name=spec.name,
                use_template=False,
            )
        metadata = {
            "model_name": spec.name,
            "method": selected_method,
            "epsilon": float(self._effective_epsilon(spec.name)),
            "gradient_source": self._last_gradient_source,
            "shape_hw": list(image.shape[:2]),
        }
        if save:
            self.save_template(name or spec.name, noise, metadata)
        return noise, metadata

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

    def monitor_online_recognition(
        self,
        image: np.ndarray,
        ground_truth: str = "",
        model_name: str = "tesseract",
        engine: str | None = None,
        ocr_evaluator=None,
        threshold: float | None = None,
    ) -> dict:
        """
        运行 OCR 监测并把识别成功率反馈给在线策略。

        这对应交底书中的轻量化影子监测闭环：识别率升高时自动切换到
        PGD、提高 ε scale 并扰动频域相位。
        """
        if ocr_evaluator is None:
            from src.attack.ocr_evaluator import OCREvaluator
            ocr_evaluator = OCREvaluator()

        ocr_engines = {"tesseract", "easyocr", "paddleocr"}
        selected_engine = engine or (
            model_name if model_name in ocr_engines else "tesseract"
        )
        if ground_truth:
            result = ocr_evaluator.evaluate_single(image, ground_truth, selected_engine)
            score = float(result.char_accuracy)
            text = getattr(result, "text", "")
        else:
            text = ocr_evaluator.recognize(image, selected_engine)
            score = 1.0 if text.strip() else 0.0

        trigger_threshold = self.online_threshold if threshold is None else threshold
        state = self.update_online_strategy(
            model_name,
            recognition_score=score,
            threshold=threshold,
        )
        state.update({
            "engine": selected_engine,
            "recognized_text": text,
            "triggered": score > trigger_threshold,
        })
        return state

    def get_online_state(self, model_name: str) -> dict:
        """返回指定模型的在线更新状态快照。"""
        return dict(self._online_state[self._get_spec(model_name).name])

    @property
    def last_gradient_source(self) -> str:
        """最近一次噪声生成使用的梯度来源：template/shadow/surrogate。"""
        return self._last_gradient_source

    def _get_spec(self, model_name: str) -> TargetModelSpec:
        fallback = self._target_specs.get("tesseract")
        if fallback is None:
            fallback = next(iter(self._target_specs.values()))
        return self._target_specs.get(model_name, fallback)

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

    def get_template_metadata(self, name: str) -> dict:
        """返回模板元数据快照；旧模板无元数据时返回空 dict。"""
        return dict(self._template_metadata.get(name, {}))

    def _target_gradient(self, image: np.ndarray, spec: TargetModelSpec) -> np.ndarray:
        if spec.name == "easyocr":
            easyocr_grad = self._easyocr_e2e_gradient(image)
            if easyocr_grad is not None:
                self._last_gradient_source = "easyocr_e2e"
                return easyocr_grad
        shadow = self._differentiable_shadow_gradient(image, spec)
        if shadow is not None:
            self._last_gradient_source = "shadow"
            return shadow
        self._last_gradient_source = "surrogate"
        return self._surrogate_gradient(image, spec)

    def _easyocr_e2e_gradient(self, image: np.ndarray) -> np.ndarray | None:
        """
        尝试对 EasyOCR 识别网络本体反传输入梯度。

        EasyOCR 的内部 recognizer API 不是公开稳定接口，因此该路径必须
        fail-soft：成功时标记 `easyocr_e2e`，任何导入/权重/形状问题都回退
        到本地可微影子模型。
        """
        try:
            import torch
            import torch.nn.functional as F
        except ImportError:
            return None

        try:
            if self._easyocr_gradient_model is None:
                if self._easyocr_gradient_reader is None:
                    import easyocr
                    self._easyocr_gradient_reader = easyocr.Reader(
                        ["en"],
                        gpu=False,
                        download_enabled=False,
                        verbose=False,
                    )
                self._easyocr_gradient_model = getattr(
                    self._easyocr_gradient_reader,
                    "recognizer",
                    None,
                )
            model = self._easyocr_gradient_model
            if model is None:
                return None

            image_f = np.clip(image.astype(np.float32), 0.0, 1.0)
            x = torch.from_numpy(image_f.transpose(2, 0, 1)).unsqueeze(0).float()
            gray = (x[:, 0:1] * 0.299 + x[:, 1:2] * 0.587 + x[:, 2:3] * 0.114)
            gray = F.interpolate(gray, size=(32, 128), mode="bilinear", align_corners=False)
            gray.requires_grad_(True)

            model.eval()
            try:
                output = model(gray, None)
            except TypeError:
                output = model(gray)
            if isinstance(output, (list, tuple)):
                output = output[0]
            if not hasattr(output, "float"):
                return None

            # Untargeted differentiable OCR loss: make the recognizer logits
            # unstable without requiring labels or converter internals.
            logits = output.float()
            loss = logits.square().mean()
            loss.backward()
            grad_gray = gray.grad
            if grad_gray is None:
                return None
            grad_rgb = grad_gray.repeat(1, 3, 1, 1)
            grad_rgb = F.interpolate(
                grad_rgb,
                size=image_f.shape[:2],
                mode="bilinear",
                align_corners=False,
            )
            grad = grad_rgb.detach().squeeze(0).cpu().numpy().transpose(1, 2, 0)
            return grad.astype(np.float32)
        except Exception:
            return None

    def _differentiable_shadow_gradient(
        self,
        image: np.ndarray,
        spec: TargetModelSpec,
    ) -> np.ndarray | None:
        """
        使用本地可微影子模型对输入求真实梯度。

        OCR 影子模型优化目标是降低笔画与局部背景的对比度；检测影子模型
        优化目标是提升边缘/纹理不稳定性。两者都通过 torch autograd 反传
        得到 ∇_I L(f_shadow(I), y_proxy)。
        """
        try:
            import torch
            import torch.nn.functional as F
        except ImportError:
            return None

        image_f = np.clip(image.astype(np.float32), 0.0, 1.0)
        x = torch.from_numpy(image_f.transpose(2, 0, 1)).unsqueeze(0)
        x = x.float()
        x.requires_grad_(True)

        rgb_weights = torch.tensor(
            [0.299, 0.587, 0.114],
            dtype=x.dtype,
            device=x.device,
        ).view(1, 3, 1, 1)
        gray = (x * rgb_weights).sum(dim=1, keepdim=True)

        # OCR strokes can be wider than a 3x3/5x5 edge neighborhood. A larger
        # differentiable background window gives non-zero gradients across the
        # stroke body, not only at the contour.
        blur_size = 15
        blur_kernel = torch.ones(
            (1, 1, blur_size, blur_size),
            dtype=x.dtype,
            device=x.device,
        ) / float(blur_size * blur_size)
        local_mean = F.conv2d(gray, blur_kernel, padding=blur_size // 2)

        if spec.family == "ocr":
            # Maximize negative contrast energy: gradient moves strokes toward
            # their local background, which is the OCR-relevant shadow target.
            loss = -F.mse_loss(gray, local_mean.detach())
        else:
            sobel_x = torch.tensor(
                [[[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]],
                dtype=x.dtype,
                device=x.device,
            ).unsqueeze(0)
            sobel_y = torch.tensor(
                [[[-1, -2, -1], [0, 0, 0], [1, 2, 1]]],
                dtype=x.dtype,
                device=x.device,
            ).unsqueeze(0)
            gx = F.conv2d(gray, sobel_x, padding=1)
            gy = F.conv2d(gray, sobel_y, padding=1)
            loss = (gx.square() + gy.square()).mean()

        loss.backward()
        grad = x.grad.detach().squeeze(0).cpu().numpy().transpose(1, 2, 0)
        weights = np.array(spec.color_weights, dtype=np.float32).reshape(1, 1, 3)
        return (grad * weights).astype(np.float32)

    def _surrogate_gradient(self, image: np.ndarray, spec: TargetModelSpec) -> np.ndarray:
        """
        torch 不可用时的模型特定 OCR/检测代理梯度。

        OCR 目标强调文字笔画边缘和高频纹理；检测目标强调连通区域边界和
        coarse objectness。正常路径应优先使用 `_differentiable_shadow_gradient`。
        """
        import cv2

        image_f = np.clip(image.astype(np.float32), 0.0, 1.0)
        img_uint8 = (image_f * 255).astype(np.uint8)
        gray = cv2.cvtColor(img_uint8, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0

        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        lap = cv2.Laplacian(gray, cv2.CV_32F, ksize=3)
        mag = np.sqrt(gx ** 2 + gy ** 2)

        if spec.family == "ocr":
            base = self._ocr_contrast_attack_gradient(gray, spec)
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

    def _ocr_contrast_attack_gradient(
        self,
        gray: np.ndarray,
        spec: TargetModelSpec,
    ) -> np.ndarray:
        """
        OCR-directed proxy gradient.

        OCR engines are most sensitive to stroke/background contrast. This
        gradient approximates the sign of a loss that reduces local text
        contrast: dark strokes are pushed lighter and nearby bright background
        is pushed darker. The output is still bounded by FGSM/PGD callers.
        """
        import cv2

        sigma = float(np.clip(16.0 / max(spec.texture_frequency, 1.0), 0.75, 2.5))
        local_mean = cv2.GaussianBlur(gray, (0, 0), sigma)
        contrast_grad = local_mean - gray

        if spec.edge_axis == "x":
            directional = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        elif spec.edge_axis == "y":
            directional = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        elif spec.edge_axis == "laplace":
            directional = cv2.Laplacian(gray, cv2.CV_32F, ksize=3)
        else:
            gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
            gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
            directional = np.sqrt(gx ** 2 + gy ** 2)

        if np.max(np.abs(directional)) > 1e-8:
            directional = directional / (np.max(np.abs(directional)) + 1e-8)
        return (0.85 * contrast_grad + 0.15 * directional).astype(np.float32)

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
        if self.n < 2:
            raise ValueError(f"子帧数量 n 须不小于 2，实际为 {self.n}")

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
        if np.max(np.abs(total)) >= 1e-5:
            raise RuntimeError("子噪声互补性验证失败")
        return sub_noises

    def split_complementary_spatial(
        self,
        noise_base: np.ndarray,
        tile: int = 1,
    ) -> list[np.ndarray]:
        """
        空间-时间联合互补扰动。

        在 `split_complementary` 的逐像素 ΣN_k=0 之外，引入棋盘格空间极性：
        同一子帧内相邻像素极性相反，弱化多相机/离轴叠加时的局部一致噪声。
        对缓慢变化的文字/背景区域，2×2 邻域噪声和接近 0。
        """
        if tile <= 0:
            raise ValueError("tile must be positive")
        h, w = noise_base.shape[:2]
        yy, xx = np.mgrid[0:h, 0:w]
        checker = (((yy // tile) + (xx // tile)) % 2) * 2 - 1
        checker = checker.astype(np.float32)[:, :, None]
        spatial_base = noise_base.astype(np.float32) * checker
        sub_noises = self.split_complementary(spatial_base)
        ok, residual = self.verify_complementarity(sub_noises)
        if not ok:
            raise RuntimeError(f"空间互补性验证失败: {residual:.2e}")
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

    def save_template(
        self,
        name: str,
        noise: np.ndarray,
        metadata: dict | None = None,
    ) -> None:
        """保存预计算噪声模板到磁盘（npz，避免 pickle 的不安全反序列化）。"""
        if self.template_dir is None:
            return
        self.template_dir.mkdir(parents=True, exist_ok=True)
        path = self.template_dir / f"{name}.npz"
        metadata = metadata or {}
        np.savez_compressed(
            path,
            noise=noise.astype(np.float32),
            metadata=np.array(json.dumps(metadata, ensure_ascii=False)),
        )
        self._templates[name] = noise
        self._template_metadata[name] = dict(metadata)

    def load_templates(self) -> None:
        """从磁盘加载所有噪声模板（npz）。"""
        if self.template_dir is None or not self.template_dir.exists():
            return
        for path in self.template_dir.glob("*.npz"):
            with np.load(path) as data:
                self._templates[path.stem] = data["noise"]
                if "metadata" in data:
                    try:
                        raw = str(data["metadata"].item())
                        self._template_metadata[path.stem] = json.loads(raw)
                    except Exception:
                        self._template_metadata[path.stem] = {}
                else:
                    self._template_metadata[path.stem] = {}
