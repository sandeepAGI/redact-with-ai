"""
Configuration settings for the Legal Document Anonymization Tool
"""

# Ollama Configuration
OLLAMA_CONFIG = {
    "endpoint": "http://localhost:11434",
    "model": "llama3:8b-instruct",
    "temperature": 0.3,
    "max_tokens": 4096,
    "top_p": 0.9,
    "stream": True
}

# Document Processing Limits
DOCUMENT_LIMITS = {
    "max_file_size_mb": 50,
    "max_word_count": 50000,
    "chunk_size_tokens": 4000,
    "chunk_overlap_tokens": 200,
    "max_batch_files": 10
}

# Supported File Formats
SUPPORTED_FORMATS = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "txt": "text/plain"
}

# Anonymization Strategies
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

# Scoring Weights
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

# Score Thresholds
SCORE_THRESHOLDS = {
    "excellent": 90,
    "good": 80,
    "acceptable": 70,
    "poor": 60,
    "failed": 0
}

# Entity Types for Recognition
ENTITY_TYPES = {
    "legal": ["PERSON", "ORG", "GPE", "LAW", "COURT", "JUDGE", "ATTORNEY"],
    "personal": ["PERSON", "PHONE", "EMAIL", "SSN", "ADDRESS"],
    "business": ["ORG", "MONEY", "PRODUCT", "EVENT"],
    "temporal": ["DATE", "TIME", "DURATION"],
    "jurisdictional": ["GPE", "LAW", "COURT"]
}

# Prompt Templates
PROMPT_TEMPLATES = {
    "traditional": """
You are a legal document anonymization specialist. Your task is to redact all identifying information from the following legal document text while preserving the document structure and legal meaning.

Replace the following with [REDACTED]:
- Names of people, companies, organizations
- Addresses, phone numbers, email addresses
- Case numbers, court names, dates
- Any other identifying information

Document text to anonymize:
{text}

Return only the anonymized text with no additional commentary.
""",
    
    "strategic": """
You are a legal document anonymization specialist. Your task is to anonymize the following legal document while preserving strategic legal insights and procedural guidance.

Anonymization rules:
- Replace specific names with generic descriptors (e.g., "Plaintiff", "Defendant", "The Company")
- Preserve legal strategies, arguments, and reasoning
- Maintain procedural steps and tactical information
- Keep industry context and business intelligence
- Replace dates with relative timeframes where possible

Document text to anonymize:
{text}

Return only the anonymized text with no additional commentary.
""",
    
    "educational": """
You are a legal document anonymization specialist. Your task is to transform the following legal document into educational principles while removing all case-specific details.

Transformation rules:
- Convert specific facts into general principles
- Replace parties with generic examples
- Focus on legal concepts and educational value
- Remove all identifying information
- Maintain the legal reasoning and educational insights

Document text to anonymize:
{text}

Return only the transformed educational text with no additional commentary.
""",
    
    "custom": """
You are a legal document anonymization specialist. Your task is to anonymize the following legal document according to these custom guidelines:

{custom_guidelines}

Document text to anonymize:
{text}

Return only the anonymized text with no additional commentary.
"""
}

# Directories
DIRECTORIES = {
    "temp_files": "temp_files",
    "exports": "exports",
    "uploads": "uploads"
}