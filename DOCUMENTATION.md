# Legal Document Anonymization Tool - Documentation

## Table of Contents
1. [Overview](#overview)
2. [Installation & Setup](#installation--setup)
3. [Architecture](#architecture)
4. [User Guide](#user-guide)
5. [API Reference](#api-reference)
6. [Configuration](#configuration)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)
9. [Development](#development)
10. [Performance & Limitations](#performance--limitations)

---

## Overview

The Legal Document Anonymization Tool is a comprehensive Streamlit application that anonymizes legal documents using Llama 3 8B Instruct (via Ollama) and performs automated reconstruction resistance testing with scoring.

### Key Features
- **Document Processing**: PDF, DOCX, TXT support with intelligent chunking
- **Anonymization Strategies**: Traditional, Strategic, Educational, Custom
- **Reconstruction Testing**: 5-category resistance testing
- **Scoring System**: Weighted composite quality assessment
- **Export Functionality**: JSON exports for documents and reports
- **Local Processing**: No cloud dependencies, all processing local

### System Requirements
- **RAM**: 16GB minimum (for Llama 3 8B)
- **Storage**: 10GB for model + document storage
- **CPU**: 8+ cores recommended
- **Python**: 3.8+
- **Ollama**: Latest version with Llama 3 8B Instruct

---

## Installation & Setup

### Quick Start
```bash
# 1. Clone or download the project
cd smart-redact

# 2. Run setup script (installs dependencies and Ollama)
./setup.sh

# 3. Start the application
streamlit run main.py
```

### Manual Installation
```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install spaCy model
python -m spacy download en_core_web_lg

# 3. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 4. Start Ollama service
ollama serve

# 5. Pull Llama 3 model
ollama pull llama3:8b-instruct

# 6. Start application
streamlit run main.py
```

### Verification
```bash
# Run comprehensive tests
python run_tests.py

# Run basic functionality tests
python test_app.py
```

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit UI (main.py)                   │
├─────────────────────────────────────────────────────────────┤
│  Upload Page  │  Anonymize Page  │  Test Page  │  Results   │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                 Core Processing Layer                        │
├─────────────────┬─────────────────┬─────────────────────────┤
│ Document        │ Ollama Client   │ Testing Engine          │
│ Processor       │                 │                         │
│ (document_      │ (ollama_        │ (testing_engine.py)     │
│ processor.py)   │ client.py)      │                         │
└─────────────────┴─────────────────┴─────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                 Support Layer                               │
├─────────────────┬─────────────────┬─────────────────────────┤
│ Scoring System  │ Error Handler   │ Utilities               │
│ (scoring_       │ (error_         │ (utils.py)              │
│ system.py)      │ handler.py)     │                         │
└─────────────────┴─────────────────┴─────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                 External Dependencies                       │
├─────────────────┬─────────────────┬─────────────────────────┤
│ Ollama API      │ spaCy NLP       │ Document Parsers        │
│ (Llama 3)       │ (en_core_web_lg)│ (PyPDF2, python-docx)   │
└─────────────────┴─────────────────┴─────────────────────────┘
```

### Data Flow
1. **Upload**: Document → `DocumentProcessor` → Chunks + Entities
2. **Anonymize**: Chunks → `OllamaClient` → Anonymized Text
3. **Test**: Original + Anonymized → `ReconstructionTester` → Test Results
4. **Score**: Test Results → `ScoringSystem` → Quality Assessment
5. **Export**: All Data → JSON Files

---

## User Guide

### 1. Upload Page

#### Document Upload
- **Supported Formats**: PDF, DOCX, TXT
- **File Size Limit**: 50MB per document
- **Batch Upload**: Up to 10 files simultaneously
- **Word Count Limit**: 50,000 words per document

#### Document Processing
```python
# Automatic processing includes:
- Text extraction from documents
- Entity recognition (people, organizations, dates)
- Legal pattern detection (case citations, statutes)
- Chunking for 8K token limit processing
- Validation and error checking
```

#### Document Preview
- Content preview (first 1000 characters)
- Entity breakdown by category
- Document statistics (word count, chunks, entities)

### 2. Anonymize Page

#### Strategy Selection
- **Traditional**: Replace all identifiers with `[REDACTED]`
- **Strategic**: Preserve legal strategy while anonymizing
- **Educational**: Transform into educational principles
- **Custom**: User-defined anonymization guidelines

#### Processing Options
- **Anonymization Level**: Light, Standard, Aggressive
- **Target Audience**: Internal, External, Public
- **Practice Area**: Litigation, Corporate, IP, Employment

#### Anonymization Process
```python
# Multi-pass processing:
1. Entity replacement (names, organizations)
2. Contextual anonymization (industry, location)
3. Strategic preservation (legal principles)
4. Quality assurance (consistency checking)
```

#### Results Display
- Before/after comparison
- Processing statistics (time, tokens, chunks)
- Failed chunk reporting
- Success/error notifications

### 3. Test Page

#### Test Configuration
- **Adversarial Testing**: Enable/disable
- **Attacker Levels**: Naive, Professional, Advanced, Expert
- **Corpus Information**: Documents available for cross-reference

#### Test Categories
1. **Direct Identifier Search** (30% weight)
   - Searches for remaining identifiers
   - Exact match detection
   - Entity leakage scoring

2. **Pattern Matching** (25% weight)
   - Unique legal pattern detection
   - Case citation analysis
   - Procedural sequence identification

3. **Contextual Reconstruction** (20% weight)
   - LLM-powered reverse engineering
   - Confidence level analysis
   - Specific detail extraction

4. **Cross-Reference Analysis** (15% weight)
   - Similarity to document corpus
   - Pattern correlation testing
   - Unique fingerprint detection

5. **Linguistic Fingerprinting** (10% weight)
   - Writing style analysis
   - Vocabulary overlap measurement
   - Sentence structure comparison

#### Test Results
- Overall resistance score (0-100)
- Individual test breakdowns
- Risk level assessment (High/Medium/Low)
- Improvement recommendations

### 4. Results Page

#### Comprehensive Scoring
- **Overall Quality Score**: Combined resistance + strategic value
- **Reconstruction Resistance**: Security-focused scoring
- **Strategic Value Preservation**: Utility-focused scoring

#### Quality Levels
- **Excellent (90-100)**: Production ready
- **Good (80-89)**: Minor improvements needed
- **Acceptable (70-79)**: Requires review
- **Poor (60-69)**: Significant issues
- **Failed (<60)**: Do not use

#### Export Options
- **Anonymized Document**: JSON format with metadata
- **Test Report**: Comprehensive testing results
- **Comprehensive Data**: All processing data combined

---

## API Reference

### DocumentProcessor Class

```python
class DocumentProcessor:
    def __init__(self)
    def process_file(self, uploaded_file) -> Dict
    def process_batch(self, uploaded_files: List) -> List[Dict]
    def get_document_summary(self, document_data: Dict) -> Dict
    def save_processed_document(self, document_data: Dict, output_path: str) -> bool
    def cleanup_temp_files(self)
```

#### process_file()
```python
# Input: Streamlit uploaded file object
# Output: Dictionary with processing results
{
    "success": bool,
    "filename": str,
    "text": str,
    "word_count": int,
    "chunks": List[Dict],
    "entities": Dict,
    "legal_patterns": List[Dict],
    "metadata": Dict
}
```

### OllamaClient Class

```python
class OllamaClient:
    def __init__(self, endpoint: str = None)
    def test_connection(self) -> Dict
    def generate_text(self, prompt: str, stream: bool = False) -> Dict
    def anonymize_text(self, text: str, strategy: str = "strategic") -> Dict
    def anonymize_chunks(self, chunks: List[Dict], strategy: str = "strategic") -> Dict
    def test_reconstruction(self, anonymized_text: str) -> Dict
    def get_model_info(self) -> Dict
```

#### anonymize_chunks()
```python
# Input: List of text chunks, strategy, custom guidelines
# Output: Anonymization results
{
    "success": bool,
    "anonymized_text": str,
    "strategy": str,
    "chunks_processed": int,
    "chunks_failed": int,
    "total_processing_time": float,
    "total_tokens": int,
    "failed_chunks": List[Dict],
    "chunk_details": List[Dict]
}
```

### ReconstructionTester Class

```python
class ReconstructionTester:
    def __init__(self, ollama_client: OllamaClient = None)
    def add_to_corpus(self, document_data: Dict)
    def run_all_tests(self, original_text: str, anonymized_text: str) -> Dict
    def test_direct_identifiers(self, original_text: str, anonymized_text: str) -> Dict
    def test_pattern_matching(self, original_text: str, anonymized_text: str) -> Dict
    def test_contextual_reconstruction(self, anonymized_text: str) -> Dict
    def test_cross_reference(self, anonymized_text: str) -> Dict
    def test_linguistic_fingerprinting(self, original_text: str, anonymized_text: str) -> Dict
    def run_adversarial_tests(self, anonymized_text: str) -> Dict
```

#### run_all_tests()
```python
# Input: Original text, anonymized text, strategy
# Output: Complete test results
{
    "success": bool,
    "test_results": Dict,
    "resistance_score": float,
    "risk_assessment": Dict,
    "recommendations": List[str]
}
```

### ScoringSystem Class

```python
class ScoringSystem:
    def __init__(self)
    def calculate_overall_score(self, reconstruction_results: Dict, strategic_value_results: Dict) -> Dict
    def calculate_reconstruction_resistance_score(self, test_results: Dict) -> float
    def calculate_strategic_value_score(self, original_text: str, anonymized_text: str) -> float
    def get_quality_level(self, score: float) -> Dict
    def generate_detailed_report(self, overall_results: Dict, reconstruction_results: Dict, strategic_results: Dict) -> Dict
```

### ErrorHandler Class

```python
class ErrorHandler:
    def __init__(self, log_file: str = "app.log")
    def handle_error(self, error: Exception, context: str = "Unknown") -> Dict
    def validate_file_upload(self, uploaded_file) -> Dict
    def validate_text_input(self, text: str, max_length: int = 100000) -> Dict
    def validate_strategy_config(self, strategy: str, custom_guidelines: str = None) -> Dict
    def validate_ollama_connection(self, ollama_client) -> Dict
```

---

## Configuration

### config.py Settings

#### Ollama Configuration
```python
OLLAMA_CONFIG = {
    "endpoint": "http://localhost:11434",
    "model": "llama3:8b-instruct",
    "temperature": 0.3,
    "max_tokens": 4096,
    "top_p": 0.9,
    "stream": True
}
```

#### Document Processing Limits
```python
DOCUMENT_LIMITS = {
    "max_file_size_mb": 50,
    "max_word_count": 50000,
    "chunk_size_tokens": 4000,
    "chunk_overlap_tokens": 200,
    "max_batch_files": 10
}
```

#### Scoring Weights
```python
SCORING_WEIGHTS = {
    "reconstruction_resistance": {
        "direct_identifier": 0.30,
        "pattern_matching": 0.25,
        "contextual_reconstruction": 0.20,
        "cross_reference": 0.15,
        "linguistic_fingerprint": 0.10
    },
    "strategic_value": {
        "legal_principle_retention": 0.40,
        "educational_value": 0.30,
        "business_intelligence": 0.20,
        "procedural_guidance": 0.10
    },
    "overall": {
        "reconstruction_resistance": 0.60,
        "strategic_value_preservation": 0.40
    }
}
```

#### Anonymization Strategies
```python
ANONYMIZATION_STRATEGIES = {
    "traditional": {
        "name": "Traditional Redaction",
        "description": "Replace all identifiers with [REDACTED]",
        "replacement_token": "[REDACTED]"
    },
    "strategic": {
        "name": "Strategic Anonymization",
        "description": "Preserve legal strategy while anonymizing",
        "replacement_token": "[ANONYMOUS]"
    },
    "educational": {
        "name": "Educational Abstraction",
        "description": "Transform into educational principles",
        "replacement_token": "[EXAMPLE]"
    },
    "custom": {
        "name": "Custom Strategy",
        "description": "User-defined anonymization rules",
        "replacement_token": "[CUSTOM]"
    }
}
```

---

## Testing

### Test Suite Structure

#### Basic Tests (`run_tests.py`)
```bash
python run_tests.py
```
- File structure validation
- Dependency checking
- Basic functionality tests
- Ollama connection testing
- Unit test execution
- Streamlit app validation

#### Unit Tests (`test_app.py`)
```bash
python test_app.py
```
- Document processing tests
- Ollama client tests
- Reconstruction testing tests
- Scoring system tests
- Error handling tests
- Integration tests

#### Test Categories

1. **Unit Tests**
   - Individual component testing
   - Mock-based testing
   - Functionality validation

2. **Integration Tests**
   - End-to-end workflow testing
   - Component interaction testing
   - Data flow validation

3. **System Tests**
   - Ollama connection testing
   - Model availability checking
   - Performance testing

### Writing Custom Tests

```python
import unittest
from document_processor import DocumentProcessor

class TestCustomFeature(unittest.TestCase):
    def setUp(self):
        self.processor = DocumentProcessor()
    
    def test_custom_functionality(self):
        # Test implementation
        result = self.processor.process_file(mock_file)
        self.assertTrue(result['success'])
        self.assertIn('text', result)
```

---

## Troubleshooting

### Common Issues

#### 1. Ollama Connection Failed
```
Error: Cannot connect to Ollama
```
**Solutions:**
- Check if Ollama is running: `ollama serve`
- Verify endpoint in config.py
- Check firewall settings
- Restart Ollama service

#### 2. Llama 3 Model Not Found
```
Error: Llama 3 model not available
```
**Solutions:**
- Pull the model: `ollama pull llama3:8b-instruct`
- Check model name in config.py
- Verify disk space availability
- Check Ollama model list: `ollama list`

#### 3. Memory Issues
```
Error: Out of memory
```
**Solutions:**
- Reduce document size
- Decrease chunk_size_tokens in config.py
- Close other applications
- Increase system RAM

#### 4. File Processing Errors
```
Error: Could not extract text from document
```
**Solutions:**
- Check file format (PDF, DOCX, TXT only)
- Verify file is not corrupted
- Check file permissions
- Try with different document

#### 5. Streamlit Connection Issues
```
Error: Streamlit app won't start
```
**Solutions:**
- Check port availability (default 8501)
- Verify Python dependencies
- Check for conflicting installations
- Try different port: `streamlit run main.py --server.port 8502`

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check application logs:
```bash
tail -f app.log
```

### Performance Optimization

#### For Large Documents
```python
# Reduce chunk size
DOCUMENT_LIMITS["chunk_size_tokens"] = 2000

# Increase overlap for better context
DOCUMENT_LIMITS["chunk_overlap_tokens"] = 400
```

#### For Slow Processing
```python
# Reduce temperature for faster processing
OLLAMA_CONFIG["temperature"] = 0.1

# Reduce max tokens
OLLAMA_CONFIG["max_tokens"] = 2048
```

---

## Development

### Project Structure
```
smart-redact/
├── core/                       # Core functionality
│   ├── document_processor.py   # Document processing
│   ├── ollama_client.py        # Ollama integration
│   ├── testing_engine.py       # Testing framework
│   └── scoring_system.py       # Scoring system
├── ui/                         # User interface
│   └── main.py                 # Streamlit app
├── utils/                      # Utilities
│   ├── utils.py                # Helper functions
│   └── error_handler.py        # Error handling
├── config/                     # Configuration
│   └── config.py               # Settings
├── tests/                      # Testing
│   ├── test_app.py             # Unit tests
│   └── run_tests.py            # Test runner
└── docs/                       # Documentation
    └── DOCUMENTATION.md        # This file
```

### Adding New Features

#### 1. New Anonymization Strategy
```python
# 1. Add to config.py
ANONYMIZATION_STRATEGIES["new_strategy"] = {
    "name": "New Strategy",
    "description": "Description of new strategy",
    "replacement_token": "[NEW]"
}

# 2. Add prompt template
PROMPT_TEMPLATES["new_strategy"] = """
Custom prompt for new strategy...
{text}
"""

# 3. Update UI in main.py
# Add to strategy selection dropdown
```

#### 2. New Test Category
```python
# 1. Add to testing_engine.py
def test_new_category(self, original_text: str, anonymized_text: str) -> Dict:
    # Implementation
    return {
        "score": calculated_score,
        "details": test_details,
        "risk_level": risk_level
    }

# 2. Add to run_all_tests()
results["new_category"] = self.test_new_category(original_text, anonymized_text)

# 3. Update scoring weights in config.py
SCORING_WEIGHTS["reconstruction_resistance"]["new_category"] = 0.05
```

#### 3. New Document Format
```python
# 1. Add to document_processor.py
def _extract_new_format_text(self, uploaded_file) -> str:
    # Implementation for new format
    return extracted_text

# 2. Update process_file()
elif file_extension == 'new_format':
    text = self._extract_new_format_text(uploaded_file)

# 3. Add to SUPPORTED_FORMATS in config.py
SUPPORTED_FORMATS["new_format"] = "application/new-format"
```

### Code Style Guidelines

#### Python Style
- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Keep functions under 50 lines
- Use meaningful variable names

#### Error Handling
```python
from error_handler import error_handler

@error_handler(context="Function name")
def your_function():
    # Implementation
    pass
```

#### Logging
```python
import logging

logging.info("Information message")
logging.warning("Warning message")
logging.error("Error message")
```

### Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature-name`
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Run test suite**: `python run_tests.py`
6. **Submit pull request**

---

## Performance & Limitations

### Performance Characteristics

#### Processing Speed
- **Small documents** (<5k words): ~30 seconds
- **Medium documents** (5k-20k words): ~2 minutes
- **Large documents** (20k+ words): ~5 minutes

#### Memory Usage
- **Base application**: ~2GB RAM
- **Llama 3 8B model**: ~8GB RAM
- **Document processing**: ~1GB per 10k words

#### Token Limits
- **Chunk size**: 4000 tokens (~3000 words)
- **Overlap**: 200 tokens (~150 words)
- **Max prompt**: 6000 tokens
- **Max response**: 4000 tokens

### Known Limitations

#### 1. Model Constraints
- Fixed to Llama 3 8B Instruct
- No GPU acceleration support
- Limited context window (8K tokens)
- English language only

#### 2. Document Processing
- OCR not implemented for scanned PDFs
- Complex document formatting may be lost
- Table extraction is basic
- Image content not processed

#### 3. Testing Limitations
- Cross-reference testing limited to uploaded corpus
- No access to external legal databases
- Linguistic fingerprinting is basic
- No real-time adversarial testing

#### 4. Scalability
- Single-threaded processing
- No distributed processing
- Memory-bound for large documents
- No batch processing optimization

### Future Improvements

#### Short Term
- GPU acceleration support
- Additional language models
- Improved OCR capabilities
- Better table handling

#### Long Term
- Multi-language support
- Real-time processing
- Advanced ML models
- Cloud deployment options

---

## License & Support

### License
This project is provided as-is for educational and research purposes.

### Support
For issues and questions:
1. Check this documentation
2. Review troubleshooting section
3. Check application logs
4. Run test suite for diagnostics

### Version Information
- **Version**: 1.0.0
- **Last Updated**: 2024
- **Python Version**: 3.8+
- **Dependencies**: See requirements.txt

---

*This documentation covers the complete Legal Document Anonymization Tool. For additional technical details, please refer to the source code and inline comments.*