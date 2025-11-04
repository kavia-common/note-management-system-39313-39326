"""
Schemas for Note entities and requests using marshmallow.
"""
from __future__ import annotations

from marshmallow import Schema, fields, validate, EXCLUDE


class PaginationMetaSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    total = fields.Int(required=True, description="Total number of items")
    total_pages = fields.Int(required=True, description="Total number of pages")
    page = fields.Int(required=True, description="Current page number")
    previous_page = fields.Int(allow_none=True, description="Previous page number if available")
    next_page = fields.Int(allow_none=True, description="Next page number if available")


class NoteSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Int(required=True, description="Unique note identifier")
    title = fields.Str(required=True, validate=validate.Length(min=1, max=256), description="Note title")
    content = fields.Str(required=True, validate=validate.Length(min=0), description="Note content")
    created_at = fields.Float(required=True, description="Creation timestamp (epoch seconds)")
    updated_at = fields.Float(required=True, description="Last updated timestamp (epoch seconds)")


class NoteCreateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    title = fields.Str(required=True, validate=validate.Length(min=1, max=256), description="Note title")
    content = fields.Str(required=True, validate=validate.Length(min=0), description="Note content")


class NoteUpdateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    title = fields.Str(required=False, validate=validate.Length(min=1, max=256), description="Note title")
    content = fields.Str(required=False, validate=validate.Length(min=0), description="Note content")
