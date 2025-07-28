from app.input.repo_scanner import RepositoryScanner
from app.input.file_classifier import FileType
from app.analysis.segmentation_engine import segment_code
from app.conversion.prompt_builder import build_prompt
from app.conversion.model_client import ModelClient
from app.conversion.code_generator import save_converted_code
# Add import for validation and output
import shutil
from pathlib import Path
from app.validation.validation_controller import ValidationController

def get_user_input():
    repo_path = input("Enter the path to the source code repo: ").strip()
    target_lang = input("Enter the language you want to convert to: ").strip()
    return repo_path, target_lang

def convert_file(file_metadata, target_lang):
    # Segment file into functions/classes
    segments = segment_code(file_metadata)

    if not segments:
        print(f"Skipping {file_metadata.path} (no segments found)")
        return

    model = ModelClient()

    for segment in segments:
        if "start_byte" in segment and "end_byte" in segment:
            code_chunk = file_metadata.content[segment["start_byte"]:segment["end_byte"]]
        elif "start_line" in segment and "end_line" in segment:
            code_lines = file_metadata.content.splitlines()
            code_chunk = "\n".join(code_lines[segment["start_line"]:segment["end_line"]+1])
        else:
            code_chunk = segment.get("code", "")
        
        prompt = build_prompt(
            code=code_chunk,
            source_lang=file_metadata.language,
            target_lang=target_lang,
            context={}  # Pass empty dict instead of None
        )

        converted = model.get_completion(prompt)

        if converted:
            save_converted_code(
                original_metadata=file_metadata,
                converted_code=converted,
                target_language=target_lang
            )
        else:
            print(f"Model failed to return output for: {file_metadata.path}")

def validate_and_output_file(converted_file_path, original_file_path):
    """
    Validate the converted file using ValidationController. If valid, move to output layer.
    """
    vc = ValidationController()
    report = vc.run_all(original_file_path, converted_file_path)
    print("Validation Matrix:")
    for row in report["matrix"]:
        print(f"  {row['validator']}: {'PASS' if row['passed'] else 'FAIL'} - {row['details']}")
    if report["overall_passed"]:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        shutil.copy(converted_file_path, output_dir / converted_file_path.name)
        print(f"Validated and moved to output: {output_dir / converted_file_path.name}")
    else:
        print(f"Validation failed for: {converted_file_path}")

def run_pipeline():
    repo_path, target_lang = get_user_input()
    
    print(f"\n Scanning repository at {repo_path}...\n")
    files_with_chunks = RepositoryScanner(repo_path).scan_with_chunks()

    classifier = FileType()

    for file_path, chunks in files_with_chunks:
        content = "\n".join(chunks)
        metadata = classifier.classify_file(file_path, content)
        metadata.content = content  # manually attach content for later use

        convert_file(metadata, target_lang)

        # After conversion, find the converted file in validation layer
        # This assumes save_converted_code saves to app/validation/<lang>/<filename>
        target_lang_folder = target_lang.lower().replace("#", "sharp")
        filename = Path(file_path).with_suffix("")
        validation_dir = Path("app/validation") / target_lang_folder

        # Find the actual converted file (extension may change)
        for f in validation_dir.glob(f"{filename.name}.*"):
            validate_and_output_file(f, Path(file_path))

if __name__ == "__main__":
    run_pipeline()
