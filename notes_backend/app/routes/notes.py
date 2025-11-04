from __future__ import annotations

from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from app.schemas.notes import (
    NoteSchema,
    NoteCreateSchema,
    NoteUpdateSchema,
)
from app.storage.notes_store import NotesStore, StorageError

blp = Blueprint(
    "Notes",
    "notes",
    url_prefix="/notes",
    description="CRUD operations for notes",
)


def get_store() -> NotesStore:
    """
    Retrieve a global store instance. In this simple setup, we attach it to
    the Flask app instance to ensure a single store per process.
    """
    from flask import current_app

    if not hasattr(current_app, "_notes_store"):
        # Use a JSON file in the container to persist notes between restarts
        current_app._notes_store = NotesStore(persistence_path="/tmp/notes_store.json")
    return current_app._notes_store


@blp.route("/")
class NotesCollection(MethodView):
    """
    Collection endpoint for listing and creating notes.
    """

    @blp.response(200, schema=NoteSchema(many=True), description="List notes")
    @blp.doc(summary="List notes", description="Retrieve a paginated list of notes.")
    def get(self):
        """
        List notes with optional pagination.

        Query Parameters:
            - page: int (default 1)
            - page_size: int (default 50, max 100)

        Returns:
            JSON array of notes with X-Pagination-* headers (metadata also returned in a `meta` envelope if `accept=application/json+meta` not needed here).
        """
        page = request.args.get("page", type=int) or 1
        page_size = request.args.get("page_size", type=int) or 50
        store = get_store()
        notes, meta = store.list_notes(page=page, page_size=page_size)

        # Attach pagination headers for clients that use headers
        from flask import make_response, jsonify

        response = make_response(jsonify(notes), 200)
        response.headers["X-Pagination-Total"] = str(meta["total"])
        response.headers["X-Pagination-Total-Pages"] = str(meta["total_pages"])
        response.headers["X-Pagination-Page"] = str(meta["page"])
        response.headers["X-Pagination-Prev-Page"] = str(meta["previous_page"])
        response.headers["X-Pagination-Next-Page"] = str(meta["next_page"])
        return response

    @blp.arguments(NoteCreateSchema)
    @blp.response(201, NoteSchema, description="Created note")
    @blp.doc(summary="Create note", description="Create a new note with title and content.")
    def post(self, json_data):
        """
        Create a note.

        Body:
            NoteCreateSchema: {title, content}

        Returns:
            The created note.
        """
        store = get_store()
        try:
            note = store.create_note(title=json_data["title"], content=json_data["content"])
            return note
        except StorageError as exc:
            abort(500, message=str(exc))


@blp.route("/<int:note_id>")
class NoteItem(MethodView):
    """
    Item endpoint for retrieving, updating, and deleting a single note.
    """

    @blp.response(200, NoteSchema, description="Single note")
    @blp.doc(summary="Get note", description="Retrieve a note by ID.")
    def get(self, note_id: int):
        store = get_store()
        note = store.get_note(note_id)
        if not note:
            abort(404, message="Note not found")
        return note

    @blp.arguments(NoteUpdateSchema)
    @blp.response(200, NoteSchema, description="Updated note")
    @blp.doc(summary="Update note", description="Update fields of a note by ID.")
    def patch(self, json_data, note_id: int):
        store = get_store()
        if not json_data:
            abort(400, message="No fields provided to update")
        try:
            note = store.update_note(note_id, title=json_data.get("title"), content=json_data.get("content"))
            if not note:
                abort(404, message="Note not found")
            return note
        except StorageError as exc:
            abort(500, message=str(exc))

    @blp.response(204, description="Note deleted")
    @blp.doc(summary="Delete note", description="Delete a note by ID.")
    def delete(self, note_id: int):
        store = get_store()
        try:
            deleted = store.delete_note(note_id)
            if not deleted:
                abort(404, message="Note not found")
            return "", 204
        except StorageError as exc:
            abort(500, message=str(exc))
