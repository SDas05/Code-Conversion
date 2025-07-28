import os
from tree_sitter import Language, Parser

# Import individual language packages
try:
    import tree_sitter_python
    PYTHON_LANGUAGE = Language(tree_sitter_python.language())
except ImportError:
    PYTHON_LANGUAGE = None

try:
    import tree_sitter_javascript
    JAVASCRIPT_LANGUAGE = Language(tree_sitter_javascript.language())
except ImportError:
    JAVASCRIPT_LANGUAGE = None

try:
    import tree_sitter_java
    JAVA_LANGUAGE = Language(tree_sitter_java.language())
except ImportError:
    JAVA_LANGUAGE = None

try:
    import tree_sitter_cpp
    CPP_LANGUAGE = Language(tree_sitter_cpp.language())
except ImportError:
    CPP_LANGUAGE = None

# Map language names to their Language objects
LANGUAGES = {
    "python": PYTHON_LANGUAGE,
    "javascript": JAVASCRIPT_LANGUAGE,
    "java": JAVA_LANGUAGE,
    "cpp": CPP_LANGUAGE,
    # Add more languages as needed
}

def get_parser(language: str) -> Parser:
    """
    Get the correct tree-sitter parser for given language
    """
    if language not in LANGUAGES or LANGUAGES[language] is None:
        raise ValueError(f"Unsupported language: {language}")
    parser = Parser(LANGUAGES[language])
    return parser

def parse_code(code: str, language: str):
    """
    Parse source code with tree-sitter and return syntax tree
    """
    parser = get_parser(language)
    tree = parser.parse(bytes(code, "utf-8"))
    return tree