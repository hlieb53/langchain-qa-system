import os
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA

from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryMemory

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

max_tokens = 32768

def configure_conversational_retrieval_chain():
    
    # LLM
    llm = ChatOpenAI(streaming=True, callbacks=[StreamingStdOutCallbackHandler()], temperature=0, verbose=True)
    memory = ConversationSummaryMemory(llm=llm, memory_key="chat_history",return_messages=True)
    
    CHROMA_DB_DIRECTORY = os.environ.get("CHROMA_DB_DIRECTORY")
    vectorstore = Chroma(persist_directory=CHROMA_DB_DIRECTORY, embedding_function=OpenAIEmbeddings())

    retriever = vectorstore.as_retriever()
    qa = ConversationalRetrievalChain.from_llm(llm, retriever=retriever, memory=memory)
    return qa

def configure_retrieval_chain(**kwargs):
    
    # LLM
    llm = OpenAI(verbose=True, **kwargs)
    
    CHROMA_DB_DIRECTORY = os.environ.get("CHROMA_DB_DIRECTORY")
    vectorstore = Chroma(persist_directory=CHROMA_DB_DIRECTORY, embedding_function=OpenAIEmbeddings())

    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vectorstore.as_retriever(search_kwargs={'k': 1}))

    return qa