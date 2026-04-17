from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains import RetrievalQA

def get_answer(user_query, documents):
    # 1. Chunking
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
    texts = text_splitter.create_documents(
        [doc['content'] for doc in documents], 
        metadatas=[{"title": d['title'], "link": d['link']} for d in documents]
    )

    # 2. Vector DB (Ephemeral)
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        task_type="retrieval_document"
    )
    vectorstore = Chroma.from_documents(texts, embeddings)

    # 3. LLM Setup
    llm = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",  # Add -preview
        temperature=0
    )

    # 4. RAG Chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5})
    )
    
    return qa_chain.invoke(user_query)