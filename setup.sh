#!/bin/bash
# CAJAL Quick Setup Script
# curl -fsSL https://raw.githubusercontent.com/Agnuxo1/CAJAL/main/setup.sh | bash

echo "🧠 CAJAL-4B-P2PCLAW Setup"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi

# Install cajal package
echo "📦 Installing cajal..."
pip install cajal

# Setup Ollama if available
if command -v ollama &> /dev/null; then
    echo "🦙 Setting up Ollama..."
    ollama pull Agnuxo/CAJAL-4B-P2PCLAW
    echo "✅ Ollama model ready: ollama run Agnuxo/CAJAL-4B-P2PCLAW"
fi

echo ""
echo "🎉 CAJAL is ready!"
echo "   CLI:    cajal 'Your question here'"
echo "   Server: cajal-server --port 8000"
echo "   Chat:   cajal -i"
echo ""
echo "   HuggingFace: https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW"
echo "   GitHub:      https://github.com/Agnuxo1/CAJAL"
