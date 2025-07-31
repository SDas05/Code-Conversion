import sys
import os
from pathlib import Path

# Add the parent directory to Python path so we can import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.orchestration.pipeline_controller import run_pipeline

if __name__ == "__main__":
    run_pipeline()
