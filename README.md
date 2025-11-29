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
```

## Cập nhật Documents (Chỉ khi cần)

**Cách update:**

- Thêm file PDF/TXT mới vào `ghidra_docs/` (xóa các file có sẵn trong folder, có imple deduplicate nhưng ko đảm bảo)

```bash
# 1. Thêm/xóa files trong ghidra_docs/
# builder.py tự động scan tất cả .pdf và .txt trong folder

# 2. Rebuild vector database
# Docker:
docker run --rm -i --env-file .env rag-mcp-server:latest python /app/builder.py

# Local (nếu không dùng Docker):
python builder.py
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

# Linux: Add user to docker group + restart system
sudo usermod -aG docker $USER
# Then logout/login or restart system

# Verify docker permission
groups | grep docker
docker ps
```

## Troubleshooting

### Linux: Permission denied - Docker

```bash
# Check if user in docker group
groups | grep docker

# If not in group, add and restart
sudo usermod -aG docker $USER
# MUST logout/login or restart system

# Quick fix (not permanent)
sudo chmod 666 /var/run/docker.sock
```

### Test Docker manually

```bash
# Test Docker works
docker ps

# Test script directly
./run_mcp_in_docker.sh

# Test container (should wait for input, Ctrl+C to exit)
docker run --rm -i --env-file .env rag-mcp-server:latest python -u /app/main.py
```

### Server không hiện trong Claude Desktop

```bash
# Check script executable
ls -la run_mcp_in_docker.sh

# Test image exists
docker images | grep rag-mcp-server

# Rebuild if needed
docker build -t rag-mcp-server:latest .
```
