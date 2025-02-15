#!/bin/sh

# Start the Ollama server in the background
ollama serve &

sleep 5

# Ensure models are pulled before proceeding
if ! ollama list | grep -q "mistral"; then
    echo "Pulling Mistral model..."
    ollama pull mistral
fi

# if ! ollama list | grep -q "llama3"; then
#     echo "Pulling Llama3 model..."
#    ollama pull llama3
# fi

# TODO: Add further models here

wait
