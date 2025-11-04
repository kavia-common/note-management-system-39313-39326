"""
Simple in-memory storage layer for notes with basic persistence to JSON file.

This module provides a NotesStore class that maintains notes in memory and
optionally persists them to a JSON file between restarts. It is designed to be
thread-safe for typical Flask dev server usage, but for production use a real
database is recommended.
"""
from __future__ import annotations

import json
import os
import threading
import time
from typing import Dict, List, Optional, Tuple


class StorageError(Exception):
    """Raised when storage operations fail."""


class NotesStore:
    """
    A simple storage layer for notes with file-backed persistence.

    Each note is represented as:
    {
        "id": int,
        "title": str,
        "content": str,
        "created_at": float (epoch seconds),
        "updated_at": float (epoch seconds)
    }
    """

    def __init__(self, persistence_path: Optional[str] = None) -> None:
        self._lock = threading.RLock()
        self._notes: Dict[int, Dict] = {}
        self._next_id: int = 1
        self._persistence_path = persistence_path
        self._load_from_disk()

    def _load_from_disk(self) -> None:
        """Load notes from disk if a persistence path is set and file exists."""
        if not self._persistence_path:
            return
        if not os.path.exists(self._persistence_path):
            return
        try:
            with open(self._persistence_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            notes = data.get("notes", [])
            self._notes = {int(n["id"]): n for n in notes if "id" in n}
            # Determine next id
            self._next_id = (max(self._notes.keys()) + 1) if self._notes else 1
        except Exception as exc:
            # Do not crash app on load failure, just start fresh
            raise StorageError(f"Failed to load notes from disk: {exc}") from exc

    def _save_to_disk(self) -> None:
        """Persist notes to disk as JSON if persistence is enabled."""
        if not self._persistence_path:
            return
        directory = os.path.dirname(self._persistence_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        try:
            with open(self._persistence_path, "w", encoding="utf-8") as f:
                json.dump({"notes": list(self._notes.values())}, f, ensure_ascii=False, indent=2)
        except Exception as exc:
            raise StorageError(f"Failed to persist notes to disk: {exc}") from exc

    # PUBLIC_INTERFACE
    def list_notes(self, page: int = 1, page_size: int = 50) -> Tuple[List[Dict], Dict]:
        """
        Return a paginated list of notes and pagination metadata.

        Returns:
            (notes, meta) where meta = {
                "total": int, "total_pages": int, "page": int,
                "previous_page": Optional[int], "next_page": Optional[int]
            }
        """
        with self._lock:
            items = sorted(self._notes.values(), key=lambda n: n["id"])
            total = len(items)
            page_size = max(1, min(100, page_size))
            total_pages = ((total - 1) // page_size) + 1 if total > 0 else 1
            page = max(1, min(page, total_pages))
            start = (page - 1) * page_size
            end = start + page_size
            subset = items[start:end]
            meta = {
                "total": total,
                "total_pages": total_pages,
                "page": page,
                "previous_page": page - 1 if page > 1 else None,
                "next_page": page + 1 if page < total_pages else None,
            }
            return subset, meta

    # PUBLIC_INTERFACE
    def get_note(self, note_id: int) -> Optional[Dict]:
        """Return a single note by id or None if not found."""
        with self._lock:
            return self._notes.get(int(note_id))

    # PUBLIC_INTERFACE
    def create_note(self, title: str, content: str) -> Dict:
        """Create a note and return it."""
        now = time.time()
        with self._lock:
            note_id = self._next_id
            self._next_id += 1
            note = {
                "id": note_id,
                "title": title,
                "content": content,
                "created_at": now,
                "updated_at": now,
            }
            self._notes[note_id] = note
            self._save_to_disk()
            return note

    # PUBLIC_INTERFACE
    def update_note(self, note_id: int, title: Optional[str] = None, content: Optional[str] = None) -> Optional[Dict]:
        """Update a note in-place; returns updated note or None if not found."""
        with self._lock:
            note = self._notes.get(int(note_id))
            if not note:
                return None
            updated = False
            if title is not None:
                note["title"] = title
                updated = True
            if content is not None:
                note["content"] = content
                updated = True
            if updated:
                note["updated_at"] = time.time()
                self._save_to_disk()
            return note

    # PUBLIC_INTERFACE
    def delete_note(self, note_id: int) -> bool:
        """Delete a note by id; returns True if deleted, False if not found."""
        with self._lock:
            existed = int(note_id) in self._notes
            if existed:
                del self._notes[int(note_id)]
                self._save_to_disk()
            return existed
