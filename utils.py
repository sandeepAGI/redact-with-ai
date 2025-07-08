"""
Utility functions for the Legal Document Anonymization Tool
"""

import re
import tiktoken
from typing import List, Dict, Tuple
import spacy
from config import DOCUMENT_LIMITS, ENTITY_TYPES


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    Count tokens in text using tiktoken (approximation for Llama)
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except:
        # Fallback approximation: ~4 chars per token
        return len(text) // 4


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[Dict]:
    """
    Split text into chunks with semantic boundaries and overlap
    """
    if chunk_size is None:
        chunk_size = DOCUMENT_LIMITS["chunk_size_tokens"]
    if overlap is None:
        overlap = DOCUMENT_LIMITS["chunk_overlap_tokens"]
    
    # Split into paragraphs first
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    current_tokens = 0
    
    for paragraph in paragraphs:
        para_tokens = count_tokens(paragraph)
        
        # If single paragraph exceeds chunk size, split by sentences
        if para_tokens > chunk_size:
            sentences = split_sentences(paragraph)
            for sentence in sentences:
                sent_tokens = count_tokens(sentence)
                
                if current_tokens + sent_tokens > chunk_size and current_chunk:
                    # Save current chunk
                    chunks.append({
                        "text": current_chunk.strip(),
                        "tokens": current_tokens,
                        "chunk_id": len(chunks)
                    })
                    
                    # Start new chunk with overlap
                    overlap_text = get_overlap_text(current_chunk, overlap)
                    current_chunk = overlap_text + sentence
                    current_tokens = count_tokens(current_chunk)
                else:
                    current_chunk += sentence
                    current_tokens += sent_tokens
        else:
            # Add paragraph if it fits
            if current_tokens + para_tokens > chunk_size and current_chunk:
                # Save current chunk
                chunks.append({
                    "text": current_chunk.strip(),
                    "tokens": current_tokens,
                    "chunk_id": len(chunks)
                })
                
                # Start new chunk with overlap
                overlap_text = get_overlap_text(current_chunk, overlap)
                current_chunk = overlap_text + paragraph + '\n\n'
                current_tokens = count_tokens(current_chunk)
            else:
                current_chunk += paragraph + '\n\n'
                current_tokens += para_tokens
    
    # Add final chunk
    if current_chunk.strip():
        chunks.append({
            "text": current_chunk.strip(),
            "tokens": current_tokens,
            "chunk_id": len(chunks)
        })
    
    return chunks


def split_sentences(text: str) -> List[str]:
    """
    Split text into sentences using simple regex
    """
    sentence_pattern = r'(?<=[.!?])\s+'
    sentences = re.split(sentence_pattern, text)
    return [s.strip() for s in sentences if s.strip()]


def get_overlap_text(text: str, overlap_tokens: int) -> str:
    """
    Get the last portion of text for overlap
    """
    words = text.split()
    if len(words) <= overlap_tokens // 2:  # Rough approximation
        return text
    
    # Take last portion of words
    overlap_words = words[-(overlap_tokens // 2):]
    return ' '.join(overlap_words) + ' '


def extract_entities_spacy(text: str) -> Dict[str, List[str]]:
    """
    Extract entities using spaCy
    """
    try:
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        
        entities = {
            "legal": [],
            "personal": [],
            "business": [],
            "temporal": [],
            "jurisdictional": []
        }
        
        for ent in doc.ents:
            entity_info = {
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            }
            
            # Categorize entities
            if ent.label_ in ENTITY_TYPES["legal"]:
                entities["legal"].append(entity_info)
            if ent.label_ in ENTITY_TYPES["personal"]:
                entities["personal"].append(entity_info)
            if ent.label_ in ENTITY_TYPES["business"]:
                entities["business"].append(entity_info)
            if ent.label_ in ENTITY_TYPES["temporal"]:
                entities["temporal"].append(entity_info)
            if ent.label_ in ENTITY_TYPES["jurisdictional"]:
                entities["jurisdictional"].append(entity_info)
        
        return entities
    except Exception as e:
        print(f"Error in entity extraction: {e}")
        return {"legal": [], "personal": [], "business": [], "temporal": [], "jurisdictional": []}


def extract_legal_patterns(text: str) -> List[Dict]:
    """
    Extract legal-specific patterns (case citations, statutes, etc.)
    """
    patterns = []
    
    # Case citation patterns
    case_pattern = r'\b\d+\s+[A-Z][a-z]+\.?\s+\d+\b'
    case_matches = re.finditer(case_pattern, text)
    for match in case_matches:
        patterns.append({
            "type": "case_citation",
            "text": match.group(),
            "start": match.start(),
            "end": match.end()
        })
    
    # Statute patterns
    statute_pattern = r'\b\d+\s+U\.S\.C\.?\s+§?\s*\d+\b'
    statute_matches = re.finditer(statute_pattern, text)
    for match in statute_matches:
        patterns.append({
            "type": "statute",
            "text": match.group(),
            "start": match.start(),
            "end": match.end()
        })
    
    # Court patterns
    court_pattern = r'\b(Supreme Court|District Court|Court of Appeals|Bankruptcy Court)\b'
    court_matches = re.finditer(court_pattern, text, re.IGNORECASE)
    for match in court_matches:
        patterns.append({
            "type": "court",
            "text": match.group(),
            "start": match.start(),
            "end": match.end()
        })
    
    return patterns


def validate_file_size(file_size: int) -> bool:
    """
    Validate file size against limits
    """
    max_size_bytes = DOCUMENT_LIMITS["max_file_size_mb"] * 1024 * 1024
    return file_size <= max_size_bytes


def validate_word_count(text: str) -> Tuple[bool, int]:
    """
    Validate word count and return status and count
    """
    word_count = len(text.split())
    is_valid = word_count <= DOCUMENT_LIMITS["max_word_count"]
    return is_valid, word_count


def clean_text(text: str) -> str:
    """
    Clean and normalize text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep legal formatting
    text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\"\'\/\\]', '', text)
    
    return text.strip()


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts using simple word overlap
    """
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    if not union:
        return 0.0
    
    return len(intersection) / len(union)


def extract_unique_phrases(text: str, min_length: int = 3) -> List[str]:
    """
    Extract unique phrases that could be identifying
    """
    # Simple n-gram extraction
    words = text.lower().split()
    phrases = []
    
    for i in range(len(words) - min_length + 1):
        phrase = ' '.join(words[i:i + min_length])
        phrases.append(phrase)
    
    # Return unique phrases
    return list(set(phrases))


def mask_sensitive_data(text: str, mask_char: str = "*") -> str:
    """
    Mask sensitive data patterns
    """
    # Social Security Numbers
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', mask_char * 11, text)
    
    # Phone numbers
    text = re.sub(r'\b\d{3}-\d{3}-\d{4}\b', mask_char * 12, text)
    
    # Email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', mask_char * 10, text)
    
    return text