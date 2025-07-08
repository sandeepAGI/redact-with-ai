"""
Reconstruction resistance testing engine
Tests anonymized documents against various attack vectors
"""

import re
import random
from typing import Dict, List, Tuple, Optional
from utils import calculate_similarity, extract_unique_phrases, extract_entities_spacy, extract_legal_patterns
from ollama_client import OllamaClient
from config import SCORING_WEIGHTS


class ReconstructionTester:
    """Test anonymized documents for reconstruction resistance"""
    
    def __init__(self, ollama_client: OllamaClient = None):
        self.ollama_client = ollama_client or OllamaClient()
        self.document_corpus = []  # Store uploaded documents for cross-reference
    
    def add_to_corpus(self, document_data: Dict):
        """Add document to corpus for cross-reference testing"""
        if document_data.get("success"):
            self.document_corpus.append({
                "filename": document_data["filename"],
                "text": document_data["text"],
                "entities": document_data["entities"],
                "legal_patterns": document_data["legal_patterns"]
            })
    
    def run_all_tests(self, original_text: str, anonymized_text: str, strategy: str = "strategic") -> Dict:
        """
        Run complete reconstruction resistance test suite
        """
        try:
            results = {}
            
            # Test 1: Direct Identifier Search
            print("Running direct identifier test...")
            results["direct_identifier"] = self.test_direct_identifiers(original_text, anonymized_text)
            
            # Test 2: Pattern Matching
            print("Running pattern matching test...")
            results["pattern_matching"] = self.test_pattern_matching(original_text, anonymized_text)
            
            # Test 3: Contextual Reconstruction
            print("Running contextual reconstruction test...")
            results["contextual_reconstruction"] = self.test_contextual_reconstruction(anonymized_text)
            
            # Test 4: Cross-Reference Analysis
            print("Running cross-reference test...")
            results["cross_reference"] = self.test_cross_reference(anonymized_text)
            
            # Test 5: Linguistic Fingerprinting
            print("Running linguistic fingerprinting test...")
            results["linguistic_fingerprint"] = self.test_linguistic_fingerprinting(original_text, anonymized_text)
            
            # Calculate overall resistance score
            resistance_score = self.calculate_resistance_score(results)
            
            return {
                "success": True,
                "strategy": strategy,
                "test_results": results,
                "resistance_score": resistance_score,
                "risk_assessment": self.assess_risk_level(results),
                "recommendations": self.generate_recommendations(results)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Testing failed: {str(e)}"
            }
    
    def test_direct_identifiers(self, original_text: str, anonymized_text: str) -> Dict:
        """
        Test A: Search for remaining direct identifiers
        """
        try:
            # Extract entities from original text
            original_entities = extract_entities_spacy(original_text)
            
            # Flatten all entities
            all_entities = []
            for category, entities in original_entities.items():
                for entity in entities:
                    all_entities.append(entity["text"].lower())
            
            # Search for exact matches in anonymized text
            anonymized_lower = anonymized_text.lower()
            matches_found = []
            
            for entity in all_entities:
                if entity in anonymized_lower:
                    matches_found.append(entity)
            
            # Calculate score
            if all_entities:
                score = max(0, 100 - (len(matches_found) / len(all_entities) * 100))
            else:
                score = 100
            
            return {
                "score": round(score, 2),
                "total_entities": len(all_entities),
                "matches_found": len(matches_found),
                "leaked_entities": matches_found[:10],  # Show first 10
                "risk_level": "high" if score < 70 else "medium" if score < 90 else "low"
            }
            
        except Exception as e:
            return {
                "score": 0,
                "error": f"Direct identifier test failed: {str(e)}"
            }
    
    def test_pattern_matching(self, original_text: str, anonymized_text: str) -> Dict:
        """
        Test B: Identify document through unique patterns
        """
        try:
            # Extract legal patterns from both texts
            original_patterns = extract_legal_patterns(original_text)
            anonymized_patterns = extract_legal_patterns(anonymized_text)
            
            # Check for preserved unique patterns
            preserved_patterns = []
            for orig_pattern in original_patterns:
                for anon_pattern in anonymized_patterns:
                    if orig_pattern["text"].lower() == anon_pattern["text"].lower():
                        preserved_patterns.append(orig_pattern["text"])
            
            # Test for unique phrase preservation
            original_phrases = extract_unique_phrases(original_text, min_length=4)
            anonymized_phrases = extract_unique_phrases(anonymized_text, min_length=4)
            
            preserved_phrases = []
            for phrase in original_phrases:
                if phrase in anonymized_phrases:
                    preserved_phrases.append(phrase)
            
            # Calculate uniqueness score
            total_patterns = len(original_patterns) + len(original_phrases)
            total_preserved = len(preserved_patterns) + len(preserved_phrases)
            
            if total_patterns > 0:
                uniqueness_score = max(0, 100 - (total_preserved / total_patterns * 100))
            else:
                uniqueness_score = 100
            
            return {
                "score": round(uniqueness_score, 2),
                "total_patterns": total_patterns,
                "preserved_patterns": total_preserved,
                "preserved_legal_patterns": preserved_patterns[:5],
                "preserved_phrases": preserved_phrases[:5],
                "risk_level": "high" if uniqueness_score < 70 else "medium" if uniqueness_score < 90 else "low"
            }
            
        except Exception as e:
            return {
                "score": 0,
                "error": f"Pattern matching test failed: {str(e)}"
            }
    
    def test_contextual_reconstruction(self, anonymized_text: str) -> Dict:
        """
        Test C: LLM-powered reverse engineering attempt
        """
        try:
            # Use LLM to attempt reconstruction
            reconstruction_result = self.ollama_client.test_reconstruction(anonymized_text)
            
            if not reconstruction_result["success"]:
                return {
                    "score": 0,
                    "error": reconstruction_result["error"]
                }
            
            reconstruction_text = reconstruction_result["reconstruction_attempt"]
            
            # Analyze reconstruction quality
            confidence_indicators = [
                "confident", "certain", "likely", "probably", "appears to be",
                "suggests", "indicates", "evidence of", "based on", "clearly"
            ]
            
            reconstruction_lower = reconstruction_text.lower()
            confidence_count = sum(1 for indicator in confidence_indicators if indicator in reconstruction_lower)
            
            # Count specific details mentioned
            specific_details = [
                "case name", "court", "judge", "attorney", "company", "date",
                "location", "plaintiff", "defendant", "parties"
            ]
            
            details_count = sum(1 for detail in specific_details if detail in reconstruction_lower)
            
            # Calculate reconstruction resistance score
            max_confidence = len(confidence_indicators)
            max_details = len(specific_details)
            
            confidence_penalty = (confidence_count / max_confidence) * 50
            details_penalty = (details_count / max_details) * 50
            
            score = max(0, 100 - confidence_penalty - details_penalty)
            
            return {
                "score": round(score, 2),
                "reconstruction_attempt": reconstruction_text[:500] + "..." if len(reconstruction_text) > 500 else reconstruction_text,
                "confidence_indicators_found": confidence_count,
                "specific_details_mentioned": details_count,
                "processing_time": reconstruction_result["processing_time"],
                "risk_level": "high" if score < 70 else "medium" if score < 90 else "low"
            }
            
        except Exception as e:
            return {
                "score": 0,
                "error": f"Contextual reconstruction test failed: {str(e)}"
            }
    
    def test_cross_reference(self, anonymized_text: str) -> Dict:
        """
        Test D: Cross-reference against document corpus
        """
        try:
            if not self.document_corpus:
                return {
                    "score": 100,
                    "message": "No corpus available for cross-reference testing",
                    "risk_level": "low"
                }
            
            # Calculate similarity with corpus documents
            similarities = []
            for doc in self.document_corpus:
                similarity = calculate_similarity(anonymized_text, doc["text"])
                similarities.append({
                    "filename": doc["filename"],
                    "similarity": similarity
                })
            
            # Find highest similarity
            max_similarity = max(similarities, key=lambda x: x["similarity"])
            
            # Calculate cross-reference resistance score
            # Higher similarity = lower resistance
            score = max(0, 100 - (max_similarity["similarity"] * 100))
            
            return {
                "score": round(score, 2),
                "corpus_size": len(self.document_corpus),
                "highest_similarity": round(max_similarity["similarity"], 3),
                "similar_document": max_similarity["filename"],
                "all_similarities": [(s["filename"], round(s["similarity"], 3)) for s in similarities],
                "risk_level": "high" if score < 70 else "medium" if score < 90 else "low"
            }
            
        except Exception as e:
            return {
                "score": 0,
                "error": f"Cross-reference test failed: {str(e)}"
            }
    
    def test_linguistic_fingerprinting(self, original_text: str, anonymized_text: str) -> Dict:
        """
        Test E: Analyze writing style preservation
        """
        try:
            # Analyze sentence structure
            original_sentences = re.split(r'[.!?]+', original_text)
            anonymized_sentences = re.split(r'[.!?]+', anonymized_text)
            
            original_avg_length = sum(len(s.split()) for s in original_sentences) / len(original_sentences)
            anonymized_avg_length = sum(len(s.split()) for s in anonymized_sentences) / len(anonymized_sentences)
            
            # Calculate vocabulary overlap
            original_words = set(word.lower() for word in original_text.split())
            anonymized_words = set(word.lower() for word in anonymized_text.split())
            
            vocab_overlap = len(original_words.intersection(anonymized_words)) / len(original_words)
            
            # Analyze unique phrases
            original_phrases = extract_unique_phrases(original_text)
            anonymized_phrases = extract_unique_phrases(anonymized_text)
            
            phrase_overlap = len(set(original_phrases).intersection(set(anonymized_phrases))) / len(original_phrases)
            
            # Calculate linguistic fingerprint score
            structure_similarity = 1 - abs(original_avg_length - anonymized_avg_length) / original_avg_length
            
            # Lower similarity = better anonymization
            fingerprint_score = max(0, 100 - (vocab_overlap * 30 + phrase_overlap * 40 + structure_similarity * 30))
            
            return {
                "score": round(fingerprint_score, 2),
                "vocabulary_overlap": round(vocab_overlap, 3),
                "phrase_overlap": round(phrase_overlap, 3),
                "structure_similarity": round(structure_similarity, 3),
                "original_avg_sentence_length": round(original_avg_length, 1),
                "anonymized_avg_sentence_length": round(anonymized_avg_length, 1),
                "risk_level": "high" if fingerprint_score < 70 else "medium" if fingerprint_score < 90 else "low"
            }
            
        except Exception as e:
            return {
                "score": 0,
                "error": f"Linguistic fingerprinting test failed: {str(e)}"
            }
    
    def calculate_resistance_score(self, test_results: Dict) -> float:
        """
        Calculate weighted composite resistance score
        """
        weights = SCORING_WEIGHTS["reconstruction_resistance"]
        
        total_score = 0
        for test_name, weight in weights.items():
            test_result = test_results.get(test_name, {})
            score = test_result.get("score", 0)
            total_score += score * weight
        
        return round(total_score, 2)
    
    def assess_risk_level(self, test_results: Dict) -> Dict:
        """
        Assess overall risk level and identify high-risk factors
        """
        high_risk_factors = []
        medium_risk_factors = []
        low_risk_factors = []
        
        for test_name, result in test_results.items():
            risk_level = result.get("risk_level", "unknown")
            
            if risk_level == "high":
                high_risk_factors.append(test_name)
            elif risk_level == "medium":
                medium_risk_factors.append(test_name)
            else:
                low_risk_factors.append(test_name)
        
        return {
            "high_risk_factors": high_risk_factors,
            "medium_risk_factors": medium_risk_factors,
            "low_risk_factors": low_risk_factors,
            "overall_risk": "high" if high_risk_factors else "medium" if medium_risk_factors else "low"
        }
    
    def generate_recommendations(self, test_results: Dict) -> List[str]:
        """
        Generate improvement recommendations based on test results
        """
        recommendations = []
        
        # Direct identifier issues
        if test_results.get("direct_identifier", {}).get("score", 100) < 80:
            recommendations.append("Consider using more aggressive entity replacement strategy")
            recommendations.append("Review entity extraction to catch missed identifiers")
        
        # Pattern matching issues
        if test_results.get("pattern_matching", {}).get("score", 100) < 80:
            recommendations.append("Replace or generalize unique legal patterns")
            recommendations.append("Consider breaking up distinctive phrase structures")
        
        # Contextual reconstruction issues
        if test_results.get("contextual_reconstruction", {}).get("score", 100) < 80:
            recommendations.append("Reduce contextual clues that enable reconstruction")
            recommendations.append("Consider more abstract anonymization approach")
        
        # Cross-reference issues
        if test_results.get("cross_reference", {}).get("score", 100) < 80:
            recommendations.append("Ensure sufficient differentiation from similar documents")
            recommendations.append("Consider additional randomization elements")
        
        # Linguistic fingerprinting issues
        if test_results.get("linguistic_fingerprint", {}).get("score", 100) < 80:
            recommendations.append("Vary sentence structure and vocabulary")
            recommendations.append("Consider style transformation in addition to anonymization")
        
        if not recommendations:
            recommendations.append("Anonymization quality is good - no major improvements needed")
        
        return recommendations
    
    def run_adversarial_tests(self, anonymized_text: str, attacker_levels: List[str] = None) -> Dict:
        """
        Run adversarial tests simulating different attacker capabilities
        """
        if attacker_levels is None:
            attacker_levels = ["naive", "professional", "advanced", "expert"]
        
        results = {}
        
        for level in attacker_levels:
            results[level] = self.simulate_attacker(anonymized_text, level)
        
        return results
    
    def simulate_attacker(self, anonymized_text: str, attacker_level: str) -> Dict:
        """
        Simulate different types of attackers
        """
        try:
            if attacker_level == "naive":
                # Simple keyword searches
                keywords = ["plaintiff", "defendant", "court", "judge", "attorney"]
                found_keywords = [kw for kw in keywords if kw.lower() in anonymized_text.lower()]
                success_rate = len(found_keywords) / len(keywords)
                
            elif attacker_level == "professional":
                # Legal database access simulation
                legal_patterns = extract_legal_patterns(anonymized_text)
                success_rate = min(1.0, len(legal_patterns) / 10)
                
            elif attacker_level == "advanced":
                # LLM assistance simulation
                reconstruction_result = self.ollama_client.test_reconstruction(anonymized_text)
                if reconstruction_result["success"]:
                    # Analyze reconstruction quality
                    confidence_words = ["confident", "certain", "likely"]
                    reconstruction_lower = reconstruction_result["reconstruction_attempt"].lower()
                    confidence_count = sum(1 for word in confidence_words if word in reconstruction_lower)
                    success_rate = min(1.0, confidence_count / 3)
                else:
                    success_rate = 0.0
                
            elif attacker_level == "expert":
                # Domain knowledge + sophisticated tools
                entities = extract_entities_spacy(anonymized_text)
                total_entities = sum(len(ent_list) for ent_list in entities.values())
                success_rate = min(1.0, total_entities / 20)
                
            else:
                success_rate = 0.0
            
            resistance_score = max(0, 100 - (success_rate * 100))
            
            return {
                "attacker_level": attacker_level,
                "success_rate": round(success_rate, 3),
                "resistance_score": round(resistance_score, 2),
                "risk_level": "high" if resistance_score < 70 else "medium" if resistance_score < 90 else "low"
            }
            
        except Exception as e:
            return {
                "attacker_level": attacker_level,
                "success_rate": 0.0,
                "resistance_score": 0.0,
                "error": str(e)
            }