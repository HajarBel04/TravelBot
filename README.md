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
- Node.js and npm (for the frontend)
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




### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd travel-rag-frontend
```
1. Install dependencies:

```bash
npm install
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
- `GET /api/statsl`: Get system statistics

### 3. Run the Frontend:
In a separate terminal, navigate to the frontend directory:

```bash
cd travel-rag-frontend
```
Start the development server:


```bash
npm run dev
```
Access the web application at:

```bash
http://localhost:3000
```


## Applying Bug Fixes
To apply all bug fixes to the system, run:
```bash
python apply_all_fixes.py
```

This script will:

1. Fix the Beach Getaway package data
2. Fix the email extractor to avoid duplicate fields with different values
3. Fix the retriever for better package ranking
4. Rebuild the vector store with enhanced text


## Enhancing the System

To enhance the system with additional data sources, run:
```bash
python enhance_data_sources.py
```


## Data

The system uses synthetic data:
- `data/synthetic/emails.json`: Sample customer emails
- `data/synthetic/travel_packages.json`: Sample travel packages
- `data/synthetic/enriched_travel_packages.json`: Enhanced travel package data

## Advanced Features
### Enhanced Proposal Generator
* Extracts enriched data from packages
* Generates detailed day-by-day itineraries
* Includes weather information when available
* Provides practical travel tips

### RAG Evaluation Metrics

Performance metrics are tracked using the `rag_evaluation_metrics.py` module:
* Extraction completeness
* Retrieval diversity and relevance
* Generation quality
* End-to-end performance

### Frontend Features

The frontend includes:
* Chat interface for submitting travel requests
* Visualization of itineraries with day-by-day breakdown
* Dashboard for system statistics
* Destination browser


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
- Adjust vector search parameters in `src/knowledge_base/vector_store.py`




