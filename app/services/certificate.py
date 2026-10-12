
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

CERTIFICATE_DIR = Path("certificates")


def generate_certificate_pdf(
    certificate_id: str,
    recipient_name: str,
    event_name: str,
    issuer: str,
) -> str:
    """Generate one PDF certificate and return its file path."""

    CERTIFICATE_DIR.mkdir(parents=True, exist_ok=True)

    output_path = CERTIFICATE_DIR / f"{certificate_id}.pdf"

    width, height = landscape(A4)
    pdf = canvas.Canvas(str(output_path), pagesize=(width, height))

    # Decorative border
    pdf.setStrokeColor(colors.HexColor("#D4AF37"))
    pdf.setLineWidth(3)
    pdf.rect(25, 25, width - 50, height - 50)

    # Certificate title
    pdf.setFillColor(colors.HexColor("#172554"))
    pdf.setFont("Helvetica-Bold", 28)
    pdf.drawCentredString(
        width / 2,
        height - 115,
        "CERTIFICATE OF ACHIEVEMENT",
    )

    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica", 15)
    pdf.drawCentredString(
        width / 2,
        height - 165,
        "This certificate is proudly presented to",
    )

    # Recipient's name
    pdf.setFillColor(colors.HexColor("#1D4ED8"))
    pdf.setFont("Helvetica-Bold", 25)
    pdf.drawCentredString(
        width / 2,
        height - 215,
        recipient_name[:100],
    )

    # Event information
    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(
        width / 2,
        height - 260,
        f"For successful participation in {event_name[:150]}",
    )

    # Issuer
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawCentredString(
        width / 2,
        height - 315,
        issuer[:100],
    )

    pdf.setFont("Helvetica", 11)
    pdf.drawCentredString(
        width / 2,
        65,
        f"Issued on {date.today().isoformat()}",
    )

    pdf.save()
    return str(output_path)
