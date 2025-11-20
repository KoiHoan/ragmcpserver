"""
FastMCP quickstart example.

cd to the `examples/snippets/clients` directory and run:
    uv run server fastmcp_quickstart stdio
"""
from typing import List, Dict
from mcp.server.fastmcp import FastMCP
from knowledge import get_knowledge_base
# Create an MCP server
mcp = FastMCP("Demo")


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b



# Add a formatting tool that takes a string and returns a formatted response
@mcp.tool()
def format_response(text: str) -> str:
    """Format the incoming text into the standardized response string."""
    return "*** This is response: {text} ***"

@mcp.tool()
def query_knowledge(query: str, k: int = 5) -> List[Dict[str, str]]:
    """Query the knowledge base for relevant chunks
    
    Args:
        query: Search query text
        k: Number of results to return (1-20)
        
    Returns:
        List of dicts with rank, content, source, page
    """
    try:
        # Limit k to avoid overload
        k = min(max(1, k), 20)
        
        kb = get_knowledge_base()
        
        # Try to load existing DB first, if not found it will build
        try:
            kb.load_vector_db()
        except ValueError:
            # DB doesn't exist, try to build it
            kb.build_vector_db()
        
        results = kb.query_relevant_chunks(query, k=k)
        
        return results
    except Exception as e:
        return [{"error": f"Failed to query knowledge base: {str(e)}"}]

@mcp.tool()
def add_knowledge_text(text: str) -> Dict[str, str]:
    """Add text content directly to knowledge base (for conclusions, notes, analysis results)
    
    Args:
        text: Text content to add
        source_name: Label/name for this entry (e.g. "conclusion", "my_analysis")
        
    Returns:
        Dict with status and info
    """
    try:
        if not text or not text.strip():
            return {"status": "error", "message": "Text content is empty"}
        
        kb = get_knowledge_base()
        result = kb.add_text_to_db(text_content=text, source_name="manual_entry")
        
        return result
    except Exception as e:
        return {"status": "error", "message": f"Failed to add text: {str(e)}"}

@mcp.tool()
def get_knowledge_info() -> Dict[str, str]:
    """Get information about the knowledge base (total chunks, location)
    
    Returns:
        Dict with database stats
    """
    try:
        kb = get_knowledge_base()
        info = kb.get_db_info()
        return info
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


# Add a prompt
@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt"""
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }

    return f"{styles.get(style, styles['friendly'])} for someone named {name}."