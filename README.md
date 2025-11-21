# RAG MCP Server

MCP Server với RAG (Retrieval-Augmented Generation) để truy vấn tài liệu PDF sử dụng Pinecone cloud vector database.

## Yêu cầu

- Python 3.12+
- Tesseract OCR
- Pinecone API key (miễn phí)
- Huggingface API key (miễn phí)

## Cài đặt

### 1. Tạo project mới

```bash
uv init rag-server
cd rag-server
```

### 2. Cài đặt dependencies

```bash
uv add "mcp[cli]"
pip install "mcp[cli]"
```

### 3. Copy các file cần thiết

Copy các file sau vào folder mới:

- `main.py`
- `knowledge.py`
- Folder `ghidra_docs` (chứa tài liệu PDF)

### 4. Cấu hình

**Pinecone API Key:**

- Ib discord để lấy API key và thay vào **line 20** trong `knowledge.py`

**Huggingface API Key:**

- Đăng ký tài khoản miễn phí tại [Huggingface](https://huggingface.co/)
- Lấy API key và thay vào **line 22** trong `knowledge.py`

**Tesseract OCR:**

- Tải và cài đặt [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- Cập nhật đường dẫn Tesseract tại **line 25** trong `knowledge.py`

## Sử dụng

### 1. Xây dựng vector database và upload lên Pinecone

```bash
pip install -r requirements.txt
python knowledge.py
```

Vector database sẽ được upload lên Pinecone cloud.

### 2. Chạy MCP server

```bash
uv run mcp dev main.py
```

## Cấu trúc project

```
rag-server/
├── main.py              # MCP server tools
├── knowledge.py         # RAG utilities với Pinecone integration
├── requirements.txt     # Python dependencies
├── ghidra_docs/         # Thư mục chứa PDF documents
└── README.md            # File hướng dẫn này
```

## Lưu ý

- Vector database được lưu trên Pinecone cloud, không lưu local
- Sử dụng embedding model: `sentence-transformers/all-mpnet-base-v2` qua HuggingFace API
- Pinecone free tier: 1 index với 100K vectors
