"""ChromaDB utilities for managing vector storage."""

import os
import chromadb
import google.generativeai as genai
from chromadb.api.types import Documents, EmbeddingFunction
from config import CHROMA_DB_PATH, GEMINI_API_KEY

class GoogleGenAIEmbeddingFunction(EmbeddingFunction):
    """Custom embedding function using Google's Generative AI."""
    
    def __init__(self, api_key, model_name="models/embedding-001"):
        """Initialize with Google Generative AI API."""
        self.api_key = api_key
        self.model_name = model_name
        genai.configure(api_key=api_key)
        
    def __call__(self, input: Documents) -> list:
        """Generate embeddings for the given input documents.
        
        Args:
            input: List of text documents to generate embeddings for
            
        Returns:
            List of embeddings, one for each input document
        """
        embeddings = []
        
        for text in input:
            # Ensure the text isn't too long for the API
            if len(text) > 25000:
                text = text[:25000]
                
            # Get embedding from the Google API
            try:
                embedding_model = genai.get_embedding_model(self.model_name)
                embedding = embedding_model.embed_content(
                    content=text,
                    task_type="retrieval_document",
                )
                embeddings.append(embedding["embedding"])
            except Exception as e:
                print(f"Error generating embedding: {e}")
                # Return a zero vector as fallback
                embeddings.append([0.0] * 768)  # Default dimension for embeddings
                
        return embeddings

class VectorStore:
    def __init__(self, collection_name="project_risks"):
        """Initialize the vector store with ChromaDB."""
        # Ensure directory exists
        os.makedirs(CHROMA_DB_PATH, exist_ok=True)
        
        # Initialize client
        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        
        # Setup custom embedding function using Gemini
        self.embedding_function = GoogleGenAIEmbeddingFunction(
            api_key=GEMINI_API_KEY
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )
        
    def add_document(self, doc_id, text, metadata=None):
        """Add a document to the vector store."""
        self.collection.add(
            documents=[text],
            metadatas=[metadata] if metadata else None,
            ids=[doc_id]
        )
        
    def search(self, query, n_results=5):
        """Search for similar documents in the vector store."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results
    
    def get_document(self, doc_id):
        """Retrieve a document by ID."""
        return self.collection.get(ids=[doc_id])