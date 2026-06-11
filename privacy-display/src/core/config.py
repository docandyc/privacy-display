"""
隐私显示配置持久化。

对应交底书 5.1 步骤2：持久化 n/epsilon/alpha/key/refresh 等运行参数。
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
    alpha: float = 1.1
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
        if float(self.alpha) <= 0:
            raise ValueError("alpha must be positive")
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
            "gamma_factor": self.alpha,
            "show_hud": self.show_hud,
        }
