# AgentDesk AI — AI-Powered IT Support Agent

AgentDesk AI is a portfolio project that demonstrates an AI-assisted IT support workflow using a hosted Gemini model, local knowledge retrieval, and Python tools.

## Features

- **AI Support Chat:** Answers IT troubleshooting questions using Gemini.
- **Knowledge Retrieval (RAG-style):** Searches Markdown documentation using TF-IDF and cosine similarity.
- **Source Attribution:** Shows which knowledge-base documents support an answer.
- **Service Health Dashboard:** Demonstrates authentication, API, and database status.
- **Support Ticket Creation:** Validates ticket details and generates incident IDs.
- **Automated Tests:** Covers agent behavior, service-status tools, and ticket validation.

## Technology Stack

- Python
- Streamlit
- Google Gemini API
- scikit-learn
- Pydantic
- pytest

## Architecture

1. The user submits a question through the Streamlit interface.
2. The retrieval module searches local Markdown documentation.
3. Relevant passages are sent to Gemini to generate a grounded response.
4. Python tools provide simulated service status and validated ticket creation.

## Run Locally

1. Create and activate a Python virtual environment.
2. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt