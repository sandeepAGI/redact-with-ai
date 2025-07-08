"""
Document processing module for the Legal Document Anonymization Tool
Simple, focused document handling with chunking support
"""

import os
import tempfile
from typing import List, Dict, Optional, Tuple
import PyPDF2
import docx
from utils import chunk_text, validate_file_size, validate_word_count, clean_text, extract_entities_spacy, extract_legal_patterns
from config import SUPPORTED_FORMATS, DOCUMENT_LIMITS


class DocumentProcessor:
    """Simple document processor with chunking support"""
    
    def __init__(self):
        self.temp_dir = "temp_files"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def process_file(self, uploaded_file) -> Dict:
        """
        Process uploaded file and return document data
        """
        try:
            # Validate file size
            if not validate_file_size(uploaded_file.size):
                return {
                    "success": False,
                    "error": f"File too large. Maximum size: {DOCUMENT_LIMITS['max_file_size_mb']}MB"
                }
            
            # Extract text based on file type
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == 'pdf':
                text = self._extract_pdf_text(uploaded_file)
            elif file_extension == 'docx':
                text = self._extract_docx_text(uploaded_file)
            elif file_extension == 'txt':
                text = self._extract_txt_text(uploaded_file)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported file format: {file_extension}"
                }
            
            if not text.strip():
                return {
                    "success": False,
                    "error": "No text could be extracted from the document"
                }
            
            # Clean text
            text = clean_text(text)
            
            # Validate word count
            is_valid, word_count = validate_word_count(text)
            if not is_valid:
                return {
                    "success": False,
                    "error": f"Document too long. Maximum words: {DOCUMENT_LIMITS['max_word_count']}, found: {word_count}"
                }
            
            # Create chunks
            chunks = chunk_text(text)
            
            # Extract entities and patterns
            entities = extract_entities_spacy(text)
            legal_patterns = extract_legal_patterns(text)
            
            return {
                "success": True,
                "filename": uploaded_file.name,
                "file_type": file_extension,
                "text": text,
                "word_count": word_count,
                "chunks": chunks,
                "entities": entities,
                "legal_patterns": legal_patterns,
                "metadata": {
                    "chunk_count": len(chunks),
                    "total_entities": sum(len(ent_list) for ent_list in entities.values()),
                    "legal_patterns_count": len(legal_patterns)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing file: {str(e)}"
            }
    
    def _extract_pdf_text(self, uploaded_file) -> str:
        """Extract text from PDF file"""
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_file_path = tmp_file.name
            
            # Extract text from PDF
            text = ""
            with open(tmp_file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            # Clean up temp file
            os.unlink(tmp_file_path)
            
            return text
            
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")
    
    def _extract_docx_text(self, uploaded_file) -> str:
        """Extract text from DOCX file"""
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_file_path = tmp_file.name
            
            # Extract text from DOCX
            doc = docx.Document(tmp_file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            # Clean up temp file
            os.unlink(tmp_file_path)
            
            return text
            
        except Exception as e:
            raise Exception(f"DOCX extraction failed: {str(e)}")
    
    def _extract_txt_text(self, uploaded_file) -> str:
        """Extract text from TXT file"""
        try:
            # Read text file
            text = uploaded_file.read().decode('utf-8')
            return text
            
        except Exception as e:
            raise Exception(f"TXT extraction failed: {str(e)}")
    
    def process_batch(self, uploaded_files: List) -> List[Dict]:
        """
        Process multiple files in batch
        """
        if len(uploaded_files) > DOCUMENT_LIMITS['max_batch_files']:
            return [{
                "success": False,
                "error": f"Too many files. Maximum: {DOCUMENT_LIMITS['max_batch_files']}"
            }]
        
        results = []
        for uploaded_file in uploaded_files:
            result = self.process_file(uploaded_file)
            results.append(result)
        
        return results
    
    def get_document_summary(self, document_data: Dict) -> Dict:
        """
        Get summary statistics for a document
        """
        if not document_data.get("success"):
            return {"error": "Document processing failed"}
        
        return {
            "filename": document_data["filename"],
            "file_type": document_data["file_type"],
            "word_count": document_data["word_count"],
            "chunk_count": document_data["metadata"]["chunk_count"],
            "entities_found": document_data["metadata"]["total_entities"],
            "legal_patterns_found": document_data["metadata"]["legal_patterns_count"],
            "entity_breakdown": {
                category: len(entities) 
                for category, entities in document_data["entities"].items()
            }
        }
    
    def save_processed_document(self, document_data: Dict, output_path: str) -> bool:
        """
        Save processed document data to file
        """
        try:
            import json
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(document_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving document: {e}")
            return False
    
    def cleanup_temp_files(self):
        """
        Clean up temporary files
        """
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                os.makedirs(self.temp_dir, exist_ok=True)
        except Exception as e:
            print(f"Error cleaning up temp files: {e}")