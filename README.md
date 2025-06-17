# LinkedIn MCP Server

This project provides an MCP server that enables posting text, images, and videos to LinkedIn, generating images with OpenAI, searching the web with Brave, and executing SQL queries on a local database.

## Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (for running and installing dependencies)
- A LinkedIn Developer App (for API credentials)
- Required environment variables set in a `.env` file (see below)

## Setup

1. **Clone the repository and navigate to the project directory.**

2. **Create a `.env` file** in the project root with the following variables (see `.env` for example values):

    ```
    CLIENT_ID=your_linkedin_client_id
    CLIENT_SECRET=your_linkedin_client_secret
    REDIRECT_URI=http://localhost:8000/callback
    ACCESS_TOKEN=
    AUTHOR_URN=
    FOLDER_PATH=~/Desktop/Experiment/MCP
    OPENAI_API_KEY=your_openai_api_key
    BRAVE_API_KEY=your_brave_api_key
    ```

3. **Authenticate with LinkedIn**  
   Run the following command to sign in and populate `ACCESS_TOKEN` and `AUTHOR_URN` in your `.env`:

    ```sh
    python oauth.py
    ```

   This will open a browser window for LinkedIn login and update your `.env` automatically.

## Running the MCP Server

To install and run the MCP server (so it can be added to Claude Desktop), use:

```sh
uv run mcp install server.py --with requests --with openai -f .env
```

- This command installs dependencies and starts the server using your environment variables.

## Features

- **Post to LinkedIn**: Text, image, and video posts.
- **Generate Images**: Use OpenAI's image generation API.
- **Web Search**: Search the web using Brave Search API.
- **Database Access**: Run SQL queries on a local SQLite database.

## Notes

- Ensure all required API keys and tokens are set in `.env`.
- The first time you run `oauth.py`, it will guide you through LinkedIn authentication.
- The MCP server exposes tools for integration with Claude Desktop.

---

For more details, see the source files:

- [server.py](server.py)
- [client.py](client.py)
- [oauth.py](oauth.py)
-