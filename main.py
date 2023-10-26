from dotenv import load_dotenv
import os, logging
from services.chain import configure_retrieval_chain
from services.embedding import embed_json

load_dotenv()

def startup():
    logging.info("Doing startup stuff")
    
    CHROMA_DB_DIRECTORY = os.environ.get("CHROMA_DB_DIRECTORY")
    if not os.path.exists(CHROMA_DB_DIRECTORY):
        os.mkdir(CHROMA_DB_DIRECTORY)

    logging.info("Done startup stuff")
    
def main():
    embed_json("assets/q_a.json")
    
    qa_chain = configure_retrieval_chain()
    question = input("Question:")
    qa_chain(question)
    print("Answer: ")
    
if __name__ == "__main__":
    main()