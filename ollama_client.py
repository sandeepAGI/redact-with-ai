"""
Ollama client for LLM anonymization
Simple interface to Ollama API with chunking support
"""

import requests
import json
import time
from typing import Dict, List, Optional
from config import OLLAMA_CONFIG, PROMPT_TEMPLATES


class OllamaClient:
    """Simple Ollama API client"""
    
    def __init__(self, endpoint: str = None):
        self.endpoint = endpoint or OLLAMA_CONFIG["endpoint"]
        self.model = OLLAMA_CONFIG["model"]
        self.temperature = OLLAMA_CONFIG["temperature"]
        self.max_tokens = OLLAMA_CONFIG["max_tokens"]
        self.top_p = OLLAMA_CONFIG["top_p"]
    
    def test_connection(self) -> Dict:
        """Test connection to Ollama service"""
        try:
            response = requests.get(f"{self.endpoint}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                llama_available = any(self.model in model.get("name", "") for model in models)
                return {
                    "success": True,
                    "models_available": len(models),
                    "llama_available": llama_available,
                    "message": "Connected successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Connection failed: {str(e)}"
            }
    
    def generate_text(self, prompt: str, stream: bool = False) -> Dict:
        """Generate text using Ollama API"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": stream,
                "options": {
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "num_predict": self.max_tokens
                }
            }
            
            response = requests.post(
                f"{self.endpoint}/api/generate",
                json=payload,
                timeout=300  # 5 minute timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "text": result.get("response", ""),
                    "done": result.get("done", True),
                    "total_duration": result.get("total_duration", 0),
                    "load_duration": result.get("load_duration", 0),
                    "prompt_eval_count": result.get("prompt_eval_count", 0),
                    "eval_count": result.get("eval_count", 0)
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}"
            }
    
    def anonymize_text(self, text: str, strategy: str = "strategic", custom_guidelines: str = None) -> Dict:
        """
        Anonymize text using specified strategy
        """
        try:
            # Get prompt template
            if strategy == "custom" and custom_guidelines:
                prompt = PROMPT_TEMPLATES["custom"].format(
                    custom_guidelines=custom_guidelines,
                    text=text
                )
            else:
                prompt = PROMPT_TEMPLATES.get(strategy, PROMPT_TEMPLATES["strategic"]).format(text=text)
            
            # Generate anonymized text
            result = self.generate_text(prompt)
            
            if result["success"]:
                return {
                    "success": True,
                    "original_text": text,
                    "anonymized_text": result["text"].strip(),
                    "strategy": strategy,
                    "processing_time": result.get("total_duration", 0) / 1000000000,  # Convert to seconds
                    "token_usage": {
                        "prompt_tokens": result.get("prompt_eval_count", 0),
                        "completion_tokens": result.get("eval_count", 0),
                        "total_tokens": result.get("prompt_eval_count", 0) + result.get("eval_count", 0)
                    }
                }
            else:
                return {
                    "success": False,
                    "error": result["error"]
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Anonymization failed: {str(e)}"
            }
    
    def anonymize_chunks(self, chunks: List[Dict], strategy: str = "strategic", custom_guidelines: str = None) -> Dict:
        """
        Anonymize document chunks with progress tracking
        """
        try:
            anonymized_chunks = []
            total_chunks = len(chunks)
            failed_chunks = []
            total_processing_time = 0
            total_tokens = 0
            
            for i, chunk in enumerate(chunks):
                print(f"Processing chunk {i+1}/{total_chunks}...")
                
                result = self.anonymize_text(
                    chunk["text"], 
                    strategy=strategy,
                    custom_guidelines=custom_guidelines
                )
                
                if result["success"]:
                    anonymized_chunks.append({
                        "chunk_id": chunk["chunk_id"],
                        "original_text": chunk["text"],
                        "anonymized_text": result["anonymized_text"],
                        "original_tokens": chunk["tokens"],
                        "processing_time": result["processing_time"],
                        "token_usage": result["token_usage"]
                    })
                    
                    total_processing_time += result["processing_time"]
                    total_tokens += result["token_usage"]["total_tokens"]
                    
                else:
                    failed_chunks.append({
                        "chunk_id": chunk["chunk_id"],
                        "error": result["error"]
                    })
                
                # Small delay to prevent overwhelming the API
                time.sleep(0.1)
            
            # Combine anonymized chunks
            combined_text = ""
            for chunk in sorted(anonymized_chunks, key=lambda x: x["chunk_id"]):
                combined_text += chunk["anonymized_text"] + "\n\n"
            
            return {
                "success": True,
                "anonymized_text": combined_text.strip(),
                "strategy": strategy,
                "chunks_processed": len(anonymized_chunks),
                "chunks_failed": len(failed_chunks),
                "total_processing_time": total_processing_time,
                "total_tokens": total_tokens,
                "failed_chunks": failed_chunks,
                "chunk_details": anonymized_chunks
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Chunk anonymization failed: {str(e)}"
            }
    
    def test_reconstruction(self, anonymized_text: str) -> Dict:
        """
        Test reconstruction resistance using LLM
        """
        try:
            prompt = f"""
You are a skilled investigator trying to identify the original case or parties from this anonymized legal document. 
Based on the content, legal patterns, and any remaining clues, make your best guess about:

1. What type of legal case this might be
2. Possible parties involved
3. Jurisdiction or court system
4. Time period
5. Any specific case details you can deduce

Anonymized document:
{anonymized_text}

Provide your analysis and confidence level (1-10) for each guess.
"""
            
            result = self.generate_text(prompt)
            
            if result["success"]:
                return {
                    "success": True,
                    "reconstruction_attempt": result["text"],
                    "processing_time": result.get("total_duration", 0) / 1000000000
                }
            else:
                return {
                    "success": False,
                    "error": result["error"]
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Reconstruction test failed: {str(e)}"
            }
    
    def get_model_info(self) -> Dict:
        """Get information about the current model"""
        try:
            response = requests.post(
                f"{self.endpoint}/api/show",
                json={"name": self.model},
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "model_info": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Model info request failed: {str(e)}"
            }