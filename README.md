# Guard Owl Chat API

Demo Chat Application.

Current capabilities:
- answer generic questions a security guard might ask
- mock implementation of retrieving schedule
- mock implementation of contacting support

setup: 
- `uv sync`
how to run
`fastapi dev main.py`

things used:
- uv (package manager)
- FastAPI
- Pydantic AI

Example cURL request: 
```
curl -X 'POST' \
  'http://127.0.0.1:8000/chat' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "I need to call support. What'\''s the number?"
}'
```
