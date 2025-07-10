## How to Setup

1. **Install uv (if you don't have it):**
   ```sh
   pip install uv
   ```

2. **Initialize the environment:**
   ```sh
   uv init
   ```

3. **Create the virtual environment:**
  - On Windows (Terminal):
     ```
     uv venv hackathon
     .venv/Scripts/activate
     ```
4. **Install the packages:**
    ```
     uv install -r requirements.txt
     ```
5. **Run the FastAPI app:**
   ```sh
   uvicorn app.main:app --reload
   ```

6. **Run the MCP server:**
   ```sh
   python -m mcp_server.server
   ```

