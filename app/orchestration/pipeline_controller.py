from app.input.repo_scanner import RepositoryScanner
from app.input.file_classifier import FileClassifier
from app.analysis.segmentation_engine import segment_code
from app.analysis.context_extractor import extract_context
from app.conversion.prompt_builder import build_prompt
from app.conversion.model_client import ModelClient
from app.conversion.code_generator import save_converted_code
from app.validation.validation_controller import ValidationController
import shutil
from pathlib import Path

import os

def get_user_input():
    """Get repository path and target language from user input."""
    repo_path = input("Enter the path to the source code repo: ").strip()
    target_lang = input("Enter the language you want to convert to: ").strip()
    return repo_path, target_lang

def convert_file(file_metadata, target_lang):
    """Convert a single file using the analysis and conversion pipeline."""
    print(f"\nConverting {file_metadata.path} ({file_metadata.language} → {target_lang})")
    
    # Segment file into functions/classes
    segments = segment_code(file_metadata)

    if not segments:
        print(f"Skipping {file_metadata.path} (no segments found)")
        return

    print(f"Found {len(segments)} segments to convert")

    model = ModelClient()

    for i, segment in enumerate(segments):
        print(f" Converting segment {i+1}/{len(segments)}: {segment.get('name', '<anonymous>')}")
        
        # Extract code chunk
        if "start_byte" in segment and "end_byte" in segment:
            code_chunk = file_metadata.content[segment["start_byte"]:segment["end_byte"]]
        elif "start_line" in segment and "end_line" in segment:
            code_lines = file_metadata.content.splitlines()
            code_chunk = "\n".join(code_lines[segment["start_line"]:segment["end_line"]+1])
        else:
            code_chunk = segment.get("code", "")
        
        # Extract context for this segment
        context = {}
        try:
            if "start_byte" in segment:
                context_result = extract_context(file_metadata, segment["start_byte"])
                context = {
                    "context_code": context_result.get("context_code", ""),
                    "source_lines": context_result.get("source_lines", [0, 0])
                }
        except Exception as e:
            print(f" Context extraction failed: {e}")
        
        # Build prompt with context
        prompt = build_prompt(
            code=code_chunk,
            source_lang=file_metadata.language,
            target_lang=target_lang,
            context=context
        )

        # Get conversion from model
        converted = model.get_completion(prompt)

        if converted:
            print(f" Conversion successful")
            save_converted_code(
                original_metadata=file_metadata,
                converted_code=converted,
                target_language=target_lang
            )
        else:
            print(f" Model failed to return output for segment {i+1}")

def validate_and_output_file(converted_file_path, original_file_path):
    """Validate the converted file and move to output if valid."""
    print(f"\nValidating: {converted_file_path.name}")
    
    try:
        # Use lenient validation for cross-language conversions
        vc = ValidationController(strict_mode=False)
        report = vc.run_all(original_file_path, converted_file_path)
        
        print("Validation Matrix:")
        for row in report["matrix"]:
            status = "PASS" if row['passed'] else "FAIL"
            print(f"  {row['validator']}: {status} - {row['details']}")
        
        # Show cross-language conversion info
        if report.get("is_cross_language", False):
            print(f" Cross-language conversion detected: {original_file_path.suffix} → {converted_file_path.suffix}")
            print(f" Validation mode: {'Strict' if report.get('strict_mode', False) else 'Lenient'}")
        
        if report["overall_passed"]:
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / converted_file_path.name
            shutil.copy(converted_file_path, output_file)
            print(f"Validated and moved to output: {output_file}")
        else:
            print(f"Validation failed for: {converted_file_path}")
            # For cross-language conversions, still move to output with warning
            if report.get("is_cross_language", False) and not report.get("strict_mode", False):
                output_dir = Path("output")
                output_dir.mkdir(exist_ok=True)
                output_file = output_dir / converted_file_path.name
                shutil.copy(converted_file_path, output_file)
                print(f"Cross-language conversion moved to output with warnings: {output_file}")
            
    except Exception as e:
        print(f"Validation error: {e}")
        # For cross-language conversions, still move to output on validation error
        try:
            source_lang = original_file_path.suffix[1:].lower() if original_file_path.suffix else "unknown"
            target_lang = converted_file_path.suffix[1:].lower() if converted_file_path.suffix else "unknown"
            if source_lang != target_lang:
                output_dir = Path("output")
                output_dir.mkdir(exist_ok=True)
                output_file = output_dir / converted_file_path.name
                shutil.copy(converted_file_path, output_file)
                print(f"Cross-language conversion moved to output despite validation error: {output_file}")
        except Exception as copy_error:
            print(f"Failed to copy file: {copy_error}")

def run_pipeline():
    """Run the complete code conversion pipeline."""
    print("Code Conversion Pipeline")
    print("=" * 50)
    
    try:
        repo_path, target_lang = get_user_input()
        
        if not os.path.exists(repo_path):
            print(f"Error: Repository path '{repo_path}' does not exist")
            return
        
        print(f"\nScanning repository at {repo_path}...")
        files_with_chunks = RepositoryScanner(repo_path).scan_with_chunks()

        if not files_with_chunks:
            print("No files found in repository")
            return

        print(f"Found {len(files_with_chunks)} files to process")
        
        classifier = FileClassifier()
        processed_files = 0
        converted_files = 0

        for file_path, chunks in files_with_chunks:
            processed_files += 1
            print(f"\nProcessing file {processed_files}/{len(files_with_chunks)}: {file_path}")
            
            content = "\n".join(chunks)
            metadata = classifier.classify_file(file_path, content)
            metadata.content = content

            # Skip unsupported languages
            if metadata.language.lower() not in ["python", "javascript", "java", "cpp", "c++", "c#", "typescript", "sql"]:
                print(f"Skipping {file_path} (unsupported language: {metadata.language})")
                continue

            try:
                convert_file(metadata, target_lang)
                converted_files += 1
                
                # Find and validate converted file
                target_lang_folder = target_lang.lower().replace("#", "sharp")
                filename = Path(file_path).with_suffix("")
                validation_dir = Path("app/validation") / target_lang_folder

                # Find the actual converted file (extension may change)
                converted_files_found = list(validation_dir.glob(f"{filename.name}.*"))
                if converted_files_found:
                    validate_and_output_file(converted_files_found[0], Path(file_path))
                else:
                    print(f"No converted file found for {file_path}")
                    
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

        # Summary
        print("\n" + "=" * 50)
        print("PIPELINE SUMMARY")
        print("=" * 50)
        print(f"Files processed: {processed_files}")
        print(f"Files converted: {converted_files}")
        print(f"Success rate: {(converted_files/processed_files*100):.1f}%" if processed_files > 0 else "No files processed")
        
        if converted_files > 0:
            print(f"\n Check the 'output' directory for converted files")
        
    except KeyboardInterrupt:
        print("\nPipeline interrupted by user")
    except Exception as e:
        print(f"\nPipeline error: {e}")

if __name__ == "__main__":
    run_pipeline()
