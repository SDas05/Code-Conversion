import os
from pathlib import Path
from app.input.file_metadata import FileMetadata

class FileClassifier:

    """
    Classifies files based on their extensions and provides metadata.
    """

    LANGUAGE_MAP = {
        ".py": "Python",
        ".r": "R",
        ".ipynb": "Jupyter Notebook",
        ".sql": "SQL",
        ".js": "JavaScript",
        ".java": "Java",
        ".cpp": "C++",
        ".c": "C",
        ".cs": "C#",
        ".ts": "TypeScript",
        ".json": "JSON"
    }

    def classify_file(self, file_path: Path, content: str) -> FileMetadata:
        extension = file_path.suffix.lower()
        language = self.LANGUAGE_MAP.get(extension, "unknown")
        size = file_path.stat().st_size
        loc = len(content.splitlines())

        complexity = loc / 100

        if loc > 800:
            priority = 1
            difficulty = "high"
        elif loc > 300:
            priority = 2
            difficulty = "medium"
        else:
            priority = 3
            difficulty = "low"
        return FileMetadata(
            path=file_path,
            language=language,
            size=size,
            loc=loc,
            complexity_score=complexity,
            priority=priority,
            difficulty=difficulty,
            content=content
        )