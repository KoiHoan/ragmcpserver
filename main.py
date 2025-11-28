"""
FastMCP quickstart example.

cd to the `examples/snippets/clients` directory and run:
    uv run server fastmcp_quickstart stdio
"""
from typing import List, Dict
from mcp.server.fastmcp import FastMCP
from knowledge import get_knowledge_base
from prompts import (
   prompt_analyze_current_function,
prompt_analyze_current_file,
prompt_refactor_current_function,
prompt_refactor_entire_file
)

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
    return f"*** This is response: {text} ***"

@mcp.tool()
def query_knowledge(query: str, k: int = 5) -> List[Dict[str, str]]:
    """Query the knowledge base for relevant chunks
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
def query_knowledge_with_scores(query: str, k: int = 5) -> List[Dict[str, str]]:
    """Query the knowledge base with similarity scores
    """
    try:
        # Limit k to avoid overload
        k = min(max(1, k), 20)
        
        kb = get_knowledge_base()
        
        # Try to load existing DB first
        try:
            kb.load_vector_db()
        except ValueError:
            kb.build_vector_db()
        
        results = kb.query_with_scores(query, k=k)
        
        return results
    except Exception as e:
        return [{"error": f"Failed to query knowledge base: {str(e)}"}]

@mcp.tool()
def add_knowledge_text(text: str, source_name: str = "manual_entry") -> Dict[str, str]:
    """Add text content directly to knowledge base (for conclusions, notes, analysis results)
    """
    try:
        if not text or not text.strip():
            return {"status": "error", "message": "Text content is empty"}
        
        kb = get_knowledge_base()
        result = kb.add_text_to_db(text_content=text, source_name=source_name)
        
        return result
    except Exception as e:
        return {"status": "error", "message": f"Failed to add text: {str(e)}"}

@mcp.tool()
def get_knowledge_info() -> Dict[str, str]:
    """Get information about the knowledge base (index name, status)

    """
    try:
        kb = get_knowledge_base()
        info = kb.get_db_info()
        return info
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Add a dynamic greeting resource
# @mcp.resource("greeting://{name}")
# def get_greeting(name: str) -> str:
#     """Get a personalized greeting"""
#     return f"Hello, {name}!"


# Add a prompt
# @mcp.prompt()
# def greet_user(name: str, style: str = "friendly") -> str:
#     """Generate a greeting prompt"""
#     styles = {
#         "friendly": "Please write a warm, friendly greeting",
#         "formal": "Please write a formal, professional greeting",
#         "casual": "Please write a casual, relaxed greeting",
#     }

#     return f"{styles.get(style, styles['friendly'])} for someone named {name}."


@mcp.prompt()
def analyze_current_function() -> str:
    """Perform a full security review of the current function in the QNX module."""
    return prompt_analyze_current_function()

@mcp.prompt()
def analyze_current_file() -> str:
    """Perform a full security review of all functions in the current QNX module."""
    return prompt_analyze_current_file()

@mcp.prompt()
def refactor_current_function() -> str:
    """Refactor the current function using the exact workflow below."""
    return prompt_refactor_current_function()

@mcp.prompt()
def refactor_entire_file() -> str:
    """Refactor the entire file using the exact workflow below."""
    return prompt_refactor_entire_file()


# Entry point for MCP server
if __name__ == "__main__":
    mcp.run()
