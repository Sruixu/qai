import chromadb
from chromadb.config import Settings
import os
from typing import List, Dict, Any

class VectorStoreService:
    def __init__(self):
        # Use a persistent storage path
        self.persist_directory = os.path.join(os.getcwd(), "chroma_db")
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # Create or get collection
        # We use the default embedding function (all-MiniLM-L6-v2) built into Chroma for simplicity
        self.collection = self.client.get_or_create_collection(name="qai_knowledge_base")

    def add_document(self, doc_id: str, text: str, metadata: Dict[str, Any]):
        """
        Add a document to the vector store.
        """
        self.collection.upsert(
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )
        print(f"Upserted document {doc_id} to vector store.")

    def query_similar(self, query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Query for similar documents.
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        if results["documents"]:
            for i in range(len(results["documents"][0])):
                formatted_results.append({
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "id": results["ids"][0][i]
                })
        
        return formatted_results

vector_store = VectorStoreService()
