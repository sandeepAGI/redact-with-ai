"""
Test runner for the Legal Document Anonymization Tool
Simple test execution script
"""

import sys
import os
import subprocess
import time

def run_basic_tests():
    """Run basic functionality tests"""
    print("=" * 50)
    print("BASIC FUNCTIONALITY TESTS")
    print("=" * 50)
    
    try:
        # Test imports
        print("1. Testing imports...")
        from config import OLLAMA_CONFIG, ANONYMIZATION_STRATEGIES
        from utils import count_tokens, chunk_text
        from document_processor import DocumentProcessor
        from ollama_client import OllamaClient
        from testing_engine import ReconstructionTester
        from scoring_system import ScoringSystem
        from error_handler import ErrorHandler
        print("   ✓ All imports successful")
        
        # Test configuration
        print("2. Testing configuration...")
        assert OLLAMA_CONFIG['model'] == 'llama3:8b-instruct'
        assert len(ANONYMIZATION_STRATEGIES) == 4
        print("   ✓ Configuration loaded correctly")
        
        # Test utilities
        print("3. Testing utilities...")
        test_text = "This is a test sentence for the legal document anonymization tool."
        tokens = count_tokens(test_text)
        chunks = chunk_text(test_text, chunk_size=50, overlap=10)
        assert tokens > 0
        assert len(chunks) > 0
        print(f"   ✓ Token counting: {tokens} tokens")
        print(f"   ✓ Text chunking: {len(chunks)} chunks")
        
        # Test error handling
        print("4. Testing error handling...")
        handler = ErrorHandler()
        error_result = handler.handle_error(Exception("Test error"), "Test context")
        assert error_result['success'] == False
        assert 'error' in error_result
        print("   ✓ Error handling works")
        
        # Test validation
        print("5. Testing validation...")
        text_validation = handler.validate_text_input("Valid text")
        strategy_validation = handler.validate_strategy_config("strategic")
        assert text_validation['success'] == True
        assert strategy_validation['success'] == True
        print("   ✓ Validation functions work")
        
        # Test component initialization
        print("6. Testing component initialization...")
        processor = DocumentProcessor()
        ollama_client = OllamaClient()
        tester = ReconstructionTester()
        scorer = ScoringSystem()
        print("   ✓ All components initialize successfully")
        
        print("\n✅ All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Basic test failed: {e}")
        return False

def test_ollama_connection():
    """Test Ollama connection"""
    print("\n" + "=" * 50)
    print("OLLAMA CONNECTION TEST")
    print("=" * 50)
    
    try:
        from ollama_client import OllamaClient
        
        client = OllamaClient()
        print("Testing Ollama connection...")
        
        result = client.test_connection()
        
        if result['success']:
            print("✅ Ollama connection successful")
            print(f"   Models available: {result['models_available']}")
            print(f"   Llama 3 available: {result['llama_available']}")
            
            if result['llama_available']:
                print("✅ Llama 3 model ready")
                return True
            else:
                print("⚠️  Llama 3 model not found")
                print("   Run: ollama pull llama3:8b-instruct")
                return False
        else:
            print(f"❌ Ollama connection failed: {result['error']}")
            print("   Make sure Ollama is running: ollama serve")
            return False
            
    except Exception as e:
        print(f"❌ Ollama test failed: {e}")
        return False

def test_dependencies():
    """Test required dependencies"""
    print("\n" + "=" * 50)
    print("DEPENDENCY CHECK")
    print("=" * 50)
    
    required_packages = [
        'streamlit',
        'spacy',
        'nltk',
        'pandas',
        'PyPDF2',
        'docx',
        'requests',
        'tiktoken'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'docx':
                import docx
            elif package == 'PyPDF2':
                import PyPDF2
            else:
                __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All dependencies available")
        return True

def test_file_structure():
    """Test file structure"""
    print("\n" + "=" * 50)
    print("FILE STRUCTURE CHECK")
    print("=" * 50)
    
    required_files = [
        'main.py',
        'config.py',
        'utils.py',
        'document_processor.py',
        'ollama_client.py',
        'testing_engine.py',
        'scoring_system.py',
        'error_handler.py',
        'requirements.txt',
        'setup.sh'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"❌ {file} - MISSING")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("\n✅ All required files present")
        return True

def run_unit_tests():
    """Run unit tests"""
    print("\n" + "=" * 50)
    print("UNIT TESTS")
    print("=" * 50)
    
    try:
        # Run the test file
        result = subprocess.run([sys.executable, 'test_app.py'], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Unit tests passed")
            print(result.stdout)
            return True
        else:
            print("❌ Unit tests failed")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Unit tests timed out")
        return False
    except Exception as e:
        print(f"❌ Unit test execution failed: {e}")
        return False

def test_streamlit_app():
    """Test Streamlit app startup"""
    print("\n" + "=" * 50)
    print("STREAMLIT APP TEST")
    print("=" * 50)
    
    try:
        # Test if app can be imported without errors
        import main
        print("✅ Main app imports successfully")
        
        # Test if Streamlit can find the app
        result = subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'main.py', '--check'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Streamlit app structure valid")
            return True
        else:
            print("❌ Streamlit app check failed")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Streamlit test timed out")
        return False
    except Exception as e:
        print(f"❌ Streamlit test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 LEGAL DOCUMENT ANONYMIZATION TOOL - TEST SUITE")
    print("=" * 60)
    
    test_results = []
    
    # Run tests in order
    test_results.append(("File Structure", test_file_structure()))
    test_results.append(("Dependencies", test_dependencies()))
    test_results.append(("Basic Functionality", run_basic_tests()))
    test_results.append(("Ollama Connection", test_ollama_connection()))
    test_results.append(("Unit Tests", run_unit_tests()))
    test_results.append(("Streamlit App", test_streamlit_app()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed + failed} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Ready to run the application.")
        print("Start with: streamlit run main.py")
    else:
        print(f"\n⚠️  {failed} tests failed. Please fix issues before running.")
        
        # Provide specific guidance
        if not any(result for name, result in test_results if name == "Ollama Connection"):
            print("\n📝 Ollama Setup:")
            print("   1. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
            print("   2. Start Ollama: ollama serve")
            print("   3. Install model: ollama pull llama3:8b-instruct")
        
        if not any(result for name, result in test_results if name == "Dependencies"):
            print("\n📝 Dependencies Setup:")
            print("   pip install -r requirements.txt")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)