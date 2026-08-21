from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from .database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String, nullable=False)

    file_path = Column(String, nullable=False)

    content_type = Column(String)

    file_size = Column(Integer)

    status = Column(String, default="uploaded")

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )