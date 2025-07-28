import ast
import re
from app.input.file_metadata import FileMetadata
from app.analysis.tree_sitter_util import parse_code

def segment_code(file_metadata: FileMetadata):
    """
    Recursively segment code into logical blocks using tree-sitter parsers.
    Supports Python, JavaScript, Java, and C++ with tree-sitter, falls back to regex for other languages.
    """
    code = file_metadata.content
    language = file_metadata.language.lower()
    segments = []

    # Try tree-sitter first for supported languages
    if language in ["python", "javascript", "java", "cpp", "c++"]:
        try:
            # Map language names to tree-sitter language names
            ts_language = "cpp" if language == "c++" else language
            tree = parse_code(code, ts_language)
            segments = extract_segments_from_tree(tree, code, language)
            if segments:
                return segments
        except Exception as e:
            print(f"Tree-sitter parsing failed for {file_metadata.path}: {e}")
            # Fall back to language-specific methods

    # Fallback to language-specific parsing
    if language == "python":
        segments = segment_python_ast(code)
    elif language == "javascript":
        segments = segment_javascript_regex(code)
    else:
        print(f"Segmentation for {language} not implemented. Returning whole file as one segment.")
        segments.append({
            "node_type": "File",
            "name": file_metadata.path.name,
            "code": code,
            "start_byte": 0,
            "end_byte": len(code)
        })
    
    return segments

def extract_segments_from_tree(tree, code, language):
    """Extract segments from tree-sitter parse tree"""
    segments = []
    
    def walk_node(node):
        # Define node types to extract based on language
        target_types = {
            "python": ["function_definition", "class_definition"],
            "javascript": ["function_declaration", "function_expression", "class_declaration", "method_definition"],
            "java": ["method_declaration", "class_declaration", "constructor_declaration"],
            "cpp": ["function_definition", "class_specifier"],
            "c++": ["function_definition", "class_specifier"]
        }
        
        node_types = target_types.get(language, [])
        
        if node.type in node_types:
            # Extract function/class name
            name = "<anonymous>"
            if language == "python":
                name_node = node.child_by_field_name("name")
                if name_node:
                    name = name_node.text.decode('utf-8')
            elif language == "javascript":
                name_node = node.child_by_field_name("name")
                if name_node:
                    name = name_node.text.decode('utf-8')
            elif language == "java":
                name_node = node.child_by_field_name("name")
                if name_node:
                    name = name_node.text.decode('utf-8')
            elif language in ["cpp", "c++"]:
                # For C++, class names are in type_identifier child, function names in identifier child
                if node.type == "class_specifier":
                    for child in node.children:
                        if child.type == "type_identifier":
                            name = child.text.decode('utf-8')
                            break
                elif node.type == "function_definition":
                    for child in node.children:
                        if child.type == "function_declarator":
                            for grandchild in child.children:
                                if grandchild.type == "identifier":
                                    name = grandchild.text.decode('utf-8')
                                    break
                            break
            
            # Get code snippet
            start_byte = node.start_byte
            end_byte = node.end_byte
            snippet = code[start_byte:end_byte]
            
            segments.append({
                "node_type": node.type,
                "name": name,
                "code": snippet,
                "start_byte": start_byte,
                "end_byte": end_byte,
                "start_line": node.start_point[0],
                "end_line": node.end_point[0]
            })
        
        # Recursively walk children
        for child in node.children:
            walk_node(child)
    
    walk_node(tree.root_node)
    return segments

def segment_python_ast(code):
    """Segment Python code using AST (fallback method)"""
    segments = []
    try:
        tree = ast.parse(code)
    except Exception as e:
        print(f"Failed to parse Python code: {e}")
        return []
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            start_line = node.lineno - 1
            end_line = node.end_lineno - 1 if hasattr(node, "end_lineno") and node.end_lineno is not None else node.lineno
            snippet = "\n".join(code.splitlines()[start_line:end_line+1]).strip()
            segments.append({
                "node_type": type(node).__name__,
                "name": getattr(node, "name", "<anonymous>"),
                "code": snippet,
                "start_line": start_line,
                "end_line": end_line
            })
    return segments

def segment_javascript_regex(code):
    """Segment JavaScript code using regex (fallback method)"""
    segments = []
    func_pattern = re.compile(r"function\s+(\w+)\s*\(|(\w+)\s*=\s*\(.*\)\s*=>|class\s+(\w+)")
    for match in func_pattern.finditer(code):
        name = match.group(1) or match.group(2) or match.group(3) or "<anonymous>"
        start = match.start()
        end = code.find("}", start) + 1 if code.find("}", start) != -1 else len(code)
        snippet = code[start:end].strip()
        segments.append({
            "node_type": "FunctionOrClass",
            "name": name,
            "code": snippet,
            "start_byte": start,
            "end_byte": end
        })
    return segments
