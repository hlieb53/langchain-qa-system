# Welcome to Langchain QA System

## Prerequisites
You should make sure Python 3.11 is already installed on your local machine.
And plus, python3.11-venv must be installed.

## Setup

1. clone the repository from GitHub.

```bash
git clone https://github.com/eagerbeaver53/langchain-qa-system.git
cd langchain-qa-system/
```

2. Create python virtual environment.

```bash
# I would like to create virtual environment using python3.11-venv.
pip install --upgrade pip
python -m venv env
source env/bin/activate
```

3. Install required packages.

```bash
pip install -r requirements.txt
```

All done successfully!!! Now you can finish setting up the project.

## Usage

1. Create environment variable for the project.

```bash
cp example.env .env
```
2. Edit the environment variable with your options.

3. Paste the JSON file of predefined questions and answers in any directory.
- `OPENAI_API_KEY`: OpenAI API Key
- `CHROMA_DB_DIRECTORY`: The location of The local ChromaDB vectorstore.
4. Run `app/main.py` file in the virtual environment.

```bash
source env/bin/activate
gunicorn --bind 0.0.0.0:8000 app.main:app -k uvicorn.workers.UvicornWorker --timeout 1500 --reload
```

## Cautions

- The ChromaDB doesn't care about the double storing of same documents so please make sure you don't store same documents twice.
- If you want to embed documents to new database, Deleting `CHROMA_DB_DIRECTORY` will be the solution.

# Good luck to you with my project!!!