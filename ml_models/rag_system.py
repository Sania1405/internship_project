import chromadb
import os
from core.logger import logger

class RAGSystem:
    def __init__(self, data_path: str = "data/job_description.txt"):
        """
        Initializes the ChromaDB local vector store.
        It reads the text file and stores it as vectors in memory so the LLM can query it.
        """
        logger.info("Initializing ChromaDB RAG Vector Store...")
        
        # We use the ephemeral client so it stays in RAM and is fast, 
        # but in production, you'd use PersistentClient to save it to disk.
        self.chroma_client = chromadb.EphemeralClient()
         
        # Create a collection (like a table in SQL)
        self.collection = self.chroma_client.get_or_create_collection(name="company_knowledge")
        
        # Load the data
        if os.path.exists(data_path):
            with open(data_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # For a real app, you would 'chunk' this text into smaller paragraphs.
            # We are keeping it simple: dump the whole thing in as one chunk.
            self.collection.add(
                documents=[content],
                metadatas=[{"source": "job_description"}],
                ids=["doc1"]
            )
            logger.info("Successfully loaded Job Description into RAG Vector Store.")
        else:
            logger.warning(f"Could not find RAG data file at {data_path}")

    def query(self, question: str) -> str:
        """
        When the LLM asks a question about the company, we search ChromaDB.
        """
        results = self.collection.query(
            query_texts=[question],
            n_results=1
        )
        
        # Extract the returned document string
        if results['documents'] and len(results['documents'][0]) > 0:
            return results['documents'][0][0]
        else:
            return "No relevant information found in the company documentation."
