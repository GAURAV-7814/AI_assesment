import os
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import CharacterTextSplitter

# We use a global variable to keep the Chroma database connection in memory
my_chroma_database = None

def init_rag(csv_path: str):
    global my_chroma_database
    
    # Using local Ollama, no API key needed

    try:
        # Load the CSV
        loader = CSVLoader(file_path=csv_path, encoding='utf-8')
        documents = loader.load()

        # Simple text splitter
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = text_splitter.split_documents(documents)

        # Initialize embeddings using Ollama
        embeddings = OllamaEmbeddings(model="nomic-embed-text")

        # Create Chroma vector store and persist to disk
        persist_directory = os.path.join(os.path.dirname(__file__), "..", "data", "chroma_db")
        my_chroma_database = Chroma.from_documents(docs, embeddings, persist_directory=persist_directory)
        print("RAG Vector Store initialized successfully.")
    except Exception as e:
        print(f"Error initializing RAG: {e}")


def search_college_info(query: str, k: int = 3) -> str:
    """
    Query the internal vector database (from CSV) for college information.
    """
    global my_chroma_database
    if not my_chroma_database:
        return "ChromaDB is not initialized. Please ensure Ollama is running and CSV is loaded."
    
    docs = my_chroma_database.similarity_search(query, k=k)
    
    if not docs:
        return "No relevant internal information found."
        
    results = []
    for doc in docs:
        results.append(doc.page_content)
        
    return "\n\n".join(results)
