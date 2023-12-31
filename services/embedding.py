from typing import List, Tuple, Any, AnyStr
import json, logging, os, csv
from pathlib import Path

from langchain.document_loaders import CSVLoader
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma


def embed_json_as_csv(file_path: str) -> List[Document]:
    logging.info("Embedding JSON files")

    logging.info("--> Loading and refactoring JSON files")

    qa_set: List[Any] = []
    with open(file_path, "r") as f:
        qa_set = json.load(f)

    refactored_qa_set: List[Tuple(AnyStr, AnyStr)] = []
    for qa in qa_set:
        refactored_qa_set.append((qa["question"], qa["answer"]))

    refactored_path = os.path.join(
        os.path.dirname(file_path), "_" + os.path.basename(file_path)
    )
    with open(refactored_path, "w") as file:
        # Create a csv.writer object
        writer = csv.writer(file)

        # Write the header row
        writer.writerow(["Question", "Answer"])

        # Write the data rows
        writer.writerows(refactored_qa_set)

    logging.info("--> Successfully refactored JSON and saved.")
    logging.info("--> Loading and embedding JSON file")

    loader = CSVLoader(
        file_path=refactored_path,
        csv_args={
            "delimiter": ",",
            "quotechar": '"',
            "fieldnames": ["Question", "Answer"],
        },
    )
    CHROMA_DB_DIRECTORY = os.environ.get("CHROMA_DB_DIRECTORY")

    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings()

    Chroma.from_documents(texts, embeddings, persist_directory=CHROMA_DB_DIRECTORY)
    logging.info(texts)

    logging.info("--> Successfully embedded JSON file.")


def embed_json_as_raw_text(file_path: str) -> List[Document]:
    logging.info("Embedding JSON files")

    logging.info("--> Loading and refactoring JSON files")

    qa_set: List[Any] = []
    with open(file_path, "r") as f:
        qa_set = json.load(f)

    refactored_qa_set: List[Document] = []
    for qa in qa_set:
        refactored_qa_set.append(Document(page_content=f'Question:{qa["question"]}\nAnswer:{qa["answer"]}'))

    logging.info("--> Successfully refactored JSON and saved.")
    logging.info("--> Loading and embedding JSON file")

    CHROMA_DB_DIRECTORY = os.environ.get("CHROMA_DB_DIRECTORY")
    embeddings = OpenAIEmbeddings()
    Chroma.from_documents(refactored_qa_set, embeddings, persist_directory=CHROMA_DB_DIRECTORY)
    logging.info(refactored_qa_set)

    logging.info("--> Successfully embedded JSON file.")
