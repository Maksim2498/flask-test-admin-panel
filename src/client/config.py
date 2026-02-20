from dataclasses import dataclass

__all__ = ["Config"]


@dataclass
class Config:
  address: str = "http://localhost:8000/api"
