import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    def load_dotenv(*args, **kwargs):  # fallback no-op
        return False

load_dotenv()

app = Flask(__name__)
# Basic secret key for flash messages; override via .env FLASK_SECRET_KEY
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change")

DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
CSV_PATH = DATA_DIR / "registrations.csv"
IMG_DIR = Path("img")  # Optional folder for uploaded assets like logos
DISABLE_CSV = os.getenv("DISABLE_CSV", "").lower() in {"1", "true", "yes", "on"} or bool(os.getenv("VERCEL"))

REQUIRED_FIELDS = [
    "participant_name",
    "age",
    "phone",
    "departure_from",
    "return_bus",
    "guardian_name",
    "guardian_phone",
    "consent_participation",
    "consent_rules",
    "consent_privacy",
]

FIELDNAMES = [
    "timestamp",
    "participant_name",
    "age",
    "phone",
    "email",
    "school",
    "departure_from",
    "return_bus",
    "departure_contact",
    "guardian_name",
    "guardian_phone",
    "emergency_name",
    "emergency_phone",
    "health_notes",
    "consent_participation",
    "consent_photo",
    "consent_rules",
    "consent_privacy",
    "ip",
    "user_agent",
]


def ensure_csv_header():
    if DISABLE_CSV:
        app.logger.info("CSV disabled (DISABLE_CSV or VERCEL set); skipping header creation")
        return
    if not CSV_PATH.exists():
        with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


ensure_csv_header()


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/img/<path:filename>")
def image_assets(filename: str):
    """Serve files from the optional ./img directory to make logo usage easy."""
    directory = IMG_DIR.resolve()
    if not directory.exists():
        # If folder not present, return 404 via Flask's default handling
        from flask import abort
        abort(404)
    return send_from_directory(str(directory), filename)


def validate_form(form: Dict[str, str]) -> Tuple[bool, str]:
    for field in REQUIRED_FIELDS:
        if not form.get(field):
            return False, "Vennligst fyll ut alle obligatoriske felter og samtykker."
    # Basic numeric check for age
    try:
        age = int(form.get("age", "0"))
        if age < 6 or age > 14:
            return False, "Alder må være mellom 6 og 14 år for dette arrangementet."
    except ValueError:
        return False, "Ugyldig alder."
    return True, ""


def save_csv(row: Dict[str, str]):
    if DISABLE_CSV:
        app.logger.info("CSV disabled; not writing registration to disk")
        return
    ensure_csv_header()
    with CSV_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(row)


def send_email(row: Dict[str, str]):
    """Optional SMTP email with a small CSV attachment. Skips silently if not configured."""
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "0"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    to_email = os.getenv("NOTIFY_EMAIL")

    if not (host and port and to_email):
        return  # Not configured

    subject = "Ny påmelding – Puls Musikkverksted"

    # Build a plaintext summary
    lines = [f"{k}: {row.get(k, '')}" for k in FIELDNAMES if k != "user_agent"]
    body_text = "\n".join(lines)

    # Build a one-line CSV attachment (header + row) for Excel friendliness
    csv_header = ",".join(FIELDNAMES)
    csv_row = ",".join([str(row.get(k, "")).replace("\n", " ") for k in FIELDNAMES])
    attachment_content = f"{csv_header}\n{csv_row}\n".encode("utf-8")

    try:
        import smtplib
        from email.message import EmailMessage

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = user or "noreply@localhost"
        msg["To"] = to_email
        msg.set_content(body_text)

        filename = f"registration-{row.get('timestamp','')}.csv" or "registration.csv"
        msg.add_attachment(attachment_content, maintype="text", subtype="csv", filename=filename)

        with smtplib.SMTP(host, port, timeout=10) as server:
            if os.getenv("SMTP_TLS", "true").lower() in {"1", "true", "yes", "on"}:
                server.starttls()
            if user and password:
                server.login(user, password)
            server.send_message(msg)
    except Exception as e:
        app.logger.warning("Email sending skipped/failed: %s", e)


@app.post("/submit")
def submit():
    form = request.form
    ok, err = validate_form(form)
    if not ok:
        flash(err, "error")
        return redirect(url_for("index"))

    now = datetime.now().isoformat(timespec="seconds")
    row = {k: "" for k in FIELDNAMES}
    row.update({
        "timestamp": now,
        "participant_name": form.get("participant_name", "").strip(),
        "age": form.get("age", "").strip(),
        "phone": form.get("phone", "").strip(),
        "email": form.get("email", "").strip(),
        "school": form.get("school", "").strip(),
        "departure_from": form.get("departure_from", "").strip(),
        "return_bus": form.get("return_bus", "").strip(),
        "departure_contact": form.get("departure_contact", "").strip(),
        "guardian_name": form.get("guardian_name", "").strip(),
        "guardian_phone": form.get("guardian_phone", "").strip(),
        "emergency_name": form.get("emergency_name", "").strip(),
        "emergency_phone": form.get("emergency_phone", "").strip(),
        "health_notes": form.get("health_notes", "").strip(),
        "consent_participation": "Ja" if form.get("consent_participation") else "Nei",
        "consent_photo": "Ja" if form.get("consent_photo") else "Nei",
        "consent_rules": "Ja" if form.get("consent_rules") else "Nei",
        "consent_privacy": "Ja" if form.get("consent_privacy") else "Nei",
        "ip": request.headers.get("X-Forwarded-For", request.remote_addr or ""),
        "user_agent": request.headers.get("User-Agent", ""),
    })

    save_csv(row)
    send_email(row)

    flash("Takk! Påmeldingen er registrert.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
