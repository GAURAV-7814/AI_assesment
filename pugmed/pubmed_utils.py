from Bio import Entrez
import os

def search_pubmed(query, max_results=3):
    Entrez.email = os.getenv("NCBI_EMAIL")
    Entrez.api_key = os.getenv("NCBI_API_KEY")
    
    try:
        # Search for IDs
        handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
        record = Entrez.read(handle)
        handle.close()
        ids = record.get("IdList", [])
        
        if not ids:
            return []
        
        # Fetch Details
        handle = Entrez.efetch(db="pubmed", id=",".join(ids), rettype="abstract", retmode="xml")
        articles = Entrez.read(handle)
        handle.close()
        
        results = []
        for art in articles.get('PubmedArticle', []):
            medline = art['MedlineCitation']['Article']
            title = medline.get('ArticleTitle', "No Title")
            
            abstract_data = medline.get('Abstract', {}).get('AbstractText', ["No abstract available."])
            abstract = " ".join([str(text) for text in abstract_data])
            
            pmid = art['MedlineCitation']['PMID']
            link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            results.append({"title": title, "content": abstract, "link": link})
        return results
    except Exception as e:
        print(f"PubMed Error: {e}")
        return []