# knowledge.py - Vector DB for RAG with PDF and TXT support (with OCR)
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_core.documents import Document
import os
from typing import List, Dict
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DOCUMENT_PATHS = [
    os.path.join(SCRIPT_DIR, "ghidra_docs", "guide(80-90).pdf")
]

PERSIST_DIRECTORY = os.path.join(SCRIPT_DIR, "ghidra_rag_db")
HUGGINGFACE_API_KEY = "key-here"

pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

class GhidraKnowledgeBase:
    def __init__(self, document_paths: List[str] = None, persist_directory: str = PERSIST_DIRECTORY):
        self.document_paths = document_paths or DOCUMENT_PATHS
        self.persist_directory = persist_directory
        self.vectorstore = None
        self.embeddings = HuggingFaceEndpointEmbeddings(
            model="sentence-transformers/all-mpnet-base-v2",
            huggingfacehub_api_token=HUGGINGFACE_API_KEY
        )
    
    def extract_text_with_ocr(self, pdf_path: str) -> List[Document]:
        """Extract text from PDF using OCR (for scanned PDF images)"""
        documents = []
        pdf_document = fitz.open(pdf_path)
        
        total_pages = len(pdf_document)
        
        for page_num in range(total_pages):
            page = pdf_document[page_num]
            
            text = page.get_text()
            if len(text.strip()) < 100:
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # OCR with Tesseract
                try:
                    text = pytesseract.image_to_string(img, lang='eng')
                except Exception as e:
                    text = ""
            
            # Create document
            if text.strip():
                documents.append(Document(
                    page_content=text,
                    metadata={
                        "source": pdf_path,
                        "page": page_num
                    }
                ))
        
        pdf_document.close()
        return documents
        
    def build_vector_db(self):
        """Build vector database from PDF and TXT files"""
        all_docs = []
        
        for doc_path in self.document_paths:
            if os.path.exists(doc_path):
                try:
                    if doc_path.lower().endswith('.pdf'):
                        docs = self.extract_text_with_ocr(doc_path)
                            
                    elif doc_path.lower().endswith('.txt'):
                        loader = TextLoader(doc_path, encoding='utf-8')
                        docs = loader.load()
                    else:
                        continue
                    
                    # Check content
                    if docs:
                        total_chars = sum(len(doc.page_content) for doc in docs)
                        if total_chars == 0:
                            continue
                    
                    all_docs.extend(docs)
                except Exception as e:
                    continue
            
        if not all_docs:
            raise ValueError("No documents found to process")
        
        # 2. Chunking
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", "class ", "def ", "public void", ". "]
        )
        splits = text_splitter.split_documents(all_docs)
        
        if not splits:
            raise ValueError("Cannot create chunks from documents")
        
        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        return self.vectorstore
    
    def load_vector_db(self):
        """Load existing vector database"""
        if os.path.exists(self.persist_directory):
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            return self.vectorstore
        else:
            raise ValueError(f"Vector DB does not exist at {self.persist_directory}")
    
    def query_relevant_chunks(self, query: str, k: int = 5) -> List[Dict[str, str]]:
        """Query to get k most relevant chunks
        
        Args:
            query: Question/query string
            k: Number of chunks to retrieve
            
        Returns:
            List of dicts containing content and metadata of chunks
        """
        if self.vectorstore is None:
            try:
                self.load_vector_db()
            except ValueError:
                self.build_vector_db()
        
        # Search for similar chunks
        results = self.vectorstore.similarity_search(query, k=k)
        
        # Format results - convert all values to strings for MCP compatibility
        formatted_results = []
        for i, doc in enumerate(results):
            formatted_results.append({
                "rank": str(i + 1),
                "content": doc.page_content,
                "source": str(doc.metadata.get("source", "unknown")),
                "page": str(doc.metadata.get("page", "unknown"))
            })
        
        return formatted_results
    
    def add_text_to_db(self, text_content: str, source_name: str = "manual_entry", metadata: Dict[str, str] = None) -> Dict[str, str]:
        """Add text content directly to vector database (for conclusions, notes, etc.)
        
        Args:
            text_content: Text content to add
            source_name: Name/label for this content (e.g., "conclusion", "analysis_result")
            metadata: Optional additional metadata dict
            
        Returns:
            Dict with status and info
        """
        if not text_content or not text_content.strip():
            return {"status": "error", "message": "Text content is empty"}
        
        if self.vectorstore is None:
            try:
                self.load_vector_db()
            except ValueError:
                return {"status": "error", "message": "No database found. Build it first."}
        
        try:
            # Prepare metadata
            doc_metadata = {
                "source": source_name,
                "type": "manual_entry",
                "added_by": "mcp_tool"
            }
            if metadata:
                doc_metadata.update(metadata)
            
            # Create document
            doc = Document(
                page_content=text_content,
                metadata=doc_metadata
            )
            
            # Chunk if text is long
            if len(text_content) > 1000:
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200,
                    separators=["\n\n", "\n", ". ", ", "]
                )
                chunks = text_splitter.split_documents([doc])
            else:
                chunks = [doc]
            
            # Add to vector store
            self.vectorstore.add_documents(chunks)
            
            return {
                "status": "success",
                "message": f"Added {len(chunks)} chunk(s) from '{source_name}'",
                "chunks_added": str(len(chunks)),
                "source": source_name
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to add: {str(e)}"}
    
    def get_db_info(self) -> Dict[str, str]:
        """Get database information
        
        Returns:
            Dict with stats
        """
        if not os.path.exists(self.persist_directory):
            return {
                "status": "not_exists",
                "message": "Database not found",
                "location": self.persist_directory
            }
        
        try:
            if self.vectorstore is None:
                self.load_vector_db()
            
            collection = self.vectorstore._collection
            count = collection.count()
            
            return {
                "status": "exists",
                "total_chunks": str(count),
                "location": self.persist_directory
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Singleton instance
_knowledge_base = None

def get_knowledge_base() -> GhidraKnowledgeBase:
    """Get hoặc tạo knowledge base instance"""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = GhidraKnowledgeBase()
    return _knowledge_base

if __name__ == "__main__":
    # Test build vector DB
    kb = GhidraKnowledgeBase()
    kb.build_vector_db()
    
    # Test query
    results = kb.query_relevant_chunks("What is hypervisor host domain", k=3)
    for result in results:
        print(f"\n--- Rank {result['rank']} (Source: {result['source']}, Page: {result['page']}) ---")
        print(result['content'][:200] + "...")

    print("Done.")