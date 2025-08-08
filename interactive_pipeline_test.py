#!/usr/bin/env python3
"""
Interactive Code Conversion Pipeline Testing
==========================================

This script provides interactive testing for the entire code conversion pipeline:
- Input Layer: Repository scanning, file classification, and preprocessing
- Analysis Layer: Code segmentation, dependency analysis, and context extraction  
- Validation Layer: LLM validation, semantic validation, and performance analysis

You can test individual files or entire repositories interactively.
"""

import sys
import os
import json
import tempfile
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Any
from urllib.parse import urlparse

# Add current directory to Python path
sys.path.insert(0, '.')

# Standard imports
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    VISUALIZATION_AVAILABLE = True
except ImportError:
    print("  Visualization libraries not available. Install with: pip install matplotlib seaborn pandas")
    VISUALIZATION_AVAILABLE = False

# Pipeline imports
from app.input.repo_scanner import RepositoryScanner
from app.input.file_classifier import FileClassifier
from app.input.preprocessing import Preprocessor
from app.analysis.context_extractor import extract_context
from app.analysis.dependency_analyzer import DependencyAnalyzer
from app.analysis.segmentation_engine import SegmentationEngine
from app.validation.validation_controller import ValidationController
from app.validation.llm_validator import LLMValidator
from app.validation.semantic_validator import SemanticValidator
from app.validation.performance_analyzer import PerformanceAnalyzer
from app.config import config

print(" All imports successful!")

def clone_github_repo(git_url: str) -> str:
    """Clone a GitHub repository into a temporary directory and return the path."""
    temp_dir = tempfile.mkdtemp()
    print(f" Cloning {git_url} into {temp_dir}...")
    try:
        subprocess.run(["git", "clone", git_url, temp_dir], check=True, stdout=subprocess.DEVNULL)
        print(f" Successfully cloned repository")
    except subprocess.CalledProcessError as e:
        print(f" Failed to clone repo: {e}")
        shutil.rmtree(temp_dir)
        raise e
    return temp_dir

def print_segment_details(segment: Dict[str, Any], index: int, file_path: str):
    """Print detailed information about a segment"""
    print(f"\n   Segment {index + 1}:")
    print(f"    Name: {segment.get('name', '<anonymous>')}")
    print(f"    Type: {segment.get('node_type', 'unknown')}")
    
    # Show line numbers if available
    if 'start_line' in segment and 'end_line' in segment:
        print(f"    Lines: {segment['start_line'] + 1}-{segment['end_line'] + 1}")
    elif 'start_byte' in segment and 'end_byte' in segment:
        print(f"    Bytes: {segment['start_byte']}-{segment['end_byte']}")
    
    # Show the actual code content (truncated if too long)
    code = segment.get('code', '')
    if code:
        lines = code.splitlines()
        if len(lines) <= 8:
            print(f"    Code:")
            for i, line in enumerate(lines):
                print(f"      {segment.get('start_line', 0) + i + 1:4d}: {line}")
        else:
            print(f"    Code (showing first 4 and last 4 lines):")
            for i, line in enumerate(lines[:4]):
                print(f"      {segment.get('start_line', 0) + i + 1:4d}: {line}")
            print(f"      ... ({len(lines) - 8} lines omitted) ...")
            for i, line in enumerate(lines[-4:]):
                actual_line = segment.get('start_line', 0) + len(lines) - 4 + i + 1
                print(f"      {actual_line:4d}: {line}")
    
    print(f"    File: {file_path}")

def visualize_language_distribution(language_stats: Dict):
    """Create a visualization of language distribution"""
    if not VISUALIZATION_AVAILABLE:
        print(" Visualization not available")
        return
        
    if not language_stats:
        print("No language statistics to visualize")
        return
    
    # Prepare data for visualization
    languages = list(language_stats.keys())
    counts = [stats['count'] for stats in language_stats.values()]
    
    plt.figure(figsize=(10, 6))
    plt.subplot(1, 2, 1)
    plt.pie(counts, labels=languages, autopct='%1.1f%%')
    plt.title('File Distribution by Language')
    
    plt.subplot(1, 2, 2)
    plt.bar(languages, counts)
    plt.title('File Count by Language')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def visualize_segment_analysis(segments_by_language: Dict):
    """Create a visualization of segment analysis"""
    if not VISUALIZATION_AVAILABLE:
        print(" Visualization not available")
        return
        
    if not segments_by_language:
        print("No segment data to visualize")
        return
    
    # Prepare data
    languages = list(segments_by_language.keys())
    segment_counts = [len(segments) for segments in segments_by_language.values()]
    
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.bar(languages, segment_counts)
    plt.title('Segments Found by Language')
    plt.ylabel('Number of Segments')
    plt.xticks(rotation=45)
    
    # Segment types distribution
    all_segments = []
    for segments in segments_by_language.values():
        all_segments.extend(segments)
    
    if all_segments:
        segment_types = {}
        for segment in all_segments:
            seg_type = segment.get('node_type', 'unknown')
            segment_types[seg_type] = segment_types.get(seg_type, 0) + 1
        
        plt.subplot(1, 2, 2)
        plt.pie(segment_types.values(), labels=segment_types.keys(), autopct='%1.1f%%')
        plt.title('Segment Types Distribution')
    
    plt.tight_layout()
    plt.show()

def test_input_layer(repo_path: str) -> Dict[str, Any]:
    """Test the complete input layer pipeline"""
    print(" Running Input Layer...")
    print("=" * 60)
    
    # Initialize components
    scanner = RepositoryScanner(repo_path)
    classifier = FileClassifier()
    queue = Preprocessor()
    
    # Step 1: Scan files
    print(" Step 1: Scanning repository...")
    files = scanner.scan()
    print(f" Scanned {len(files)} files.")
    
    # Step 2: Classify and enqueue
    print("\n  Step 2: Classifying files...")
    language_stats = {}
    total_loc = 0
    
    for path, content in files:
        metadata = classifier.classify_file(path, content)
        queue.enqueue(metadata)
        
        # Track statistics
        if metadata.language not in language_stats:
            language_stats[metadata.language] = {
                'count': 0,
                'total_loc': 0,
                'files': []
            }
        
        language_stats[metadata.language]['count'] += 1
        language_stats[metadata.language]['total_loc'] += metadata.loc
        language_stats[metadata.language]['files'].append(str(path))
        total_loc += metadata.loc
    
    # Step 3: Print summary
    print(f"\n Preprocessing Queue Summary ({len(queue.peek_all())} files):")
    print("=" * 60)
    
    for meta in queue.peek_all():
        print(f" {meta.path} | Language: {meta.language} | LOC: {meta.loc} | "
              f"Complexity: {meta.complexity_score:.2f} | Priority: {meta.priority} | Difficulty: {meta.difficulty}")
    
    # Print language statistics
    print(f"\n Language Statistics:")
    print("=" * 60)
    for lang, stats in language_stats.items():
        print(f"{lang}: {stats['count']} files, {stats['total_loc']} LOC")
    
    print(f"\n Total: {len(files)} files, {total_loc} LOC")
    
    # Visualize results
    if language_stats:
        visualize_language_distribution(language_stats)
    
    return {
        'files': files,
        'queue': queue,
        'language_stats': language_stats,
        'total_files': len(files),
        'total_loc': total_loc
    }

def test_analysis_layer(repo_path: str) -> Dict[str, Any]:
    """Test the complete analysis layer pipeline"""
    print(" Running Analysis Layer...")
    print("=" * 60)
    
    # Initialize components
    scanner = RepositoryScanner(repo_path)
    classifier = FileClassifier()
    segmentation_engine = SegmentationEngine()
    dependency_analyzer = DependencyAnalyzer()
    
    # Scan repository
    files_with_chunks = scanner.scan_with_chunks()
    
    results = {
        "total_files": 0,
        "supported_languages": 0,
        "segments_found": 0,
        "language_stats": {},
        "file_details": [],
        "segments_by_language": {}
    }
    
    for file_path, chunks in files_with_chunks:
        content = "\n".join(chunks)
        metadata = classifier.classify_file(file_path, content)
        metadata.content = content
        
        results["total_files"] += 1
        
        print(f"\n File: {file_path}")
        print(f"   Language: {metadata.language}")
        print(f"   Size: {metadata.size} bytes, Lines: {metadata.loc}")
        
        # Track language statistics
        if metadata.language not in results["language_stats"]:
            results["language_stats"][metadata.language] = {
                "count": 0,
                "total_segments": 0,
                "files": []
            }
        
        results["language_stats"][metadata.language]["count"] += 1
        
        # Test segmentation
        segments = []
        error = None
        try:
            segments = segmentation_engine.segment_code(metadata)
            
            if segments:
                results["supported_languages"] += 1
                results["segments_found"] += len(segments)
                results["language_stats"][metadata.language]["total_segments"] += len(segments)
                
                # Store segments by language for visualization
                if metadata.language not in results["segments_by_language"]:
                    results["segments_by_language"][metadata.language] = []
                results["segments_by_language"][metadata.language].extend(segments)
                
                print(f"    Segments found: {len(segments)}")
                
                # Show detailed segment information
                for i, segment in enumerate(segments):
                    print_segment_details(segment, i, str(file_path))
                
                # Test context extraction for first segment
                if segments:
                    first_segment = segments[0]
                    context_result = extract_context(metadata, first_segment["start_byte"])
                    context_lines = len(context_result["context_code"].splitlines())
                    print(f"    Context lines for first segment: {context_lines}")
                    
                    # Show context content if not too long
                    context_code = context_result["context_code"]
                    if context_code:
                        context_lines_list = context_code.splitlines()
                        if len(context_lines_list) <= 5:
                            print(f"   Context content:")
                            for line in context_lines_list:
                                print(f"     {line}")
                        else:
                            print(f"   Context content (first 3 lines):")
                            for line in context_lines_list[:3]:
                                print(f"     {line}")
                            print(f"     ... ({len(context_lines_list) - 3} more lines)")
                
            else:
                print(f"     No segments found")
                
        except Exception as e:
            error = str(e)
            print(f"    Error during segmentation: {e}")
        
        # Store file details
        file_detail = {
            "path": str(file_path),
            "language": metadata.language,
            "size": metadata.size,
            "loc": metadata.loc,
            "segments_count": len(segments),
            "error": error
        }
        results["file_details"].append(file_detail)
    
    # Print summary
    print("\n" + "=" * 60)
    print(" ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Total files processed: {results['total_files']}")
    print(f"Files with supported languages: {results['supported_languages']}")
    print(f"Total segments found: {results['segments_found']}")
    
    # Visualize results
    if results["segments_by_language"]:
        visualize_segment_analysis(results["segments_by_language"])
    
    return results

def test_validation_layer(original_file: str, converted_file: str) -> Dict[str, Any]:
    """Test the complete validation layer pipeline"""
    print(" Running Validation Layer...")
    print("=" * 60)
    
    # Initialize validation controller
    validator = ValidationController(strict_mode=False)
    
    # Run validation
    print(f" Validating conversion from {original_file} to {converted_file}")
    results = validator.run_all(Path(original_file), Path(converted_file))
    
    # Print results
    print(f"\n Validation Results:")
    print(f"Overall Passed: {' YES' if results['overall_passed'] else ' NO'}")
    print(f"Cross-language conversion: {'Yes' if results['is_cross_language'] else 'No'}")
    print(f"Strict mode: {'Yes' if results['strict_mode'] else 'No'}")
    
    print(f"\n Individual Validator Results:")
    for result in results['results']:
        status = " PASS" if result.get('passed', False) else " FAIL"
        print(f"  {result.get('name', 'Unknown')}: {status}")
        print(f"    Details: {result.get('details', 'No details provided')}")
    
    # Create validation matrix visualization
    if results['matrix'] and VISUALIZATION_AVAILABLE:
        df = pd.DataFrame(results['matrix'])
        
        plt.figure(figsize=(10, 6))
        
        # Create a heatmap of validation results
        pivot_table = df.pivot_table(
            index='validator', 
            columns=None, 
            values='passed', 
            aggfunc='first'
        )
        
        plt.subplot(1, 2, 1)
        sns.heatmap(pivot_table, annot=True, cmap=['red', 'green'], cbar=False)
        plt.title('Validation Results Heatmap')
        
        # Create a bar chart
        plt.subplot(1, 2, 2)
        df['passed'].value_counts().plot(kind='bar', color=['red', 'green'])
        plt.title('Pass/Fail Distribution')
        plt.ylabel('Count')
        
        plt.tight_layout()
        plt.show()
    
    return results

def test_complete_pipeline(repo_path: str) -> Dict[str, Any]:
    """Test the complete pipeline (input + analysis layers)"""
    print(" Running Complete Pipeline Test...")
    print("=" * 80)
    
    # Test Input Layer
    print("\n PHASE 1: Input Layer Testing")
    input_results = test_input_layer(repo_path)
    
    # Test Analysis Layer
    print("\n PHASE 2: Analysis Layer Testing")
    analysis_results = test_analysis_layer(repo_path)
    
    # Combine results
    combined_results = {
        'input_layer': input_results,
        'analysis_layer': analysis_results,
        'summary': {
            'total_files': input_results['total_files'],
            'total_loc': input_results['total_loc'],
            'supported_languages': analysis_results['supported_languages'],
            'total_segments': analysis_results['segments_found'],
            'languages_found': list(input_results['language_stats'].keys())
        }
    }
    
    # Print final summary
    print("\n" + "=" * 80)
    print(" PIPELINE SUMMARY")
    print("=" * 80)
    print(f" Total files processed: {combined_results['summary']['total_files']}")
    print(f" Total lines of code: {combined_results['summary']['total_loc']}")
    print(f" Supported languages: {combined_results['summary']['supported_languages']}")
    print(f" Total segments found: {combined_results['summary']['total_segments']}")
    print(f" Languages found: {', '.join(combined_results['summary']['languages_found'])}")
    
    return combined_results

def interactive_testing():
    """Interactive testing interface"""
    print(" Code Conversion Pipeline - Interactive Testing")
    print("=" * 60)
    
    while True:
        print("\n Testing Options:")
        print("1. Test Input Layer only")
        print("2. Test Analysis Layer only")
        print("3. Test Complete Pipeline (Input + Analysis)")
        print("4. Test Validation Layer (requires original + converted files)")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            path = input("\nEnter repository path or GitHub URL: ").strip()
            if path.startswith("https://github.com"):
                temp_dir = clone_github_repo(path)
                try:
                    test_input_layer(temp_dir)
                finally:
                    print(f"\n🧹 Cleaning up temporary clone at {temp_dir}")
                    shutil.rmtree(temp_dir)
            else:
                test_input_layer(path)
        
        elif choice == "2":
            path = input("\nEnter repository path or GitHub URL: ").strip()
            if path.startswith("https://github.com"):
                temp_dir = clone_github_repo(path)
                try:
                    test_analysis_layer(temp_dir)
                finally:
                    print(f"\n🧹 Cleaning up temporary clone at {temp_dir}")
                    shutil.rmtree(temp_dir)
            else:
                test_analysis_layer(path)
        
        elif choice == "3":
            path = input("\nEnter repository path or GitHub URL: ").strip()
            if path.startswith("https://github.com"):
                temp_dir = clone_github_repo(path)
                try:
                    test_complete_pipeline(temp_dir)
                finally:
                    print(f"\n🧹 Cleaning up temporary clone at {temp_dir}")
                    shutil.rmtree(temp_dir)
            else:
                test_complete_pipeline(path)
        
        elif choice == "4":
            original_file = input("\nEnter path to original file: ").strip()
            converted_file = input("Enter path to converted file: ").strip()
            
            if not os.path.exists(original_file):
                print(f" Original file not found: {original_file}")
                continue
            if not os.path.exists(converted_file):
                print(f" Converted file not found: {converted_file}")
                continue
            
            test_validation_layer(original_file, converted_file)
        
        elif choice == "5":
            print(" Goodbye!")
            break
        
        else:
            print(" Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    # Run the interactive interface
    interactive_testing()
