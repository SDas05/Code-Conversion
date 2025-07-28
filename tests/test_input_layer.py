import argparse
import subprocess
import tempfile
import shutil
from pathlib import Path
from urllib.parse import urlparse

from app.input.repo_scanner import RepositoryScanner
from app.input.file_classifier import FileType
from app.input.preprocessing import PreprocessingQueue


def clone_github_repo(git_url: str) -> str:
    """
    Clone a GitHub repository into a temporary directory and return the path.
    """
    temp_dir = tempfile.mkdtemp()
    print(f" Cloning {git_url} into {temp_dir}...")
    try:
        subprocess.run(["git", "clone", git_url, temp_dir], check=True, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to clone repo: {e}")
        shutil.rmtree(temp_dir)
        raise e
    return temp_dir


def run_input_layer(repo_path: str):
    print("\n Running Input Layer...")

    # Initialize components
    scanner = RepositoryScanner(repo_path)
    classifier = FileType()
    queue = PreprocessingQueue()

    # Step 1: Scan files
    files = scanner.scan()
    print(f"\n Scanned {len(files)} files.")

    # Step 2: Classify and enqueue
    for path, content in files:
        metadata = classifier.classify_file(path, content)
        queue.enqueue(metadata)

    # Step 3: Print summary
    print(f"\n Preprocessing Queue Summary ({len(queue.peek_all())} files):\n")
    for meta in queue.peek_all():
        print(f"{meta.path} | Language: {meta.language} | LOC: {meta.loc} | "
              f"Complexity: {meta.complexity_score} | Priority: {meta.priority} | Difficulty: {meta.difficulty}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Input Layer on a local repo or GitHub URL.")
    parser.add_argument("repo_path", type=str, help="Local path or GitHub repo URL")
    args = parser.parse_args()

    repo_path = args.repo_path
    temp_dir = None

    if repo_path.startswith("https://github.com"):
        repo_path = clone_github_repo(repo_path)
        temp_dir = repo_path  # Save to clean up later

    try:
        run_input_layer(repo_path)
    finally:
        if temp_dir:
            print(f"\n Cleaning up temporary clone at {temp_dir}")
            shutil.rmtree(temp_dir)
