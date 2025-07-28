from dataclasses import dataclass
from pathlib import Path

@dataclass
class FileMetadata:
    path: Path
    language: str
    size: int
    loc: int
    complexity_score: float
    difficulty: str
    priority: int
    content: str = ""