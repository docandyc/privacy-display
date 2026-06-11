"""
隐私显示配置持久化。

对应交底书 5.1 步骤2：持久化 n/epsilon/反色 alpha/key/refresh 等运行参数。
"""

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class PrivacyDisplayConfig:
    width: int = 1280
    height: int = 720
    n: int = 2
    epsilon: float = 8 / 255
    gamma_factor: float = 1.1
    inversion_alpha: float = 0.3
    insert_inversion: bool = False
    key_hex: str = ""
    refresh_rate: int = 120
    show_hud: bool = True

    def __post_init__(self) -> None:
        if not self.key_hex:
            self.key_hex = os.urandom(32).hex()
        self.validate()

    def validate(self) -> None:
        if not (2 <= int(self.n) <= 16):
            raise ValueError("n must be in [2, 16]")
        if not (0.0 <= float(self.epsilon) <= 1.0):
            raise ValueError("epsilon must be in [0, 1]")
        if float(self.gamma_factor) <= 0:
            raise ValueError("gamma_factor must be positive")
        if not (0.2 <= float(self.inversion_alpha) <= 0.5):
            raise ValueError("inversion_alpha must be in [0.2, 0.5]")
        if int(self.refresh_rate) <= 0:
            raise ValueError("refresh_rate must be positive")
        raw = bytes.fromhex(self.key_hex)
        if len(raw) != 32:
            raise ValueError("key_hex must encode 32 bytes")

    @property
    def key(self) -> bytes:
        return bytes.fromhex(self.key_hex)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict) -> "PrivacyDisplayConfig":
        payload = dict(payload)
        # Backward compatibility: older configs used "alpha" for gamma_factor.
        # In the disclosure, alpha is the inversion duration coefficient.
        if "alpha" in payload:
            legacy_alpha = payload.pop("alpha")
            if "inversion_alpha" not in payload and 0.2 <= float(legacy_alpha) <= 0.5:
                payload["inversion_alpha"] = legacy_alpha
            elif "gamma_factor" not in payload:
                payload["gamma_factor"] = legacy_alpha
        allowed = set(cls.__dataclass_fields__)
        filtered = {k: v for k, v in payload.items() if k in allowed}
        return cls(**filtered)

    @classmethod
    def load(cls, path: str | Path) -> "PrivacyDisplayConfig":
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    def save(self, path: str | Path) -> None:
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    def to_window_kwargs(self) -> dict:
        return {
            "width": self.width,
            "height": self.height,
            "n": self.n,
            "refresh_rate": self.refresh_rate,
            "epsilon": self.epsilon,
            "gamma_factor": self.gamma_factor,
            "inversion_alpha": self.inversion_alpha,
            "insert_inversion": self.insert_inversion,
            "show_hud": self.show_hud,
        }
