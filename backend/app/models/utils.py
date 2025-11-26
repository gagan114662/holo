"""
Database utility types for cross-database compatibility
"""
import json
from sqlalchemy import TypeDecorator, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB
import uuid


class GUID(TypeDecorator):
    """
    Platform-independent GUID type.
    Uses PostgreSQL's UUID type when available, otherwise stores as String(36).
    Works with both PostgreSQL and SQLite.
    """
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)


class JSONType(TypeDecorator):
    """
    Platform-independent JSON type.
    Uses PostgreSQL's JSONB when available, otherwise stores as Text with JSON serialization.
    """
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_JSONB())
        else:
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, str):
                return json.loads(value)
            return value


class ArrayType(TypeDecorator):
    """
    Platform-independent ARRAY type.
    Uses PostgreSQL's ARRAY when available, otherwise stores as JSON array in Text.
    """
    impl = Text
    cache_ok = True

    def __init__(self, item_type=None):
        super().__init__()
        self.item_type = item_type

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            from sqlalchemy.dialects.postgresql import ARRAY
            return dialect.type_descriptor(ARRAY(self.item_type or String))
        else:
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            # Convert UUIDs to strings for JSON serialization
            processed = []
            for item in value:
                if isinstance(item, uuid.UUID):
                    processed.append(str(item))
                else:
                    processed.append(item)
            return json.dumps(processed)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, str):
                return json.loads(value)
            return value
