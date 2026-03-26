from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


''' 
It creates the base class for all your SQLAlchemy ORM models.
SQLAlchemy’s docs describe this exact pattern as the standard modern declarative style: 
you create a Base class by subclassing DeclarativeBase, and then all mapped classes inherit from that base.

Instead of manually creating a table object somewhere else and then separately mapping it, you declare the model directly as a class.
SQLAlchemy calls this declarative mapping, and it is the typical modern ORM style.

and all your models inherit from that same base.
That gives your whole app:

one shared metadata collection
one shared registry of mapped classes
one place to add common behavior later

Without it:
- your models would not share the same metadata
- Base.metadata.create_all() would not know what tables exist
- SQLAlchemy would not treat your classes as part of the same declarative mapping system
'''