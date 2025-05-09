# Travel Agency RAG System

A proof-of-concept Retrieval-Augmented Generation (RAG) system for a travel agency to automatically generate travel proposals from customer emails.

## Project Overview

This system:
1. Extracts key information from customer emails (destinations, dates, travelers, budget, interests)
2. Searches a knowledge base of travel packages using vector embeddings
3. Retrieves relevant packages based on customer needs
4. Generates personalized travel proposals using the retrieved context

## Requirements

- Python 3.8+
- Ollama - Running locally on http://localhost:11434
- Required Python packages (see requirements.txt)

## Installation

1. Make sure you have [Ollama](https://ollama.ai/) installed and running on your computer
2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

3. Make sure you have the required Ollama models:
   - For embeddings: `nomic-embed-text`
   - For generation: `llama3`

You can pull these models with the following commands:
```bash
ollama pull nomic-embed-text
ollama pull llama3
```

## Usage

There are two ways to run the system:

### 1. Run as a command-line application:

```bash
python src/main.py
```

This will:
- Load the sample travel packages data
- Load example customer emails
- Process one example email
- Show the extracted information
- Show the generated proposal

### 2. Run as a web API:

```bash
python run_api.py
```

This will start a FastAPI server at http://localhost:8000 with the following endpoints:

- `GET /`: Welcome message
- `GET /health`: Health check
- `GET /packages`: List all available travel packages
- `POST /process-email`: Process an email and generate a proposal. Send a JSON payload with:
  ```json
  {
    "email": "Your email content here"
  }
  ```

## Data

The system uses synthetic data:
- `data/synthetic/emails.json`: Sample customer emails
- `data/synthetic/travel_packages.json`: Sample travel packages

## Project Structure

- `src/`: Main source code
  - `email_processing/`: Email parsing and information extraction
  - `knowledge_base/`: Vector store and package database
  - `retrieval/`: Query building and package retrieval
  - `generation/`: Proposal generation with Ollama
  - `api/`: FastAPI web server
  - `main.py`: Command-line entry point
- `data/`: Data storage
- `tests/`: Test cases

## Customization

- Change Ollama models in `src/config.py`
- Add more travel packages in `data/synthetic/travel_packages.json`
- Modify prompt templates in `src/generation/prompt_templates.py`