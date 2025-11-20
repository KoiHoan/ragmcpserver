Chạy trên 1 folder khác

uv init rag-server
cd rag-server
uv add "mcp[cli]"
pip install "mcp[cli]"

Copy main.py, knowledge.py và folder ghidra_docs vào folder mới
Lấy api key từ Huggingface (free) thay line 21
Tải tesseract OCR đổi path line 23

python knowledge.py
uv run mcp dev server.py
