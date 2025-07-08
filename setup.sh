#!/bin/bash

# Legal Document Anonymization Tool Setup Script

echo "Setting up Legal Document Anonymization Tool..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
else
    echo "Ollama already installed."
fi

# Start Ollama service
echo "Starting Ollama service..."
ollama serve &
sleep 5

# Pull required model
echo "Pulling Llama 3 8B Instruct model..."
ollama pull llama3:8b-instruct

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Download spaCy model
echo "Downloading spaCy language model..."
python -m spacy download en_core_web_lg

# Download NLTK data
echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"

# Create necessary directories
mkdir -p temp_files
mkdir -p exports

echo "Setup complete! Run 'streamlit run main.py' to start the application."