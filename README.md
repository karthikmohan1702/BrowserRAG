# Browser RAG Project

## BrowserRAG Demo

https://github.com/user-attachments/assets/01b10db9-f36b-45c0-a509-79aa18865a8f

## Description

This project implements a **Browser RAG** system. RAG, or Retrieval-Augmented Generation, is an AI framework designed to improve the quality and reliability of Large Language Model (LLM) responses by retrieving relevant information from an external knowledge base before generating an answer. This approach helps to ground the LLM's output in factual, up-to-date data, reducing inaccuracies or "hallucinations" and allowing the AI to leverage specific information beyond its initial training data.

In this project, the concept is applied within the browser context. A Chrome Extension acts as the interface, allowing users to build a personal knowledge base by indexing the content of web pages they visit. This indexed content becomes the external knowledge source. When a user asks a question via the extension, the system retrieves the most relevant text chunks from the indexed pages (using semantic search) and provides this context to the LLM (Gemini) to generate a detailed, factually grounded answer. This provides a powerful way to create a personal, searchable, and queryable archive of web content relevant to the user.

To make the content ingestion process more robust and autonomous, the system integrates with a **Markitdown MCP server**. Markitdown is a tool that converts various document types (like web pages, PDFs, Word documents) into clean Markdown format, which is ideal for LLM processing. The Markitdown MCP server exposes this conversion capability as an external tool via an API, following the Model Context Protocol (MCP). The backend agent in this project can discover and call the `convert_to_markdown` tool on the MCP server. This automates the process of fetching and cleaning web content before it's chunked and indexed, allowing the agent to handle different web page structures more effectively without needing the conversion logic built-in.

## Why Browser RAG? How It Helps

In today's information-rich online world, users often face challenges like:

* **Information Overload:** Drowning in tabs, articles, and resources found online.
* **Scattered Knowledge:** Useful information bookmarked or noted across different places, making it hard to consolidate.
* **Difficulty Recalling:** Forgetting where specific information was found or struggling to remember key details from past browsing.
* **Inefficient Re-Searching:** Wasting time trying to re-find pages or re-google information previously encountered.

This Browser RAG plugin addresses these needs by helping users:

* **Build Personal Expertise:** Create a curated, centralized knowledge base from web content *you* select as important.
* **Improve Recall:** Easily find specific information you've previously logged using natural language queries, leveraging semantic search instead of just keywords.
* **Deepen Understanding:** Ask clarifying questions and get AI-generated answers based *specifically* on the content you saved, enhancing comprehension.
* **Boost Productivity:** Quickly access relevant saved information and summaries directly within your browser, streamlining research and learning workflows.
* **Combat Information Fog:** Turn passive browsing into an active knowledge-building process, ensuring valuable online discoveries aren't lost.

## Features

* **Log Web Pages:** Index the textual content of any web page with a single click. Content is converted to Markdown via the Markitdown MCP server.
* **Summarize Pages:** Instantly generate an AI summary of any logged page.
* **Ask Questions:** Query your indexed content in natural language and receive answers with source references.
* **Semantic Search:** Find relevant information across all indexed content using semantic similarity.
* **Manage Indexed Pages:** View a list of indexed pages and delete entries directly from the extension popup.
* **Delete Pages:** Remove any indexed URL and all its associated content from your personal knowledge base, either from the extension popup or via the backend API.
* **Backend Health & Stats:** Check backend status and view FAISS index statistics.

## Benefits Over Traditional Methods

Compared to traditional bookmarking, note-taking, or manual web searching, this Browser RAG plugin offers several advantages:

* **Personalized Knowledge Base:** Build a searchable repository of content *you* find relevant, not just generic web results.
* **Semantic & Contextual Search:** Retrieve information by meaning, not just keywords, with answers grounded in your saved content.
* **Efficient Recall:** Quickly resurface details or summaries from previously indexed pages, reducing information overload and context switching.

## Technology Stack

* **Backend:** Python, FastAPI, Sentence Transformers (`nomic-ai/nomic-embed-text-v1`), FAISS, Gemini API
* **Frontend:** Chrome Extension API, JavaScript, HTML, CSS
* **Content Processing:** Markitdown MCP Server, FastMCP Client
* **Persistence:** FAISS index file (`faiss.index`), Chunk data file (`chunks.pkl`)

## Setup and Installation

### Backend

1.  **Environment:** Set up a Python environment.
2.  **Dependencies:** Install necessary Python packages (e.g., `fastapi`, `uvicorn`, `sentence-transformers`, `faiss-cpu` or `faiss-gpu`, `python-dotenv`, `requests`, `numpy`, `fastmcp`, `pydantic`).
3.  **API Key:** Obtain a Gemini API key and set it as an environment variable named `GEMINI_API_KEY` (e.g., in a `.env` file).
4.  **Markitdown MCP Server:** Ensure the Markitdown MCP server is running and accessible (the default client assumes `http://127.0.0.1:3001/sse`). See [Markitdown MCP documentation](https://github.com/microsoft/markitdown/tree/main/packages/markitdown-mcp) for setup instructions.
5.  **Run Backend:** Start the FastAPI application from the root directory using:

   ```sh
   uvicorn backend.agent:app --reload --host 0.0.0.0 --port 8000
   ```

   This ensures the backend is started with the correct module path after project reorganization.

### Chrome Extension

1.  **Clone/Download:** Place the `chrome_extension` folder on your local machine.
2.  **Backend URL:** Verify the `BACKEND_BASE` constant in `chrome_extension/popup.js` matches your running backend URL (default is `http://127.0.0.1:8000`). Optionally, use the Options page (`options.html`) to configure this, although the popup currently hardcodes it.
3.  **Load Extension:**
    * Open Chrome and navigate to `chrome://extensions/`.
    * Enable "Developer mode" (usually a toggle in the top right).
    * Click "Load unpacked".
    * Select the `chrome_extension` folder.

## Usage

1.  Navigate to a web page you want to interact with.
2.  Click the "Vector Store Assistant" (or "Browser RAG") icon in your Chrome toolbar to open the popup.
3.  **Log Page:** Click "Log Page" to fetch markdown via MCP, chunk, embed, and index the current page's content.
4.  **Summarize Page:** Click "Summarize Page" to get an AI summary (requires the page to be logged first).
5.  **Ask Questions:** Type a question about the indexed content into the text area and click "Ask". The results (answer and source URLs) will appear below.
6.  **Manage Pages:** Expand "My Indexed Pages" to see a list of URLs you've logged. Click the trash icon to remove a page from the index.
7.  **View Stats:** Click "Show Stats" to see details about the FAISS index.

## File Structure

```
Session_7/
├── backend/
│   ├── __init__.py
│   ├── agent.py
│   ├── action.py
│   ├── decision.py
│   ├── memory.py
│   └── .env
├── chrome_extension/
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.js
│   ├── popup.css
│   ├── content.js
│   ├── content.css
│   ├── options.html
│   └── icons/
│       ├── icon16.png
│       ├── icon48.png
│       └── icon128.png
├── README.md
├── requirements.txt
```

## Configuration

* **Backend API URL:** Currently hardcoded in `chrome_extension/popup.js` as `http://127.0.0.1:8000`. Can be made configurable via `options.html`.
* **Gemini API Key:** Must be set as the `GEMINI_API_KEY` environment variable for the backend.
* **MCP Server URL:** Hardcoded in `action.py` and `mcp_client.py` as `http://127.0.0.1:3001/sse`.
* **Embedding Model:** Set in `memory.py` (currently `nomic-ai/nomic-embed-text-v1`).
* **Chunk Size:** Defined in `memory.py`.

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FAISS: Facebook AI Similarity Search](https://github.com/facebookresearch/faiss)
- [Sentence Transformers](https://www.sbert.net/)
- [Gemini API (Google Generative Language)](https://ai.google.dev/gemini-api/docs)
- [Markitdown MCP](https://github.com/microsoft/markitdown/tree/main/packages/markitdown-mcp)
- [Model Context Protocol (MCP)](https://github.com/markitdown/model-context-protocol)
- [Chrome Extension Developer Guide](https://developer.chrome.com/docs/extensions/)
