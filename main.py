from dotenv import load_dotenv
import os, logging
from services.chain import configure_retrieval_chain
from services.embedding import embed_json_as_csv, embed_json_as_raw_text

load_dotenv()

def startup():
    logging.info("Doing startup stuff")
    
    CHROMA_DB_DIRECTORY = os.environ.get("CHROMA_DB_DIRECTORY")
    if not os.path.exists(CHROMA_DB_DIRECTORY):
        os.mkdir(CHROMA_DB_DIRECTORY)

    logging.info("Done startup stuff")
    
def main():
    logging.basicConfig(filename="./output.log", level=logging.INFO)
    embed_json_as_raw_text("assets/q_a.json")
    
    qa_chain = configure_retrieval_chain()
    while True:
        print(f"{'-' * 40}\n")
        question = input("Question:")
        print("Answer:")
        qa_chain(question)
        print(f"\n{'-' * 40}\n")
    
if __name__ == "__main__":
    main()