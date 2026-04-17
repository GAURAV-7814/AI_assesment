import os
from dotenv import load_dotenv
from pubmed_utils import search_pubmed
from rag_engine import get_answer

# Load keys from .env
load_dotenv()

def main():
    print("--- Medical Research Assistant (Gemini + PubMed) ---")
    
    while True:
        query = input("\nEnter your medical question (or 'exit'): ")
        if query.lower() == 'exit':
            break
            
        print("Searching PubMed for the latest research...")
        docs = search_pubmed(query)
        
        if not docs:
            print("No relevant articles found.")
            continue
            
        print(f"Found {len(docs)} articles. Generating answer...")
        response = get_answer(query, docs)
        
        print("\n" + "="*50)
        print("AI ANALYSIS:")
        print(response['result'])
        print("="*50)
        
        print("\nCITATIONS:")
        for d in docs:
            print(f"- {d['title']}")
            print(f"  URL: {d['link']}")

if __name__ == "__main__":
    main()