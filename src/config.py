from dataclasses import dataclass

@dataclass(frozen=True)
class AppConfig:
    top_n: int = 10
    normalize_factors: bool = True
    output_dir: str = "output"

CONFIG = AppConfig()
