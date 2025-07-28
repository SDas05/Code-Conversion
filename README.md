# Code-Conversion

A sophisticated AI-powered code conversion tool that transforms source code between different programming languages while preserving functionality, structure, and best practices.

## 🚀 Features

### **Multi-Language Support**

- **Source Languages**: Python, JavaScript, Java, C++, C#, TypeScript, SQL, R
- **Target Languages**: All supported source languages
- **Advanced Parsing**: Tree-sitter based syntax analysis for accurate code segmentation

### **Intelligent Code Analysis**

- **Segmentation Engine**: Breaks down code into logical units (functions, classes, methods)
- **Context Extraction**: Identifies relevant imports, dependencies, and surrounding code
- **Dependency Analysis**: Maps relationships between code components

### **AI-Powered Conversion**

- **GPT-4 Integration**: Uses OpenAI's GPT-4 for high-quality code conversion
- **Prompt Engineering**: Sophisticated prompt building for optimal conversion results
- **Context Preservation**: Maintains code structure and comments during conversion

### **Validation & Quality Assurance**

- **Syntax Validation**: Ensures converted code is syntactically correct
- **Semantic Analysis**: Validates functional equivalence
- **Performance Analysis**: Monitors conversion quality and performance

## 🏗️ Architecture

```
Code-Conversion/
├── app/
│   ├── analysis/           # Code analysis and segmentation
│   │   ├── segmentation_engine.py
│   │   ├── context_extractor.py
│   │   ├── dependency_analyzer.py
│   │   └── tree_sitter_util.py
│   ├── conversion/         # AI-powered code conversion
│   │   ├── code_generator.py
│   │   ├── model_client.py
│   │   └── prompt_builder.py
│   ├── input/             # File processing and classification
│   │   ├── file_classifier.py
│   │   ├── file_metadata.py
│   │   ├── preprocessing.py
│   │   └── repo_scanner.py
│   ├── orchestration/     # Pipeline coordination
│   │   ├── pipeline_controller.py
│   │   └── error_handler.py
│   ├── validation/        # Code validation and testing
│   │   ├── base_validator.py
│   │   ├── llm_validator.py
│   │   └── performance_analyzer.py
│   └── output/           # Final output processing
│       └── final_repo.py
├── tests/                # Test suite
├── vendor/              # Tree-sitter language grammars
└── config.json         # Configuration settings
```

## 📋 Prerequisites

- **Python 3.8+**
- **Git**
- **OpenAI API Key** (for GPT-4 access)
- **Tree-sitter language packages** (automatically installed)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Code-Conversion.git
cd Code-Conversion
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Tree-sitter Language Packages

```bash
pip install tree-sitter-python tree-sitter-javascript tree-sitter-java tree-sitter-cpp tree-sitter-typescript tree-sitter-sql
```

### 5. Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

## 🚀 Usage

### Basic Usage

1. **Run the Pipeline**:

```bash
python app/main.py
```

2. **Follow the Prompts**:
   - Enter the path to your source code repository
   - Specify the target programming language

### Advanced Usage

#### Command Line Interface

```bash
# Convert Python to JavaScript
python app/main.py --source python --target javascript --input ./my_project

# Convert with custom configuration
python app/main.py --config custom_config.json
```

#### Programmatic Usage

```python
from app.orchestration.pipeline_controller import run_pipeline

# Run the complete conversion pipeline
run_pipeline()
```

## ⚙️ Configuration

The `config.json` file allows you to customize:

### Model Settings

```json
{
  "model": {
    "provider": "openai",
    "model_name": "gpt-4",
    "temperature": 0.2,
    "max_tokens": 3000
  }
}
```

### Conversion Settings

```json
{
  "conversion": {
    "preserve_comments": true,
    "preserve_formatting": true,
    "handle_errors": true,
    "use_best_practices": true
  }
}
```

### Chunking Strategy

```json
{
  "chunking": {
    "chunk_strategy": "function_level",
    "max_chunk_tokens": 8000,
    "overlap_tokens": 200
  }
}
```

## 🧪 Testing

Run the test suite to ensure everything works correctly:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_analysis_layer.py

# Run with verbose output
pytest -v
```

## 📊 Supported Languages

| Language   | Parsing         | Segmentation         | Context Extraction   |
| ---------- | --------------- | -------------------- | -------------------- |
| Python     | ✅ Tree-sitter  | ✅ Functions/Classes | ✅ Imports/Context   |
| JavaScript | ✅ Tree-sitter  | ✅ Functions/Classes | ✅ Imports/Context   |
| Java       | ✅ Tree-sitter  | ✅ Methods/Classes   | ✅ Imports/Context   |
| C++        | ✅ Tree-sitter  | ✅ Functions/Classes | ✅ Includes/Context  |
| C#         | ✅ Tree-sitter  | ✅ Methods/Classes   | ✅ Using/Context     |
| TypeScript | ✅ Tree-sitter  | ✅ Functions/Classes | ✅ Imports/Context   |
| SQL        | ✅ Tree-sitter  | ✅ Statements        | ✅ Schema/Context    |
| R          | 🔄 AST Fallback | ✅ Functions         | ✅ Libraries/Context |

## 🔧 Development

### Project Structure

- **`app/analysis/`**: Code analysis and segmentation logic
- **`app/conversion/`**: AI model integration and code generation
- **`app/input/`**: File processing and repository scanning
- **`app/orchestration/`**: Pipeline coordination and error handling
- **`app/validation/`**: Code validation and quality assurance
- **`app/output/`**: Final output processing and repository generation

### Adding New Languages

1. **Install Tree-sitter Grammar**:

```bash
pip install tree-sitter-[language]
```

2. **Update `tree_sitter_util.py`**:

```python
try:
    import tree_sitter_[language]
    [LANGUAGE]_LANGUAGE = Language(tree_sitter_[language].language())
except ImportError:
    [LANGUAGE]_LANGUAGE = None
```

3. **Update Segmentation Engine**:
   Add language-specific node types to `extract_segments_from_tree()`.

4. **Update Context Extractor**:
   Add language-specific context types to `extract_context_from_tree()`.

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation for API changes
- Ensure all tests pass before submitting PR

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Tree-sitter**: For robust parsing capabilities
- **OpenAI**: For GPT-4 language model
- **FastAPI**: For web framework (if web interface is added)
- **Pytest**: For testing framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/Code-Conversion/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/Code-Conversion/discussions)
- **Email**: your.email@example.com

## 🔄 Roadmap

- [ ] Web interface for easier usage
- [ ] Support for more programming languages
- [ ] Batch processing for large repositories
- [ ] Integration with CI/CD pipelines
- [ ] Advanced code optimization features
- [ ] Real-time collaboration features

---

**Made with ❤️ by [Your Name]**
