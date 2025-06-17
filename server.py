# server.py
from mcp.server.fastmcp import FastMCP
from utils.client import LinkedInClient
from utils.config import AUTHOR_URN
import os
from utils.gpt_image import generate_and_save_image
from utils.brave import brave_search, extract_titles_and_descriptions
import sqlite3
import json

BASE_DIR = os.path.dirname(__file__)
DB_PATH  = os.path.join(BASE_DIR, "data.db")

# Create an MCP server
mcp = FastMCP("LinkedIn MCP Server")

AUTHOR_URN   = os.getenv("AUTHOR_URN")

#Creating a LinkedIn client instance
client = LinkedInClient()

# LinkedIn Post tool
@mcp.tool()
def create_post(content:str) -> str:
    """Create a text-only LinkedIn post.
    Returns the new post's URL (e.g. 'urn:li:share:12345').
    """
    # Ensure the content is not empty
    if not content:
        raise ValueError("Content cannot be empty")

    # Call the LinkedIn API to create a post
    new_urn = client.post_text(AUTHOR_URN, content)
    
    URL = f"https://www.linkedin.com/feed/update/{new_urn}"
    # Return the new post's URN
    return {"url" : URL}

# LinkedIn Image Post tool
@mcp.tool()
def create_image_post(content:str, image_path:str) -> str:
    """Create a LinkedIn post with an image.
    Returns the new post's URL (e.g. 'urn:li:share:12345').
    """
    # Ensure the content is not empty
    if not content:
        raise ValueError("Content cannot be empty")

    

    # Call the LinkedIn API to create a post with an image
    new_urn = client.post_image(AUTHOR_URN, content, [image_path])
    
    URL = f"https://www.linkedin.com/feed/update/{new_urn}"
    # Return the new post's URN
    return {"url" : URL}

# LinkedIn Video Post tool
@mcp.tool()
def create_video_post(content:str, video_path:str) -> str:
    """Create a LinkedIn post with a video.
    Returns the new post's URL (e.g. 'urn:li:share:12345').
    """
    # Ensure the content is not empty
    if not content:
        raise ValueError("Content cannot be empty")


    # Call the LinkedIn API to create a post with a video
    new_urn = client.post_video(AUTHOR_URN, content, video_path)
    
    URL = f"https://www.linkedin.com/feed/update/{new_urn}"
    # Return the new post's URN
    return {"url" : URL}

#Generate an image using a promt
@mcp.tool()
def generate_image(prompt:str, quality: str = "medium",
    size: str = "1536x1024") -> str:
    """Generate an image using a prompt, and optionally take quality and size of a image and save it locally.
    Returns the path to the saved image file.
    """
    # Ensure the prompt is not empty
    if not prompt:
        raise ValueError("Prompt cannot be empty")

    # Call the openai API to create an image
    new_path = generate_and_save_image(prompt, quality=quality, size=size)

    # Extract file name from the path
    file_name = os.path.basename(new_path)
    
    return {"path" : new_path, "file_name" : file_name}

# Search the web using Brave
@mcp.tool()
def search_web(query: str, count: int = 5, search_lang: str = "en") -> dict:
    """Perform a Brave Web Search and return the JSON response.
    Args:
        query (str): The search query.
        count (int): Number of search results to return.
        search_lang (str): ISO 639-1 language code (default: "en").
    Returns:
        dict: Parsed JSON response from Brave Search API.
    """
    # Ensure the query is not empty
    if not query:
        raise ValueError("Query cannot be empty")

    # Call the Brave API to perform a web search
    results = brave_search(query, count=count, search_lang=search_lang)

    final_results = extract_titles_and_descriptions(results)
    # Return the parsed results
    return final_results

# Database Query tool
@mcp.tool()
def execute_db_query(query: str) -> str:
    """
    Executes any SQL on data.db.
    Returns a JSON-stringified dict:
      - { "success": true }
      - { "success": true, "rows": [ {...}, {...} ] }
      - { "success": false, "error": "..." }
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(query)

            if query.strip().lower().startswith("select"):
                rows = [dict(r) for r in cur.fetchall()]
                return json.dumps({"success": True, "rows": rows})

            conn.commit()
            return json.dumps({"success": True})

    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})
