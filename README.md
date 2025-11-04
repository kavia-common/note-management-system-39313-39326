# note-management-system-39313-39326

Notes Backend (Flask)
- REST API with CRUD endpoints for notes.
- OpenAPI docs available at /docs/swagger-ui
- Base URL (preview): see running container info. Typically http://localhost:3001

Quickstart
1) Install dependencies
   pip install -r notes_backend/requirements.txt
2) Run the server
   cd notes_backend && python run.py

Environment
- PORT: Port to bind (default 3001)
- HOST: Interface to bind (default 0.0.0.0)
- FLASK_DEBUG: true/false to enable debug (default false)

Endpoints
- GET    /           Health status
- GET    /notes      List notes (page, page_size optional)
- POST   /notes      Create note {title, content}
- GET    /notes/<id> Get note by id
- PATCH  /notes/<id> Update note fields
- DELETE /notes/<id> Delete note

Example curl
- Health
  curl -s http://localhost:3001/
- Create
  curl -s -X POST http://localhost:3001/notes -H "Content-Type: application/json" -d '{"title":"First","content":"Hello"}'
- List
  curl -s http://localhost:3001/notes
- Get
  curl -s http://localhost:3001/notes/1
- Update
  curl -s -X PATCH http://localhost:3001/notes/1 -H "Content-Type: application/json" -d '{"content":"Updated"}'
- Delete
  curl -s -X DELETE http://localhost:3001/notes/1 -i

OpenAPI Docs
- Visit: http://localhost:3001/docs/swagger-ui