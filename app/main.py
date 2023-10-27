from dotenv import load_dotenv
import os, logging
from typing import Annotated

from fastapi import FastAPI, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosedOK

from langchain.callbacks.manager import AsyncCallbackManager

load_dotenv()

from services import embedding, chain
from services.utils import StreamingLLMCallbackHandler, ChatResponse, MESSAGE_ERROR, MESSAGE_NORMAL, SENDER_USER,SENDER_AGENT

temp_dir = "temp"
app = FastAPI()
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logging.basicConfig(filename="./output.log", level=logging.INFO)
    logging.info("Doing startup stuff")
    
    CHROMA_DB_DIRECTORY = os.environ.get("CHROMA_DB_DIRECTORY")
    if not os.path.exists(CHROMA_DB_DIRECTORY):
        os.mkdir(CHROMA_DB_DIRECTORY)
        
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)

    logging.info("Done startup stuff")

# Example route
@app.get("/")
async def root():
    return {"message": "Hello, the APIs are now ready for your embeds and queries!!!"}

@app.post("/embed")
async def embed_json(files: Annotated[list[UploadFile], File(description="Upload JSON")]):
    """
    Upload the JSON files to embed.
    The JSON should have the following format: [{"Question": "", "Answer": ""}]
    """
    
    succedded_files = []
    for file in files:
        logging.info(f"{file.filename} received")
        try:
            file_path = os.path.join(temp_dir, file.filename)
            logging.info(file_path)
            with open(file_path, "wb") as result_file:
                content = await file.read()
                logging.info(len(content))
                result_file.write(content)
            logging.info("AAA")
            embedding.embed_json_as_raw_text(file_path)
            os.remove(file_path)
            
            succedded_files.append(file.filename)
            
            logging.info(f"Successfully embedded")
        except Exception as e:
            print(e)
            logging.info(f"{file.filename} isn't embedded")
    return {"status": "success", "payload": succedded_files}

@app.websocket("/qa")
async def qa(websocket: WebSocket):
    """
    Generates answers for questions
    """
    logging.info("Got Websocket Request")
    await websocket.accept()
    
    qa_chain = chain.configure_retrieval_chain(callback_manager = AsyncCallbackManager([StreamingLLMCallbackHandler(websocket)]), streaming=True, temperature=0)
    
    while True:
        try:
            question = await websocket.receive_text()
            resp = ChatResponse(
                sender=SENDER_USER, message=question, type=MESSAGE_NORMAL
            )
            await websocket.send_json(resp.dict())
            answer = await qa_chain.arun({"query": question})

        except WebSocketDisconnect:
            logging.info("WebSocketDisconnect")
            # TODO try to reconnect with back-off
            break
        except ConnectionClosedOK:
            logging.info("ConnectionClosedOK")
            # TODO handle this?
            break
        except Exception as e:
            logging.error(e)
            resp = ChatResponse(
                sender=SENDER_AGENT,
                message="Sorry, something went wrong. Try again.",
                type=MESSAGE_ERROR,
            )
            await websocket.send_json(resp.dict())