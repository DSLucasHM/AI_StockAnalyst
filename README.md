
# Stock Research Web Application 

This project performs stock research and generates detailed reports. It has been restructured for a cleaner directory organization, with the Flask application logic and main business components placed inside a `src` directory.

## Web Interface Features

-   **Stock Symbols Input:** Allows users to input multiple stock symbols.
-   **Report Generation:** Processes the research and generates a Markdown report.
-   **Report Display:** Displays the report (converted to HTML) in the interface.
-   **Report Download:** Allows downloading the original report in Markdown.
-   **Responsive Design:** Adapted for both desktop and mobile devices.

## Project Structure

```
/stock_research/
  ├── src/                                
  │   ├── __init__.py
  │   ├── config.py                        
  │   ├── app/                            
  │   │   ├── __init__.py
  │   │   ├── main.py                     
  │   │   ├── templates/                  
  │   │   │   └── index.html
  │   │   ├── static/                     
  │   │   │   └── css/
  │   │   └── reports/                    
  │   ├── core/                           
  │   │   ├── __init__.py
  │   │   ├── agent/
  │   │   │   ├── __init__.py
  │   │   │   └── graph.py
  │   │   ├── nodes.py
  │   │   └── state.py
  │   ├── utils/                           
  │   │   ├── __init__.py      
  │   │   └── search.py
  │   └── retriever/                      
  │       ├── __init__.py
  │       └── search.py
  ├── Dockerfile
  ├── requirements.txt
  ├── .gitignore
  ├── README.md                           
  └── .env_example
```

## How to Run with Docker (Recommended)

1.  **Build the Docker Image:**
    In the project's root directory (`stock_analyst`), run:
    ```bash
    docker build -t stock-research-app-final .
    ```

2.  **Run the Docker Container:**
    Make sure you have a `.env` file in the root of the project (`stock_analyst`) with your API keys.
    ```bash
    docker run -p 5000:5000 -v "$(pwd)/src/app/reports:/app/src/app/reports" --env-file .env stock-research-app-final
    ```
    -   `-p 5000:5000`: Maps host port to container port.
    -   `-v "$(pwd)/src/app/reports:/app/src/app/reports"`: (Optional but recommended) Maps the local reports directory (`src/app/reports/` on your machine) to the corresponding container directory. Create `src/app/reports` locally if it does not exist (`mkdir -p src/app/reports`).
    -   `--env-file .env`: Loads environment variables from the `.env` file.

    > ⚠️ **Note:** When you're done using the application, stop the container using `docker ps` to find the container ID and `docker stop <container_id>` to shut it down.

3.  **Access the Application:**
    Open your browser and go to `http://localhost:5000`.

## How to Run Locally for Development (Without Docker)

1.  **Create and Activate a Virtual Environment:**
    In the root directory (`stock_analyst`):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Linux/macOS
    # venv\Scriptsctivate    # Windows
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set Up Environment Variables:**
    Copy `.env_example` to `.env` and fill in the API keys.

4.  **Run the Flask Application:**
    The `PYTHONPATH` should include the project's root directory so that `from src...` works. `src/app/main.py` tries to adjust `sys.path` for this.
    From the root directory (`stock_analyst`):
    ```bash
    python src/app/main.py
    ```

5.  **Access the Application:**
    Open your browser and go to `http://localhost:5000`.

## Considerations

-   **API Keys:** Essential for operation, set them in the `.env` file (e.g., `TAVILY_API_KEY`, `OPENAI_API_KEY`).
-   **Synchronous Processing:** Report generation is synchronous.
-   **Docker Validation:** Due to limitations in the AI development environment, Docker build and execution could not be tested directly. It is recommended that users test these steps in their local environment.


Referencess:
https://scoras.com
https://tavily.com