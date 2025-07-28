import os
from pathlib import Path
from typing import List, Tuple

# Configurable constants
SUPPORTED_EXTENSIONS = {".py", ".r", ".ipynb", ".sql", ".js", ".java", ".cpp", ".c", ".cs", ".rb", ".go", ".rs", ".ts"}
EXCLUDED_DIRS = {"node_modules", "venv", "__pycache__", ".git"}
EXCLUDED_FILES = {"config.json", "secrets.json"}
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MAX_FILES = 100
MAX_TOTAL_SIZE_MB = 50
MAX_TOTAL_SIZE_BYTES = MAX_TOTAL_SIZE_MB * 1024 * 1024
MAX_LINES_PER_FILE = 1000
ENCODING = "utf-8"
CHUNK_SIZE = 500

# Internal helper functions
def is_valid_file(file_path: Path) -> bool:
    if file_path.suffix not in SUPPORTED_EXTENSIONS:
        return False
    if file_path.name in EXCLUDED_FILES:
        return False
    if file_path.stat().st_size > MAX_FILE_SIZE_BYTES:
        return False
    return True

def chunk_file_content(content: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    lines = content.splitlines()
    return ["\n".join(lines[i:i + chunk_size]) for i in range(0, len(lines), chunk_size)]

class RepositoryScanner:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.valid_files: List[Tuple[Path, str]] = []
        self.total_size = 0

        if not self.repo_path.is_dir():
            raise ValueError(f"Provided path is not a directory: {repo_path}")

    def scan(self) -> List[Tuple[Path, str]]:
        """
        Scans the repository and stores a list of valid (Path, content) tuples.
        Applies filtering rules and size/line limits.
        """
        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

            for file_name in files:
                file_path = Path(root) / file_name

                if not is_valid_file(file_path):
                    continue

                try:
                    file_size = file_path.stat().st_size
                    if self.total_size + file_size > MAX_TOTAL_SIZE_BYTES:
                        print(f"Skipping {file_path}: total size limit exceeded.")
                        continue

                    with open(file_path, "r", encoding=ENCODING, errors="ignore") as f:
                        lines = f.readlines()

                    if len(lines) > MAX_LINES_PER_FILE:
                        lines = lines[:MAX_LINES_PER_FILE]
                        print(f"Truncated {file_path} to {MAX_LINES_PER_FILE} lines.")

                    content = "".join(lines)
                    self.valid_files.append((file_path, content))
                    self.total_size += file_size

                    if len(self.valid_files) >= MAX_FILES:
                        print("Reached maximum number of files to process.")
                        return self.valid_files

                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

        return self.valid_files

    def scan_with_chunks(self) -> List[Tuple[Path, List[str]]]:
        """
        Scans and returns content as chunks of lines per file.
        """
        if not self.valid_files:
            self.scan()

        return [(path, chunk_file_content(content)) for path, content in self.valid_files]

    def print_summary(self):
        """
        Prints a simple summary of scanned files.
        """
        if not self.valid_files:
            self.scan()

        print(f"Repository: {self.repo_path}")
        print(f"Total valid files: {len(self.valid_files)}")
        print(f"Total size of valid files: {self.total_size / (1024 * 1024):.2f} MB")
