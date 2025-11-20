# RAG MCP Server

MCP Server với RAG (Retrieval-Augmented Generation) để truy vấn tài liệu PDF.

## Yêu cầu

- Python 3.12+
- Tesseract OCR
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

**Huggingface API Key:**

- Đăng ký tài khoản miễn phí tại [Huggingface](https://huggingface.co/)
- Lấy API key và thay vào **line 21** trong `knowledge.py`

**Tesseract OCR:**

- Tải và cài đặt [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- Cập nhật đường dẫn Tesseract tại **line 23** trong `knowledge.py`

## Sử dụng

### 1. Xây dựng vector database từ PDF

```bash
python knowledge.py
```

### 2. Chạy MCP server

```bash
uv run mcp dev main.py
```

## Cấu trúc project

```
rag-server/
├── main.py           # MCP server tools
├── knowledge.py      # RAG utilities và vector DB
├── ghidra_docs/      # Thư mục chứa PDF documents
└── README.md         # File hướng dẫn này
```
