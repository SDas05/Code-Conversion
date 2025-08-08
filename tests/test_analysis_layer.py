from multiprocessing import context
import unittest
import sys
import os
from pathlib import Path
from typing import Dict, List, Any

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.analysis.segmentation_engine import segment_code
from app.analysis.context_extractor import extract_context
from app.input.file_metadata import FileMetadata
from app.input.repo_scanner import RepositoryScanner
from app.input.file_classifier import FileClassifier

def print_segment_details(segment: Dict[str, Any], index: int, file_path: str):
    """Print detailed information about a segment"""
    print(f"\n  Segment {index + 1}:")
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
        if len(lines) <= 10:
            print(f"    Code:")
            for i, line in enumerate(lines):
                print(f"      {segment.get('start_line', 0) + i + 1:4d}: {line}")
        else:
            print(f"    Code (showing first 5 and last 5 lines):")
            for i, line in enumerate(lines[:5]):
                print(f"      {segment.get('start_line', 0) + i + 1:4d}: {line}")
            print(f"      ... ({len(lines) - 10} lines omitted) ...")
            for i, line in enumerate(lines[-5:]):
                actual_line = segment.get('start_line', 0) + len(lines) - 5 + i + 1
                print(f"      {actual_line:4d}: {line}")
    
    print(f"    File: {file_path}")

class TestSegmentationEngine(unittest.TestCase):
    def test_python_segmentation(self):
        code = """
def foo(x):
    return x + 1

class Bar:
    def method(self):
        pass
"""
        meta = FileMetadata(
            path=Path("foo.py"), language="Python", size=len(code), loc=7,
            complexity_score=0.07, difficulty="low", priority=3, content=code
        )
        segments = segment_code(meta)
        
        print(f"\nPython Segmentation Test Results:")
        print(f"File: {meta.path}")
        print(f"Language: {meta.language}")
        print(f"Total segments found: {len(segments)}")
        
        for i, segment in enumerate(segments):
            print_segment_details(segment, i, str(meta.path))
        
        # Tree-sitter finds 3 segments: function, class, and method
        self.assertEqual(len(segments), 3)
        self.assertEqual(segments[0]["node_type"], "function_definition")
        self.assertEqual(segments[1]["node_type"], "class_definition")
        self.assertEqual(segments[2]["node_type"], "function_definition")

    def test_javascript_segmentation(self):
        code = """
function foo(x) {
    return x + 1;
}

class Bar {
    method() {
        return this.x;
    }
}
"""
        meta = FileMetadata(
            path=Path("foo.js"), language="JavaScript", size=len(code), loc=10,
            complexity_score=0.1, difficulty="low", priority=3, content=code
        )
        segments = segment_code(meta)
        
        print(f"\nJavaScript Segmentation Test Results:")
        print(f"File: {meta.path}")
        print(f"Language: {meta.language}")
        print(f"Total segments found: {len(segments)}")
        
        for i, segment in enumerate(segments):
            print_segment_details(segment, i, str(meta.path))
        
        # Tree-sitter finds 3 segments: function, class, and method
        self.assertEqual(len(segments), 3)
        self.assertEqual(segments[0]["node_type"], "function_declaration")
        self.assertEqual(segments[1]["node_type"], "class_declaration")
        self.assertEqual(segments[2]["node_type"], "method_definition")

    def test_java_segmentation(self):
        code = """
public class Test {
    public void method1() {
        System.out.println("Hello");
    }
    
    public static void main(String[] args) {
        method1();
    }
}
"""
        meta = FileMetadata(
            path=Path("Test.java"), language="Java", size=len(code), loc=10,
            complexity_score=0.1, difficulty="low", priority=3, content=code
        )
        segments = segment_code(meta)
        
        print(f"\nJava Segmentation Test Results:")
        print(f"File: {meta.path}")
        print(f"Language: {meta.language}")
        print(f"Total segments found: {len(segments)}")
        
        for i, segment in enumerate(segments):
            print_segment_details(segment, i, str(meta.path))
        
        self.assertGreater(len(segments), 0)
        self.assertEqual(segments[0]["node_type"], "class_declaration")

    def test_cpp_segmentation(self):
        code = """
#include <iostream>

class Test {
public:
    void method1() {
        std::cout << "Hello" << std::endl;
    }
};

int main() {
    Test t;
    t.method1();
    return 0;
}
"""
        meta = FileMetadata(
            path=Path("test.cpp"), language="C++", size=len(code), loc=15,
            complexity_score=0.15, difficulty="medium", priority=3, content=code
        )
        segments = segment_code(meta)
        
        print(f"\nC++ Segmentation Test Results:")
        print(f"File: {meta.path}")
        print(f"Language: {meta.language}")
        print(f"Total segments found: {len(segments)}")
        
        for i, segment in enumerate(segments):
            print_segment_details(segment, i, str(meta.path))
        
        self.assertGreater(len(segments), 0)

class TestContextExtractor(unittest.TestCase):
    def test_python_context(self):
        code = """
import os
import sys

def helper():
    pass

def main():
    helper()
"""
        meta = FileMetadata(
            path=Path("main.py"), language="Python", size=len(code), loc=8,
            complexity_score=0.08, difficulty="low", priority=3, content=code
        )
        # Test context extraction for the main function
        segments = segment_code(meta)
        if segments:
            main_segment = segments[-1]  # Get the main function
            result = extract_context(meta, main_segment["start_byte"])
            self.assertIn("import os", result["context_code"])
            self.assertIn("import sys", result["context_code"])
            self.assertIn("def helper", result["context_code"])

    def test_javascript_context(self):
        code = """
import x from 'y';

function helper() {
    return true;
}

function main() {
    helper();
}
"""
        meta = FileMetadata(
            path=Path("main.js"), language="JavaScript", size=len(code), loc=10,
            complexity_score=0.1, difficulty="low", priority=3, content=code
        )
        segments = segment_code(meta)
        if segments:
            main_segment = segments[-1]  # Get the main function
            result = extract_context(meta, main_segment["start_byte"])
            self.assertIn("import x from 'y'", result["context_code"])
            # Expected behavior with the current implementation

    def test_unknown_language_context(self):
        code = "some random code"
        meta = FileMetadata(
            path=Path("unknown.txt"), language="Unknown", size=len(code), loc=1,
            complexity_score=0.01, difficulty="low", priority=1, content=code
        )
        result = extract_context(meta, 0)
        self.assertEqual(result["context_code"], "")

def analyze_repository_segmentation(repo_path: str) -> Dict[str, Any]:
    """
    Analyze segmentation for all files in a repository.
    
    Args:
        repo_path: Path to the repository to analyze
        
    Returns:
        Dictionary containing analysis results
    """
    print(f"\n Analyzing repository: {repo_path}")
    print("=" * 60)
    
    # Scan repository
    scanner = RepositoryScanner(repo_path)
    files_with_chunks = scanner.scan_with_chunks()
    
    classifier = FileClassifier()
    results = {
        "total_files": 0,
        "supported_languages": 0,
        "segments_found": 0,
        "language_stats": {},
        "file_details": []
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
            segments = segment_code(metadata)
            
            if segments:
                results["supported_languages"] += 1
                results["segments_found"] += len(segments)
                results["language_stats"][metadata.language]["total_segments"] += len(segments)
                
                print(f"   Segments found: {len(segments)}")
                
                # Show detailed segment information
                for i, segment in enumerate(segments):
                    print_segment_details(segment, i, str(file_path))
                
                # Test context extraction for first segment
                if segments:
                    first_segment = segments[0]
                    context_result = extract_context(metadata, first_segment["start_byte"])
                    context_lines = len(context_result["context_code"].splitlines())
                    print(f"   Context lines for first segment: {context_lines}")
                    
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
                print(f"   No segments found")
                
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
    print("ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Total files processed: {results['total_files']}")
    print(f"Files with supported languages: {results['supported_languages']}")
    print(f"Total segments found: {results['segments_found']}")
    
    print("\nLanguage Statistics:")
    for lang, stats in results["language_stats"].items():
        if stats["count"] > 0:
            avg_segments = stats["total_segments"] / stats["count"]
            print(f"  {lang}: {stats['count']} files, {stats['total_segments']} segments (avg: {avg_segments:.1f})")
    
    return results

def test_single_file_segmentation(file_path: str):
    """
    Test single file segmentation

    Args:
        file_path: path to file
    """

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        #file classification
        classifier = FileClassifier()
        metadata = classifier.classify_file(Path(file_path), content)
        metadata.content = content 
        
        print(f"\n{'='*60}")
        print(f"Analzing file: {file_path}")
        print(f"Language: {metadata.language}")
        print(f"Size: {metadata.size} bytes")
        print(f"Lines of Code: {metadata.loc}")

        #Segmentation test
        print("Segmentation results")
        print(f"\n{'='*60}")

        segments = segment_code(metadata)

        if segments:
            print(f"Total segments found: {len(segments)}")

            for i, segment in enumerate(segments):
                print_segment_details(segment, i, file_path)

            if "start_byte" in segment:
                context_result = extract_context(metadata, segment["start_byte"])
                context_lines = len(context_result["context_code"].splitlines())

                context_code = context_result["context_code"]
                if context_code:
                    context_lines_list = context_code.splitlines()
                    print(f"   Context content (first 3 lines):")
                    for line in context_lines_list[:3]:
                        print(f"  {line}")
                    print(f" .. ({len(context_lines_list) - 3} more lines)")
        else:
            print("No segments found")
    except Exception as e:
        print(f"Error analyzing file: {e}")



def interactive_analysis():
    """
    Interactive function to analyze a repository's segmentation.
    """
    print("Analysis Layer Testing Tool")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Analyze a repository")
        print("2. Test a single file")
        print("3. Run unit tests")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            repo_path = input("\nEnter the path to the repository: ").strip()
            
            if not os.path.exists(repo_path):
                print(f"Error: Path '{repo_path}' does not exist")
                continue
            
            try:
                results = analyze_repository_segmentation(repo_path)
                
                # Ask if user wants to save results
                save_choice = input("\nSave results to file? (y/n): ").strip().lower()
                if save_choice == 'y':
                    import json
                    output_file = f"analysis_results_{Path(repo_path).name}.json"
                    with open(output_file, 'w') as f:
                        json.dump(results, f, indent=2)
                    print(f"Results saved to: {output_file}")
                    
            except Exception as e:
                print(f"Error during analysis: {e}")
        
        elif choice == "2":
            file_path = input("\nEnter the path to the file to analyze: ").strip()
            test_single_file_segmentation(file_path)
        
        elif choice == "3":
            print("\nRunning unit tests...")
            # Run the unit tests
            unittest.main(argv=[''], exit=False, verbosity=2)
        
        elif choice == "4":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    # Check if command line arguments are provided
    if len(sys.argv) > 1:
        # Command line mode
        repo_path = sys.argv[1]
        if os.path.exists(repo_path):
            results = analyze_repository_segmentation(repo_path)
        else:
            print(f"Error: Repository path '{repo_path}' does not exist")
    else:
        # Interactive mode
        interactive_analysis()
