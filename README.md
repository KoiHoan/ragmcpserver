# RAG MCP Server - Quick Start

## Yêu cầu

- Docker Desktop
- Pinecone API key - [Sign up](https://app.pinecone.io/)
- OpenAI API key - [Get key](https://platform.openai.com/api-keys)
- Claude Desktop

## Cài đặt (Docker)

```bash
# 1. Clone repository
git clone https://github.com/KoiHoan/ragmcpserver.git
cd mcp-server-demo

# 2. Tạo .env file
copy .env.example .env  # Windows
cp .env.example .env    # Linux/macOS

# Chỉnh sửa .env:
# PINECONE_API_KEY=your-key
# OPENAI_API_KEY=your-key
# PINECONE_INDEX_NAME=rag-mcp-server

# 3. Build Docker image
docker build -t rag-mcp-server:latest .

# 4*. Build vector database from documents (DONT RUN)
d.o.c.k.e.r run --rm -i --env-file .env rag-mcp-server:latest python /app/builder.py
```

## Kết nối Claude Desktop

**Windows:**

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "rag-knowledge": {
      "command": "C:\\Users\\YourUsername\\path\\to\\mcp-server-demo\\run_mcp_in_docker.bat"
    }
  }
}
```

**Linux/macOS:**

Edit `~/.config/Claude/claude_desktop_config.json` (Linux) hoặc `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "rag-knowledge": {
      "command": "/absolute/path/to/mcp-server-demo/run_mcp_in_docker.sh"
    }
  }
}
```

```bash
# Linux/macOS: Make script executable
chmod +x run_mcp_in_docker.sh
```

**Restart Claude Desktop:**

1. Tắt hoàn toàn từ System Tray (Windows) hoặc Dock (macOS)
2. Mở lại Claude Desktop
3. Click 🔌 icon → Verify `rag-knowledge` server active
