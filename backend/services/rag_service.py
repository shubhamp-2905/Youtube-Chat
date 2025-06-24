from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
import os

class RAGService:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.getenv('GOOGLE_API_KEY')
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
    
    def process_transcript(self, transcript):
        """Process transcript and create vector store"""
        try:
            # Split transcript into chunks
            chunks = self.text_splitter.create_documents([transcript])
            
            # Create vector store
            vector_store = FAISS.from_documents(chunks, self.embeddings)
            
            return vector_store
            
        except Exception as e:
            print(f"Error processing transcript: {str(e)}")
            raise e
    
    def retrieve_relevant_chunks(self, vector_store, query, k=4):
        """Retrieve relevant chunks for a query"""
        try:
            retriever = vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": k}
            )
            
            relevant_docs = retriever.invoke(query)
            
            # Format chunks
            context_text = "\n\n".join(doc.page_content for doc in relevant_docs)
            
            return context_text
            
        except Exception as e:
            print(f"Error retrieving chunks: {str(e)}")
            raise e