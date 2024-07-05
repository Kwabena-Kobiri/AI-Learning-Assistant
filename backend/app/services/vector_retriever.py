import os
import logging
import glob
from app.config import Config
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

class VectorRetriever:
    def __init__(self, index_name="personal_documentation"):
        self.index_name = index_name
        os.environ["OPENAI_API_KEY"] = Config.OPENAI_API_KEY
        # Use os.path.join to create the path to the documents folder
        self.documents_folder = os.path.join(os.path.dirname(__file__), "documents")
        self.faiss_index_file = os.path.join(self.documents_folder, f"{self.index_name}.faiss")

    # Vectorise the data in the documents folder
    def data_vectoriser(self):
        
        logging.info("Checking for documents in the local documents folder")
        documents = []
        if os.path.exists(self.documents_folder):
            for filename in os.listdir(self.documents_folder):
                if filename.endswith(".pdf"):
                    file_path = os.path.join(self.documents_folder, filename)
                    logging.info(f"Found PDF document: {file_path}")
                    print(f"Found PDF document: {file_path}")
                    loader = PyMuPDFLoader(file_path)
                    documents.extend(loader.load())
        else:
            logging.warning(f"The documents folder '{self.documents_folder}' does not exist")
            print(f"The documents folder '{self.documents_folder}' does not exist")

        embeddings = OpenAIEmbeddings(openai_api_key=Config.OPENAI_API_KEY)

        if documents:
            logging.info("Documents found, creating FAISS index")
            print("Documents found, creating FAISS index")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200
            )
            texts = text_splitter.split_documents(documents)

            vectorstore = FAISS.from_documents(documents=texts, embedding=embeddings)
            vectorstore.save_local(self.faiss_index_file)
            logging.info(f"FAISS index saved to {self.faiss_index_file}")
            
            # Find all PDF files in the documents folder
            pdf_files = glob.glob(os.path.join(self.documents_folder, "*.pdf"))

            # Loop through the list of PDF files and remove each one
            for pdf_file in pdf_files:
                try:
                    os.remove(pdf_file)
                    print(f"Removed: {pdf_file}")
                except Exception as e:
                    print(f"Error removing {pdf_file}: {e}")

            print("All PDF files have been removed.")
    
    # Retriever from saved FAISS Index
    def get_retriever(self):
        
        embeddings = OpenAIEmbeddings(openai_api_key=Config.OPENAI_API_KEY)
        
        if os.path.exists(self.faiss_index_file):
            vectorstore = FAISS.load_local(self.faiss_index_file, embeddings=embeddings, allow_dangerous_deserialization=True)
            logging.info(f"Loaded FAISS index from {self.faiss_index_file}")
        else:
            error_message = "No existing FAISS index."
            logging.error(error_message)
            raise FileNotFoundError(error_message)

        retriever = vectorstore.as_retriever()
        logging.info("Returning Retriever")
        return retriever