import os
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.memory import ConversationSummaryMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

def configure_retrieval_chain():
    
    # LLM
    llm = ChatOpenAI(streaming=True, callbacks=[StreamingStdOutCallbackHandler()], temperature=0, verbose=True)
    memory = ConversationSummaryMemory(llm=llm, memory_key="chat_history",return_messages=True)
    
    CHROMA_DB_DIRECTORY = os.environ.get("CHROMA_DB_DIRECTORY")
    vectorstore = Chroma(persist_directory=CHROMA_DB_DIRECTORY, embedding_function=OpenAIEmbeddings())

    retriever = vectorstore.as_retriever()
    qa = ConversationalRetrievalChain.from_llm(llm, retriever=retriever, memory=memory)
    return qa