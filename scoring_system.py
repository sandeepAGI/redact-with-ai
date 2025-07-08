"""
Scoring system for anonymization quality assessment
Combines reconstruction resistance and strategic value preservation
"""

from typing import Dict, List, Tuple
from config import SCORING_WEIGHTS, SCORE_THRESHOLDS
from utils import extract_entities_spacy, extract_legal_patterns, calculate_similarity
import re


class ScoringSystem:
    """Comprehensive scoring system for anonymization quality"""
    
    def __init__(self):
        self.weights = SCORING_WEIGHTS
        self.thresholds = SCORE_THRESHOLDS
    
    def calculate_overall_score(self, reconstruction_results: Dict, strategic_value_results: Dict) -> Dict:
        """
        Calculate overall anonymization quality score
        """
        try:
            # Calculate reconstruction resistance score
            resistance_score = self.calculate_reconstruction_resistance_score(reconstruction_results)
            
            # Get strategic value score (already calculated and passed in)
            strategic_score = strategic_value_results.get('strategic_value', 0.0)
            
            # Calculate overall weighted score
            overall_score = (
                resistance_score * self.weights["overall"]["reconstruction_resistance"] +
                strategic_score * self.weights["overall"]["strategic_value_preservation"]
            )
            
            # Determine quality level
            quality_level = self.get_quality_level(overall_score)
            
            return {
                "success": True,
                "overall_score": round(overall_score, 2),
                "reconstruction_resistance_score": round(resistance_score, 2),
                "strategic_value_score": round(strategic_score, 2),
                "quality_level": quality_level,
                "score_breakdown": {
                    "reconstruction_resistance": {
                        "score": round(resistance_score, 2),
                        "weight": self.weights["overall"]["reconstruction_resistance"],
                        "contribution": round(resistance_score * self.weights["overall"]["reconstruction_resistance"], 2)
                    },
                    "strategic_value": {
                        "score": round(strategic_score, 2),
                        "weight": self.weights["overall"]["strategic_value_preservation"],
                        "contribution": round(strategic_score * self.weights["overall"]["strategic_value_preservation"], 2)
                    }
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Overall scoring failed: {str(e)}"
            }
    
    def calculate_reconstruction_resistance_score(self, test_results: Dict) -> float:
        """
        Calculate weighted reconstruction resistance score
        """
        weights = self.weights["reconstruction_resistance"]
        total_score = 0
        
        for test_name, weight in weights.items():
            test_result = test_results.get(test_name, {})
            score = test_result.get("score", 0)
            total_score += score * weight
        
        return total_score
    
    def calculate_strategic_value_score(self, original_text: str, anonymized_text: str, strategy: str = "strategic") -> float:
        """
        Calculate strategic value preservation score
        """
        try:
            # Test legal principle retention
            legal_retention_score = self.test_legal_principle_retention(original_text, anonymized_text)
            
            # Test educational value
            educational_score = self.test_educational_value(original_text, anonymized_text)
            
            # Test business intelligence preservation
            business_score = self.test_business_intelligence(original_text, anonymized_text)
            
            # Test procedural guidance preservation
            procedural_score = self.test_procedural_guidance(original_text, anonymized_text)
            
            # Calculate weighted score
            weights = self.weights["strategic_value"]
            total_score = (
                legal_retention_score * weights["legal_principle_retention"] +
                educational_score * weights["educational_value"] +
                business_score * weights["business_intelligence"] +
                procedural_score * weights["procedural_guidance"]
            )
            
            return total_score
            
        except Exception as e:
            print(f"Strategic value scoring failed: {e}")
            return 0.0
    
    def test_legal_principle_retention(self, original_text: str, anonymized_text: str) -> float:
        """
        Test how well legal principles are retained
        """
        try:
            # Extract legal concepts and terms
            legal_terms = [
                "contract", "breach", "liability", "damages", "negligence", "statute",
                "precedent", "jurisdiction", "motion", "discovery", "evidence",
                "testimony", "ruling", "judgment", "appeal", "constitutional",
                "due process", "burden of proof", "standard of care"
            ]
            
            original_legal_count = sum(1 for term in legal_terms if term.lower() in original_text.lower())
            anonymized_legal_count = sum(1 for term in legal_terms if term.lower() in anonymized_text.lower())
            
            # Calculate retention rate
            if original_legal_count == 0:
                return 100.0
            
            retention_rate = anonymized_legal_count / original_legal_count
            
            # Extract legal patterns
            original_patterns = extract_legal_patterns(original_text)
            anonymized_patterns = extract_legal_patterns(anonymized_text)
            
            # Check for preserved legal reasoning structure
            reasoning_indicators = [
                "therefore", "because", "since", "as a result", "consequently",
                "however", "nevertheless", "furthermore", "moreover", "in contrast"
            ]
            
            original_reasoning = sum(1 for indicator in reasoning_indicators if indicator.lower() in original_text.lower())
            anonymized_reasoning = sum(1 for indicator in reasoning_indicators if indicator.lower() in anonymized_text.lower())
            
            reasoning_retention = anonymized_reasoning / original_reasoning if original_reasoning > 0 else 1.0
            
            # Combine scores
            legal_score = (retention_rate * 0.7 + reasoning_retention * 0.3) * 100
            
            return min(100, max(0, legal_score))
            
        except Exception as e:
            print(f"Legal principle retention test failed: {e}")
            return 0.0
    
    def test_educational_value(self, original_text: str, anonymized_text: str) -> float:
        """
        Test educational value preservation
        """
        try:
            # Look for educational indicators
            educational_elements = [
                "example", "illustrates", "demonstrates", "shows", "teaches",
                "principle", "concept", "theory", "practice", "method",
                "approach", "strategy", "technique", "process", "procedure"
            ]
            
            original_educational = sum(1 for element in educational_elements if element.lower() in original_text.lower())
            anonymized_educational = sum(1 for element in educational_elements if element.lower() in anonymized_text.lower())
            
            # Calculate preservation rate
            if original_educational == 0:
                return 100.0
            
            preservation_rate = anonymized_educational / original_educational
            
            # Check for abstract concepts preservation
            abstract_concepts = [
                "analysis", "interpretation", "conclusion", "rationale",
                "reasoning", "logic", "argument", "position", "stance"
            ]
            
            original_abstract = sum(1 for concept in abstract_concepts if concept.lower() in original_text.lower())
            anonymized_abstract = sum(1 for concept in abstract_concepts if concept.lower() in anonymized_text.lower())
            
            abstract_preservation = anonymized_abstract / original_abstract if original_abstract > 0 else 1.0
            
            # Combine scores
            educational_score = (preservation_rate * 0.6 + abstract_preservation * 0.4) * 100
            
            return min(100, max(0, educational_score))
            
        except Exception as e:
            print(f"Educational value test failed: {e}")
            return 0.0
    
    def test_business_intelligence(self, original_text: str, anonymized_text: str) -> float:
        """
        Test business intelligence preservation
        """
        try:
            # Business context indicators
            business_terms = [
                "market", "industry", "competition", "strategy", "revenue",
                "costs", "profit", "loss", "investment", "risk", "opportunity",
                "negotiation", "contract", "deal", "partnership", "merger"
            ]
            
            original_business = sum(1 for term in business_terms if term.lower() in original_text.lower())
            anonymized_business = sum(1 for term in business_terms if term.lower() in anonymized_text.lower())
            
            # Calculate preservation rate
            if original_business == 0:
                return 100.0
            
            business_preservation = anonymized_business / original_business
            
            # Check for strategic insights
            strategic_terms = [
                "competitive advantage", "market position", "strategic approach",
                "business model", "value proposition", "risk assessment"
            ]
            
            original_strategic = sum(1 for term in strategic_terms if term in original_text.lower())
            anonymized_strategic = sum(1 for term in strategic_terms if term in anonymized_text.lower())
            
            strategic_preservation = anonymized_strategic / original_strategic if original_strategic > 0 else 1.0
            
            # Combine scores
            business_score = (business_preservation * 0.7 + strategic_preservation * 0.3) * 100
            
            return min(100, max(0, business_score))
            
        except Exception as e:
            print(f"Business intelligence test failed: {e}")
            return 0.0
    
    def test_procedural_guidance(self, original_text: str, anonymized_text: str) -> float:
        """
        Test procedural guidance preservation
        """
        try:
            # Procedural indicators
            procedural_terms = [
                "step", "process", "procedure", "method", "approach",
                "first", "second", "third", "next", "then", "finally",
                "before", "after", "during", "timeline", "deadline"
            ]
            
            original_procedural = sum(1 for term in procedural_terms if term.lower() in original_text.lower())
            anonymized_procedural = sum(1 for term in procedural_terms if term.lower() in anonymized_text.lower())
            
            # Calculate preservation rate
            if original_procedural == 0:
                return 100.0
            
            procedural_preservation = anonymized_procedural / original_procedural
            
            # Check for timing information
            timing_patterns = [
                r'\b\d+\s*(days?|weeks?|months?|years?)\b',
                r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b',
                r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
            ]
            
            original_timing = sum(len(re.findall(pattern, original_text.lower())) for pattern in timing_patterns)
            anonymized_timing = sum(len(re.findall(pattern, anonymized_text.lower())) for pattern in timing_patterns)
            
            timing_preservation = anonymized_timing / original_timing if original_timing > 0 else 1.0
            
            # Combine scores
            procedural_score = (procedural_preservation * 0.8 + timing_preservation * 0.2) * 100
            
            return min(100, max(0, procedural_score))
            
        except Exception as e:
            print(f"Procedural guidance test failed: {e}")
            return 0.0
    
    def get_quality_level(self, score: float) -> Dict:
        """
        Determine quality level based on score
        """
        if score >= self.thresholds["excellent"]:
            return {
                "level": "excellent",
                "description": "Production ready",
                "color": "green",
                "recommendation": "Document is ready for use"
            }
        elif score >= self.thresholds["good"]:
            return {
                "level": "good",
                "description": "Minor improvements needed",
                "color": "lightgreen",
                "recommendation": "Consider minor refinements"
            }
        elif score >= self.thresholds["acceptable"]:
            return {
                "level": "acceptable",
                "description": "Requires review",
                "color": "yellow",
                "recommendation": "Review and improve before use"
            }
        elif score >= self.thresholds["poor"]:
            return {
                "level": "poor",
                "description": "Significant issues",
                "color": "orange",
                "recommendation": "Significant improvements required"
            }
        else:
            return {
                "level": "failed",
                "description": "Do not use",
                "color": "red",
                "recommendation": "Do not use - major security issues"
            }
    
    def generate_detailed_report(self, overall_results: Dict, reconstruction_results: Dict, strategic_results: Dict) -> Dict:
        """
        Generate comprehensive scoring report
        """
        try:
            report = {
                "executive_summary": {
                    "overall_score": overall_results["overall_score"],
                    "quality_level": overall_results["quality_level"],
                    "recommendation": overall_results["quality_level"]["recommendation"]
                },
                "detailed_scores": {
                    "reconstruction_resistance": {
                        "overall_score": overall_results["reconstruction_resistance_score"],
                        "component_scores": {
                            test_name: result.get("score", 0)
                            for test_name, result in reconstruction_results.items()
                        }
                    },
                    "strategic_value": {
                        "overall_score": overall_results["strategic_value_score"],
                        "component_scores": {
                            "legal_principle_retention": strategic_results.get("legal_principle_retention", 0),
                            "educational_value": strategic_results.get("educational_value", 0),
                            "business_intelligence": strategic_results.get("business_intelligence", 0),
                            "procedural_guidance": strategic_results.get("procedural_guidance", 0)
                        }
                    }
                },
                "risk_analysis": {
                    "high_risk_areas": [],
                    "medium_risk_areas": [],
                    "low_risk_areas": []
                },
                "recommendations": []
            }
            
            # Analyze risks
            for test_name, result in reconstruction_results.items():
                risk_level = result.get("risk_level", "unknown")
                if risk_level == "high":
                    report["risk_analysis"]["high_risk_areas"].append(test_name)
                elif risk_level == "medium":
                    report["risk_analysis"]["medium_risk_areas"].append(test_name)
                else:
                    report["risk_analysis"]["low_risk_areas"].append(test_name)
            
            # Generate recommendations
            if overall_results["overall_score"] < 70:
                report["recommendations"].append("Consider using a more aggressive anonymization strategy")
            if overall_results["reconstruction_resistance_score"] < 80:
                report["recommendations"].append("Improve reconstruction resistance by addressing high-risk test areas")
            if overall_results["strategic_value_score"] < 80:
                report["recommendations"].append("Balance anonymization with strategic value preservation")
            
            return report
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Report generation failed: {str(e)}"
            }
    
    def compare_strategies(self, strategy_results: Dict) -> Dict:
        """
        Compare multiple anonymization strategies
        """
        try:
            comparison = {
                "best_overall": None,
                "best_security": None,
                "best_utility": None,
                "strategy_comparison": []
            }
            
            best_overall_score = 0
            best_security_score = 0
            best_utility_score = 0
            
            for strategy, results in strategy_results.items():
                overall_score = results.get("overall_score", 0)
                security_score = results.get("reconstruction_resistance_score", 0)
                utility_score = results.get("strategic_value_score", 0)
                
                comparison["strategy_comparison"].append({
                    "strategy": strategy,
                    "overall_score": overall_score,
                    "security_score": security_score,
                    "utility_score": utility_score,
                    "quality_level": results.get("quality_level", {}).get("level", "unknown")
                })
                
                if overall_score > best_overall_score:
                    best_overall_score = overall_score
                    comparison["best_overall"] = strategy
                
                if security_score > best_security_score:
                    best_security_score = security_score
                    comparison["best_security"] = strategy
                
                if utility_score > best_utility_score:
                    best_utility_score = utility_score
                    comparison["best_utility"] = strategy
            
            return comparison
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Strategy comparison failed: {str(e)}"
            }