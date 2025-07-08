"""
Error handling and validation utilities
Provides consistent error handling across the application
"""

import logging
import traceback
from typing import Dict, Any, Optional, Callable
from functools import wraps
import streamlit as st


class ErrorHandler:
    """Centralized error handling for the application"""
    
    def __init__(self, log_file: str = "app.log"):
        self.setup_logging(log_file)
    
    def setup_logging(self, log_file: str):
        """Setup logging configuration"""
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Also log to console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        logger = logging.getLogger()
        logger.addHandler(console_handler)
    
    def handle_error(self, error: Exception, context: str = "Unknown", user_message: str = None) -> Dict:
        """
        Handle errors with logging and user feedback
        """
        # Log the error
        logging.error(f"Error in {context}: {str(error)}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        
        # Determine user-friendly message
        if user_message:
            display_message = user_message
        else:
            display_message = self.get_user_friendly_message(error)
        
        return {
            "success": False,
            "error": display_message,
            "technical_error": str(error),
            "context": context
        }
    
    def get_user_friendly_message(self, error: Exception) -> str:
        """
        Convert technical errors to user-friendly messages
        """
        error_str = str(error).lower()
        
        if "connection" in error_str or "timeout" in error_str:
            return "Connection error. Please check if Ollama is running and try again."
        
        elif "memory" in error_str or "out of memory" in error_str:
            return "Memory error. Try processing a smaller document or restart the application."
        
        elif "file" in error_str and "not found" in error_str:
            return "File not found. Please check the file path and try again."
        
        elif "permission" in error_str or "access denied" in error_str:
            return "Permission error. Please check file permissions and try again."
        
        elif "invalid" in error_str or "format" in error_str:
            return "Invalid file format. Please use PDF, DOCX, or TXT files."
        
        elif "token" in error_str or "limit" in error_str:
            return "Document too large. Please try with a smaller document."
        
        elif "model" in error_str or "ollama" in error_str:
            return "AI model error. Please check if Llama 3 is installed and try again."
        
        else:
            return "An unexpected error occurred. Please try again or contact support."
    
    def validate_file_upload(self, uploaded_file) -> Dict:
        """
        Validate uploaded file
        """
        try:
            if uploaded_file is None:
                return {"success": False, "error": "No file uploaded"}
            
            # Check file size
            if uploaded_file.size > 50 * 1024 * 1024:  # 50MB
                return {"success": False, "error": "File too large (max 50MB)"}
            
            # Check file type
            allowed_extensions = ['pdf', 'docx', 'txt']
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension not in allowed_extensions:
                return {"success": False, "error": f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"}
            
            # Check filename
            if len(uploaded_file.name) > 255:
                return {"success": False, "error": "Filename too long"}
            
            return {"success": True, "message": "File validation passed"}
            
        except Exception as e:
            return self.handle_error(e, "File validation")
    
    def validate_text_input(self, text: str, max_length: int = 100000) -> Dict:
        """
        Validate text input
        """
        try:
            if not text or not text.strip():
                return {"success": False, "error": "Text cannot be empty"}
            
            if len(text) > max_length:
                return {"success": False, "error": f"Text too long (max {max_length} characters)"}
            
            return {"success": True, "message": "Text validation passed"}
            
        except Exception as e:
            return self.handle_error(e, "Text validation")
    
    def validate_strategy_config(self, strategy: str, custom_guidelines: str = None) -> Dict:
        """
        Validate anonymization strategy configuration
        """
        try:
            valid_strategies = ['traditional', 'strategic', 'educational', 'custom']
            
            if strategy not in valid_strategies:
                return {"success": False, "error": f"Invalid strategy. Must be one of: {', '.join(valid_strategies)}"}
            
            if strategy == 'custom' and not custom_guidelines:
                return {"success": False, "error": "Custom guidelines required for custom strategy"}
            
            if custom_guidelines and len(custom_guidelines) > 1000:
                return {"success": False, "error": "Custom guidelines too long (max 1000 characters)"}
            
            return {"success": True, "message": "Strategy configuration valid"}
            
        except Exception as e:
            return self.handle_error(e, "Strategy validation")
    
    def validate_ollama_connection(self, ollama_client) -> Dict:
        """
        Validate Ollama connection
        """
        try:
            connection_result = ollama_client.test_connection()
            
            if not connection_result['success']:
                return {
                    "success": False,
                    "error": "Cannot connect to Ollama. Please ensure Ollama is running.",
                    "technical_error": connection_result['error']
                }
            
            if not connection_result['llama_available']:
                return {
                    "success": False,
                    "error": "Llama 3 model not available. Please run 'ollama pull llama3:8b-instruct'",
                    "technical_error": "Model not found"
                }
            
            return {"success": True, "message": "Ollama connection validated"}
            
        except Exception as e:
            return self.handle_error(e, "Ollama connection validation")


def error_handler(context: str = "Unknown", user_message: str = None):
    """
    Decorator for error handling
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handler = ErrorHandler()
                error_result = handler.handle_error(e, context, user_message)
                
                # Display error in Streamlit if available
                if 'st' in globals():
                    st.error(error_result['error'])
                
                return error_result
        
        return wrapper
    return decorator


def safe_execute(func: Callable, *args, context: str = "Unknown", **kwargs) -> Dict:
    """
    Safely execute a function with error handling
    """
    try:
        result = func(*args, **kwargs)
        return {"success": True, "result": result}
    except Exception as e:
        handler = ErrorHandler()
        return handler.handle_error(e, context)


def validate_session_state(required_keys: list) -> Dict:
    """
    Validate required session state keys
    """
    try:
        missing_keys = []
        
        for key in required_keys:
            if key not in st.session_state:
                missing_keys.append(key)
        
        if missing_keys:
            return {
                "success": False,
                "error": f"Missing required data: {', '.join(missing_keys)}",
                "missing_keys": missing_keys
            }
        
        return {"success": True, "message": "Session state validation passed"}
        
    except Exception as e:
        handler = ErrorHandler()
        return handler.handle_error(e, "Session state validation")


def create_error_page(error_message: str, suggestions: list = None):
    """
    Create a standardized error page
    """
    st.error(f"❌ {error_message}")
    
    if suggestions:
        st.subheader("💡 Suggestions:")
        for suggestion in suggestions:
            st.write(f"• {suggestion}")
    
    st.subheader("🔧 Troubleshooting:")
    st.write("• Check if Ollama is running: `ollama serve`")
    st.write("• Verify Llama 3 model: `ollama pull llama3:8b-instruct`")
    st.write("• Restart the application")
    st.write("• Check application logs for technical details")


def handle_streamlit_error(error: Exception, context: str = "Unknown"):
    """
    Handle errors in Streamlit context
    """
    handler = ErrorHandler()
    error_result = handler.handle_error(error, context)
    
    # Display error in Streamlit
    st.error(error_result['error'])
    
    # Show technical details in expander
    with st.expander("Technical Details"):
        st.code(error_result['technical_error'])
    
    return error_result


def retry_with_backoff(func: Callable, max_retries: int = 3, initial_delay: float = 1.0):
    """
    Retry function with exponential backoff
    """
    import time
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            delay = initial_delay * (2 ** attempt)
            time.sleep(delay)
    
    return None


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class ProcessingError(Exception):
    """Custom exception for processing errors"""
    pass


class ConnectionError(Exception):
    """Custom exception for connection errors"""
    pass


# Global error handler instance
error_handler_instance = ErrorHandler()