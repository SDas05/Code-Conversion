import ast
import re
from typing import Dict, List, Set, Tuple
from app.input.file_metadata import FileMetadata
from app.analysis.tree_sitter_util import parse_code

def analyze_dependencies(file_metadata: FileMetadata) -> Dict:
    """
    Analyze dependencies in the code file.
    Returns information about imports, function calls, class relationships, etc.
    """
    code = file_metadata.content
    language = file_metadata.language.lower()
    
    # Try tree-sitter first for supported languages
    if language in ["python", "javascript", "java", "cpp", "c++"]:
        try:
            ts_language = "cpp" if language == "c++" else language
            tree = parse_code(code, ts_language)
            return extract_dependencies_from_tree(tree, code, language)
        except Exception as e:
            print(f"Tree-sitter dependency analysis failed for {file_metadata.path}: {e}")
            # Fall back to language-specific methods
    
    # Fallback to language-specific parsing
    if language == "python":
        return analyze_python_dependencies_ast(code)
    elif language == "javascript":
        return analyze_javascript_dependencies_regex(code)
    else:
        return analyze_generic_dependencies(code, language)

def extract_dependencies_from_tree(tree, code, language):
    """Extract dependencies from tree-sitter parse tree"""
    dependencies = {
        "imports": [],
        "function_calls": [],
        "class_uses": [],
        "variables": [],
        "modules": set()
    }
    
    def walk_node(node):
        # Define node types to extract based on language
        import_types = {
            "python": ["import_statement", "import_from_statement"],
            "javascript": ["import_statement"],
            "java": ["import_declaration"],
            "cpp": ["preproc_include"]
        }
        
        call_types = {
            "python": ["call"],
            "javascript": ["call_expression"],
            "java": ["method_invocation"],
            "cpp": ["call_expression"]
        }
        
        import_node_types = import_types.get(language, [])
        call_node_types = call_types.get(language, [])
        
        if node.type in import_node_types:
            # Extract import information
            import_text = code[node.start_byte:node.end_byte]
            dependencies["imports"].append({
                "text": import_text,
                "start_byte": node.start_byte,
                "end_byte": node.end_byte
            })
            
            # Extract module names
            if language == "python":
                if "from" in import_text:
                    match = re.search(r"from\s+(\w+)", import_text)
                    if match:
                        dependencies["modules"].add(match.group(1))
                else:
                    match = re.search(r"import\s+(\w+)", import_text)
                    if match:
                        dependencies["modules"].add(match.group(1))
        
        elif node.type in call_node_types:
            # Extract function call information
            call_text = code[node.start_byte:node.end_byte]
            dependencies["function_calls"].append({
                "text": call_text,
                "start_byte": node.start_byte,
                "end_byte": node.end_byte
            })
        
        # Recursively walk children
        for child in node.children:
            walk_node(child)
    
    walk_node(tree.root_node)
    
    # Convert set to list for JSON serialization
    dependencies["modules"] = list(dependencies["modules"])
    
    return dependencies

def analyze_python_dependencies_ast(code):
    """Analyze Python dependencies using AST"""
    dependencies = {
        "imports": [],
        "function_calls": [],
        "class_uses": [],
        "variables": [],
        "modules": set()
    }
    
    try:
        tree = ast.parse(code)
    except Exception as e:
        print(f"Failed to parse Python code: {e}")
        return dependencies
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            import_info = {
                "type": "import" if isinstance(node, ast.Import) else "import_from",
                "names": [alias.name for alias in node.names],
                "lineno": node.lineno
            }
            dependencies["imports"].append(import_info)
            
            # Add module names
            if isinstance(node, ast.ImportFrom) and node.module:
                dependencies["modules"].add(node.module)
            for alias in node.names:
                dependencies["modules"].add(alias.name)
        
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                dependencies["function_calls"].append({
                    "name": node.func.id,
                    "lineno": node.lineno
                })
            elif isinstance(node.func, ast.Attribute):
                dependencies["function_calls"].append({
                    "name": f"{ast.unparse(node.func)}",
                    "lineno": node.lineno
                })
        
        elif isinstance(node, ast.Name):
            dependencies["variables"].append({
                "name": node.id,
                "lineno": node.lineno
            })
    
    dependencies["modules"] = list(dependencies["modules"])
    return dependencies

def analyze_javascript_dependencies_regex(code):
    """Analyze JavaScript dependencies using regex"""
    dependencies = {
        "imports": [],
        "function_calls": [],
        "class_uses": [],
        "variables": [],
        "modules": set()
    }
    
    # Import patterns
    import_pattern = re.compile(r"import\s+(.+?)\s+from\s+['\"](.+?)['\"]", re.MULTILINE)
    require_pattern = re.compile(r"require\s*\(\s*['\"](.+?)['\"]", re.MULTILINE)
    
    for match in import_pattern.finditer(code):
        dependencies["imports"].append({
            "type": "import",
            "text": match.group(0),
            "module": match.group(2)
        })
        dependencies["modules"].add(match.group(2))
    
    for match in require_pattern.finditer(code):
        dependencies["imports"].append({
            "type": "require",
            "text": match.group(0),
            "module": match.group(1)
        })
        dependencies["modules"].add(match.group(1))
    
    # Function call patterns
    func_call_pattern = re.compile(r"(\w+)\s*\(", re.MULTILINE)
    for match in func_call_pattern.finditer(code):
        dependencies["function_calls"].append({
            "name": match.group(1),
            "text": match.group(0)
        })
    
    dependencies["modules"] = list(dependencies["modules"])
    return dependencies

def analyze_generic_dependencies(code, language):
    """Generic dependency analysis for unsupported languages"""
    dependencies = {
        "imports": [],
        "function_calls": [],
        "class_uses": [],
        "variables": [],
        "modules": [],
        "language": language
    }
    
    # Basic regex patterns for common constructs
    import_patterns = {
        "java": r"import\s+([\w.]+);",
        "cpp": r"#include\s*[<\"](.+?)[>\"]",
        "c#": r"using\s+([\w.]+);"
    }
    
    pattern = import_patterns.get(language)
    if pattern:
        for match in re.finditer(pattern, code, re.MULTILINE):
            dependencies["imports"].append({
                "text": match.group(0),
                "module": match.group(1)
            })
            dependencies["modules"].append(match.group(1))
    
    return dependencies

def get_dependency_graph(dependencies: Dict) -> Dict:
    """Create a dependency graph from analyzed dependencies"""
    graph = {
        "nodes": [],
        "edges": []
    }
    
    # Add modules as nodes
    for module in dependencies.get("modules", []):
        graph["nodes"].append({
            "id": module,
            "type": "module",
            "label": module
        })
    
    # Add function calls as nodes
    for call in dependencies.get("function_calls", []):
        func_name = call.get("name", "unknown")
        graph["nodes"].append({
            "id": func_name,
            "type": "function",
            "label": func_name
        })
    
    # Add edges from imports to modules
    for import_info in dependencies.get("imports", []):
        if "module" in import_info:
            graph["edges"].append({
                "from": "current_file",
                "to": import_info["module"],
                "type": "imports"
            })
    
    return graph
