# Company AI Setup

Company AI uses OpenAI Responses with hosted file search and web search, plus read-only tools for company search, comparison, analytics, and CSV export.

## Configuration

Install backend dependencies with `pip install -r backend_api/requirements.txt`. Set `OPENAI_API_KEY` in the backend process environment. The optional `OPENAI_CHAT_MODEL` defaults to `gpt-4.1`, which supports the web search domain filters used by the assistant.

For local PowerShell development, set the key in the shell before starting FastAPI:

```powershell
$env:OPENAI_API_KEY = "<your OpenAI API key>"
```

For Render, add `OPENAI_API_KEY` as a secret environment variable on the backend service. Do not put the key in `config.json`, `render.yaml`, or source control.

## Usage

1. Sign in and open the **Company AI** tab.
2. Choose **Index my records**. The service builds a per-user OpenAI vector store from that user's uploaded and processed company records.
3. Ask questions, compare companies, or request a summary. Search tools only read rows uploaded by the signed-in username.
4. Export tool-produced rows as CSV from the assistant response.
5. Use **Refresh index** after uploading or processing additional company data. **Delete index** removes the hosted OpenAI vector store and its app-side reference; it does not delete source records from PostgreSQL.

Public web search is restricted to domains found in that user's processed company website fields. Web URLs and file-search citations are shown below responses.

## Data Handling

Indexing transmits uploaded and processed company data to OpenAI and stores it in that user's OpenAI vector store until the index is refreshed or deleted. Responses are requested with `store=False`; this does not remove the separate vector store. Only index company data approved for external processing. The model receives retrieved records and public web results as untrusted evidence; its application tools are read-only and do not execute arbitrary SQL or modify company records.