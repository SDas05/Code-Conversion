import re
import ast
from app.input.file_metadata import FileMetadata
from app.analysis.tree_sitter_util import parse_code

def extract_context(file_metadata: FileMetadata, segment_start: int):
    """
    Extract context code from the same file that occurs before the segment_start byte or line.
    Uses tree-sitter for supported languages (Python, JavaScript, Java, C++), falls back to language-specific methods.
    """
    code = file_metadata.content
    language = file_metadata.language.lower()
    context_lines = []
    code_lines = code.splitlines()

    # Try tree-sitter first for supported languages
    if language in ["python", "javascript", "java", "cpp", "c++"]:
        try:
            # Map language names to tree-sitter language names
            ts_language = "cpp" if language == "c++" else language
            tree = parse_code(code, ts_language)
            context_code = extract_context_from_tree(tree, code, segment_start, language)
            if context_code:
                return {
                    "context_code": context_code,
                    "source_lines": [0, len(context_code.splitlines())]
                }
        except Exception as e:
            print(f"Tree-sitter context extraction failed for {file_metadata.path}: {e}")
            # Fall back to language-specific methods

    # Fallback to language-specific parsing
    if language == "python":
        context_code = extract_python_context_ast(code, segment_start)
    elif language == "javascript":
        context_code = extract_javascript_context_regex(code, segment_start)
    else:
        # Fallback: all lines before segment_start
        context_lines = code_lines[:segment_start]
        context_code = "\n".join(context_lines).strip()

    return {
        "context_code": context_code,
        "source_lines": [0, len(context_code.splitlines())]
    }

def extract_context_from_tree(tree, code, segment_start, language):
    """Extract context from tree-sitter parse tree"""
    context_nodes = []
    
    def walk_node(node):
        # Define node types to extract as context based on language
        context_types = {
            "python": ["import_statement", "import_from_statement", "function_definition", "class_definition"],
            "javascript": ["import_statement", "function_declaration", "class_declaration"],
            "java": ["import_declaration", "class_declaration", "method_declaration"],
            "cpp": ["preproc_include", "class_specifier", "function_definition"]
        }
        
        node_types = context_types.get(language, [])
        
        if node.type in node_types and node.end_byte < segment_start:
            # Get code snippet
            start_byte = node.start_byte
            end_byte = node.end_byte
            snippet = code[start_byte:end_byte]
            context_nodes.append(snippet)
        
        # Recursively walk children
        for child in node.children:
            walk_node(child)
    
    walk_node(tree.root_node)
    return "\n".join(context_nodes).strip()

def extract_python_context_ast(code, segment_start):
    """Extract Python context using AST (fallback method)"""
    context_lines = []
    code_lines = code.splitlines()
    
    try:
        tree = ast.parse(code)
    except Exception as e:
        print(f"Failed to parse Python code: {e}")
        return ""
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef, ast.Assign)):
            if hasattr(node, "end_lineno") and node.end_lineno is not None and node.end_lineno < segment_start:
                lines = code_lines[node.lineno-1: node.end_lineno]
                context_lines.extend(lines)
    
    return "\n".join(context_lines).strip()

def extract_javascript_context_regex(code, segment_start):
    """Extract JavaScript context using regex (fallback method)"""
    context_lines = []
    
    # Simple regex for imports and function/class declarations before segment_start
    import_pattern = re.compile(r"^import .+", re.MULTILINE)
    func_pattern = re.compile(r"function\s+\w+|class\s+\w+", re.MULTILINE)
    
    for match in import_pattern.finditer(code):
        if match.start() < segment_start:
            context_lines.append(match.group())
    
    for match in func_pattern.finditer(code):
        if match.start() < segment_start:
            context_lines.append(match.group())
    
    return "\n".join(context_lines).strip()
