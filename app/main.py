
from pathlib import Path
from uuid import uuid4

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.database import Base, engine, get_db, SessionLocal
from app.models import Certificate, GenerationJob
from app.schemas import GenerationRequest, RecipientInput
from app.services.certificate import generate_certificate_pdf
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bulk Certificate Generator",
    description="Generate and download certificates in bulk.",
    version="1.0.0",
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)


def process_job(job_id: str):
    """Generate certificates independently for each recipient."""
    db = SessionLocal()

    try:
        job = db.get(GenerationJob, job_id)
        if job is None:
            return

        job.status = "PROCESSING"
        db.commit()

        records = (
            db.query(Certificate)
            .filter(
                Certificate.job_id == job_id,
                Certificate.status == "PENDING",
            )
            .all()
        )

        for record in records:
            try:
                recipient = RecipientInput.model_validate({
                    "name": record.recipient_name,
                    "email": record.recipient_email,
                })

                record.file_path = generate_certificate_pdf(
                    certificate_id=record.id,
                    recipient_name=recipient.name,
                    event_name=job.event_name,
                    issuer=job.issuer,
                )
                record.status = "COMPLETED"
                record.error_message = None

            except Exception:
                record.status = "FAILED"
                record.error_message = (
                    "Certificate generation failed. "
                    "Check server logs for details."
                )

            db.commit()

        # Recalculate the final results from the database.
        records = (
            db.query(Certificate)
            .filter(Certificate.job_id == job_id)
            .all()
        )

        job.success_count = sum(
            record.status == "COMPLETED" for record in records
        )
        job.failed_count = sum(
            record.status == "FAILED" for record in records
        )
        job.status = (
            "COMPLETED_WITH_ERRORS"
            if job.failed_count
            else "COMPLETED"
        )
        db.commit()

    finally:
        db.close()

@app.get("/", include_in_schema=False)
def root():
    return FileResponse("app/static/index.html")

@app.post("/api/jobs/", status_code=202)
def create_job(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    job = GenerationJob(
        id=str(uuid4()),
        event_name=request.event_name,
        issuer=request.issuer,
        status="PENDING",
        total_count=len(request.recipients),
        success_count=0,
        failed_count=0,
    )
    db.add(job)

    for item in request.recipients:
        certificate_id = str(uuid4())

        try:
            recipient = RecipientInput.model_validate(item)
            record = Certificate(
                id=certificate_id,
                job_id=job.id,
                recipient_name=recipient.name,
                recipient_email=str(recipient.email),
                status="PENDING",
            )

        except ValidationError as exc:
            raw_name = item.get("name")
            raw_email = item.get("email")

            record = Certificate(
                id=certificate_id,
                job_id=job.id,
                recipient_name=(
                    raw_name[:200]
                    if isinstance(raw_name, str) and raw_name.strip()
                    else "Invalid recipient"
                ),
                recipient_email=(
                    raw_email[:320]
                    if isinstance(raw_email, str)
                    else ""
                ),
                status="FAILED",
                error_message=(
                    "Invalid recipient data: "
                    + exc.errors()[0]["msg"][:350]
                ),
            )

        db.add(record)

    db.commit()

    # Count validation failures before generation begins.
    job.failed_count = sum(
        record.status == "FAILED" for record in job.certificates
    )
    db.commit()

    background_tasks.add_task(process_job, job.id)

    return {
        "job_id": job.id,
        "status": job.status,
        "total_count": job.total_count,
        "status_url": f"/api/jobs/{job.id}",
    }


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.get(GenerationJob, job_id)

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    records = (
        db.query(Certificate)
        .filter(Certificate.job_id == job_id)
        .all()
    )

    return {
        "job_id": job.id,
        "event_name": job.event_name,
        "issuer": job.issuer,
        "status": job.status,
        "total_count": job.total_count,
        "success_count": job.success_count,
        "failed_count": job.failed_count,
        "recipients": [
            {
                "certificate_id": record.id,
                "name": record.recipient_name,
                "email": record.recipient_email,
                "status": record.status,
                "error": record.error_message,
                "download_url": (
                    f"/api/certificates/{record.id}/download"
                    if record.status == "COMPLETED"
                    else None
                ),
            }
            for record in records
        ],
    }


@app.get("/api/certificates/{certificate_id}/download")
def download_certificate(
    certificate_id: str,
    db: Session = Depends(get_db),
):
    record = db.get(Certificate, certificate_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found",
        )

    if record.status != "COMPLETED" or not record.file_path:
        raise HTTPException(
            status_code=409,
            detail="Certificate is not ready for download",
        )

    path = Path(record.file_path)

    if not path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Certificate PDF file is missing",
        )

    return FileResponse(
        path=str(path),
        media_type="application/pdf",
        filename=f"certificate-{record.id}.pdf",
    )
