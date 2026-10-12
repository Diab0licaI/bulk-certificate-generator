
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(String(36), primary_key=True)
    event_name = Column(String(200), nullable=False)
    issuer = Column(String(200), nullable=False)

    status = Column(String(30), default="PENDING", nullable=False)
    total_count = Column(Integer, default=0, nullable=False)
    success_count = Column(Integer, default=0, nullable=False)
    failed_count = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime(timezone=True), default=utc_now)

    certificates = relationship(
        "Certificate",
        back_populates="job",
        cascade="all, delete-orphan",
    )


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(String(36), primary_key=True)
    job_id = Column(
        String(36),
        ForeignKey("generation_jobs.id"),
        nullable=False,
        index=True,
    )

    recipient_name = Column(String(200), nullable=False)
    recipient_email = Column(String(320), nullable=False)

    status = Column(String(30), default="PENDING", nullable=False)
    error_message = Column(String(500), nullable=True)
    file_path = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now)

    job = relationship("GenerationJob", back_populates="certificates")
