"""
Basic tests for the Legal Document Anonymization Tool
Simple test cases to verify core functionality
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

# Import application modules
from document_processor import DocumentProcessor
from ollama_client import OllamaClient
from testing_engine import ReconstructionTester
from scoring_system import ScoringSystem
from utils import chunk_text, count_tokens, extract_entities_spacy, calculate_similarity
from error_handler import ErrorHandler, ValidationError


class TestDocumentProcessor(unittest.TestCase):
    """Test document processing functionality"""
    
    def setUp(self):
        self.processor = DocumentProcessor()
    
    def test_text_chunking(self):
        """Test text chunking with token limits"""
        text = "This is a test document. " * 100  # Create a longer text
        chunks = chunk_text(text, chunk_size=100, overlap=20)
        
        self.assertGreater(len(chunks), 0)
        self.assertIsInstance(chunks, list)
        
        for chunk in chunks:
            self.assertIn('text', chunk)
            self.assertIn('tokens', chunk)
            self.assertIn('chunk_id', chunk)
    
    def test_token_counting(self):
        """Test token counting functionality"""
        text = "This is a test sentence."
        token_count = count_tokens(text)
        
        self.assertGreater(token_count, 0)
        self.assertIsInstance(token_count, int)
    
    def test_entity_extraction(self):
        """Test entity extraction"""
        text = "John Smith worked at Microsoft in Seattle on January 1, 2023."
        entities = extract_entities_spacy(text)
        
        self.assertIsInstance(entities, dict)
        self.assertIn('legal', entities)
        self.assertIn('personal', entities)
        self.assertIn('business', entities)
    
    @patch('tempfile.NamedTemporaryFile')
    def test_txt_processing(self, mock_temp_file):
        """Test TXT file processing"""
        # Mock uploaded file
        mock_file = Mock()
        mock_file.name = "test.txt"
        mock_file.size = 1000
        mock_file.read.return_value = b"This is test content for a legal document."
        
        # Mock temporary file
        mock_temp_file.return_value.__enter__.return_value.name = "temp.txt"
        
        result = self.processor.process_file(mock_file)
        
        # Should succeed for basic text
        self.assertTrue(result.get('success', False))
        self.assertIn('text', result)
        self.assertIn('chunks', result)
        self.assertIn('entities', result)


class TestOllamaClient(unittest.TestCase):
    """Test Ollama client functionality"""
    
    def setUp(self):
        self.client = OllamaClient()
    
    @patch('requests.get')
    def test_connection_success(self, mock_get):
        """Test successful Ollama connection"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [{"name": "llama3:8b-instruct"}]
        }
        mock_get.return_value = mock_response
        
        result = self.client.test_connection()
        
        self.assertTrue(result['success'])
        self.assertTrue(result['llama_available'])
    
    @patch('requests.get')
    def test_connection_failure(self, mock_get):
        """Test Ollama connection failure"""
        mock_get.side_effect = Exception("Connection failed")
        
        result = self.client.test_connection()
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    @patch('requests.post')
    def test_text_generation(self, mock_post):
        """Test text generation"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "This is anonymized text",
            "done": True,
            "total_duration": 1000000000,
            "prompt_eval_count": 50,
            "eval_count": 25
        }
        mock_post.return_value = mock_response
        
        result = self.client.generate_text("Test prompt")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['text'], "This is anonymized text")
    
    def test_chunk_anonymization(self):
        """Test chunk anonymization with mock"""
        # Mock chunks
        chunks = [
            {"text": "Test chunk 1", "tokens": 10, "chunk_id": 0},
            {"text": "Test chunk 2", "tokens": 15, "chunk_id": 1}
        ]
        
        with patch.object(self.client, 'anonymize_text') as mock_anonymize:
            mock_anonymize.return_value = {
                "success": True,
                "anonymized_text": "Anonymized chunk",
                "processing_time": 1.0,
                "token_usage": {"total_tokens": 20}
            }
            
            result = self.client.anonymize_chunks(chunks)
            
            self.assertTrue(result['success'])
            self.assertEqual(result['chunks_processed'], 2)
            self.assertEqual(result['chunks_failed'], 0)


class TestReconstructionTester(unittest.TestCase):
    """Test reconstruction resistance testing"""
    
    def setUp(self):
        self.tester = ReconstructionTester()
    
    def test_direct_identifier_test(self):
        """Test direct identifier detection"""
        original = "John Smith from Microsoft filed a lawsuit"
        anonymized = "The plaintiff from [COMPANY] filed a lawsuit"
        
        result = self.tester.test_direct_identifiers(original, anonymized)
        
        self.assertIn('score', result)
        self.assertIn('total_entities', result)
        self.assertIn('matches_found', result)
        self.assertGreater(result['score'], 0)
    
    def test_similarity_calculation(self):
        """Test similarity calculation"""
        text1 = "This is a test document"
        text2 = "This is another test document"
        
        similarity = calculate_similarity(text1, text2)
        
        self.assertGreater(similarity, 0)
        self.assertLessEqual(similarity, 1.0)
    
    def test_pattern_matching(self):
        """Test pattern matching detection"""
        original = "Case No. 123-CV-2023 in the District Court"
        anonymized = "Case No. [REDACTED] in the [COURT]"
        
        result = self.tester.test_pattern_matching(original, anonymized)
        
        self.assertIn('score', result)
        self.assertIn('total_patterns', result)
    
    def test_corpus_management(self):
        """Test document corpus management"""
        doc_data = {
            "success": True,
            "filename": "test.pdf",
            "text": "Test document content",
            "entities": {"legal": [], "personal": []},
            "legal_patterns": []
        }
        
        initial_size = len(self.tester.document_corpus)
        self.tester.add_to_corpus(doc_data)
        
        self.assertEqual(len(self.tester.document_corpus), initial_size + 1)


class TestScoringSystem(unittest.TestCase):
    """Test scoring system functionality"""
    
    def setUp(self):
        self.scorer = ScoringSystem()
    
    def test_resistance_score_calculation(self):
        """Test reconstruction resistance score calculation"""
        test_results = {
            "direct_identifier": {"score": 85},
            "pattern_matching": {"score": 90},
            "contextual_reconstruction": {"score": 80},
            "cross_reference": {"score": 95},
            "linguistic_fingerprint": {"score": 88}
        }
        
        score = self.scorer.calculate_reconstruction_resistance_score(test_results)
        
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 100)
    
    def test_quality_level_determination(self):
        """Test quality level determination"""
        # Test excellent score
        excellent_result = self.scorer.get_quality_level(95)
        self.assertEqual(excellent_result['level'], 'excellent')
        
        # Test poor score
        poor_result = self.scorer.get_quality_level(55)
        self.assertEqual(poor_result['level'], 'poor')
    
    def test_strategic_value_calculation(self):
        """Test strategic value preservation calculation"""
        original = "This contract demonstrates strategic business principles"
        anonymized = "This agreement demonstrates strategic business principles"
        
        score = self.scorer.calculate_strategic_value_score(original, anonymized)
        
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 100)


class TestErrorHandler(unittest.TestCase):
    """Test error handling functionality"""
    
    def setUp(self):
        self.handler = ErrorHandler()
    
    def test_error_handling(self):
        """Test error handling with exception"""
        error = Exception("Test error")
        result = self.handler.handle_error(error, "Test context")
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('technical_error', result)
        self.assertIn('context', result)
    
    def test_file_validation(self):
        """Test file validation"""
        # Mock valid file
        mock_file = Mock()
        mock_file.name = "test.pdf"
        mock_file.size = 1000
        
        result = self.handler.validate_file_upload(mock_file)
        self.assertTrue(result['success'])
        
        # Mock invalid file (too large)
        mock_file.size = 100 * 1024 * 1024  # 100MB
        result = self.handler.validate_file_upload(mock_file)
        self.assertFalse(result['success'])
    
    def test_text_validation(self):
        """Test text input validation"""
        # Valid text
        result = self.handler.validate_text_input("This is valid text")
        self.assertTrue(result['success'])
        
        # Empty text
        result = self.handler.validate_text_input("")
        self.assertFalse(result['success'])
        
        # Too long text
        long_text = "a" * 200000
        result = self.handler.validate_text_input(long_text)
        self.assertFalse(result['success'])
    
    def test_strategy_validation(self):
        """Test strategy configuration validation"""
        # Valid strategy
        result = self.handler.validate_strategy_config("strategic")
        self.assertTrue(result['success'])
        
        # Invalid strategy
        result = self.handler.validate_strategy_config("invalid")
        self.assertFalse(result['success'])
        
        # Custom strategy without guidelines
        result = self.handler.validate_strategy_config("custom")
        self.assertFalse(result['success'])
        
        # Custom strategy with guidelines
        result = self.handler.validate_strategy_config("custom", "Custom guidelines")
        self.assertTrue(result['success'])


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow"""
    
    def setUp(self):
        self.processor = DocumentProcessor()
        self.error_handler = ErrorHandler()
    
    def test_end_to_end_workflow_mock(self):
        """Test complete workflow with mocked components"""
        # Mock document processing
        mock_doc_result = {
            "success": True,
            "filename": "test.txt",
            "text": "This is a test legal document with John Smith as plaintiff.",
            "word_count": 11,
            "chunks": [{"text": "Test chunk", "tokens": 5, "chunk_id": 0}],
            "entities": {"legal": [], "personal": []},
            "legal_patterns": [],
            "metadata": {"chunk_count": 1, "total_entities": 0, "legal_patterns_count": 0}
        }
        
        # Mock anonymization
        mock_anon_result = {
            "success": True,
            "anonymized_text": "This is a test legal document with [PLAINTIFF] as plaintiff.",
            "strategy": "strategic",
            "chunks_processed": 1,
            "chunks_failed": 0,
            "total_processing_time": 1.0,
            "total_tokens": 20,
            "failed_chunks": []
        }
        
        # Mock testing
        mock_test_result = {
            "success": True,
            "test_results": {
                "direct_identifier": {"score": 85},
                "pattern_matching": {"score": 90},
                "contextual_reconstruction": {"score": 80},
                "cross_reference": {"score": 95},
                "linguistic_fingerprint": {"score": 88}
            },
            "resistance_score": 87.5,
            "risk_assessment": {"high_risk_factors": [], "medium_risk_factors": [], "low_risk_factors": ["all"]},
            "recommendations": ["Good anonymization quality"]
        }
        
        # Verify workflow components
        self.assertTrue(mock_doc_result['success'])
        self.assertTrue(mock_anon_result['success'])
        self.assertTrue(mock_test_result['success'])
        
        # Verify data flow
        self.assertIn('text', mock_doc_result)
        self.assertIn('anonymized_text', mock_anon_result)
        self.assertIn('resistance_score', mock_test_result)


def run_basic_tests():
    """Run basic functionality tests"""
    print("Running basic tests...")
    
    # Test utilities
    print("Testing utilities...")
    test_text = "This is a test sentence for token counting."
    tokens = count_tokens(test_text)
    print(f"✓ Token counting: {tokens} tokens")
    
    chunks = chunk_text(test_text, chunk_size=50, overlap=10)
    print(f"✓ Text chunking: {len(chunks)} chunks")
    
    # Test error handling
    print("Testing error handling...")
    handler = ErrorHandler()
    error_result = handler.handle_error(Exception("Test error"), "Test context")
    print(f"✓ Error handling: {error_result['success'] == False}")
    
    # Test validation
    print("Testing validation...")
    text_validation = handler.validate_text_input("Valid text")
    print(f"✓ Text validation: {text_validation['success']}")
    
    strategy_validation = handler.validate_strategy_config("strategic")
    print(f"✓ Strategy validation: {strategy_validation['success']}")
    
    print("Basic tests completed!")


if __name__ == '__main__':
    # Run basic tests first
    run_basic_tests()
    
    # Run unit tests
    print("\nRunning unit tests...")
    unittest.main(verbosity=2)