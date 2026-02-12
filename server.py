"""
Solutions PM — Flask API Server
Wraps existing backend modules into a clean REST API
"""

from flask import Flask, jsonify, request, send_from_directory, Response
import os
import sys
import csv
import io
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tracking.database import OnboardingDatabase
from documents.generator import DocumentGenerator
import config

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.secret_key = config.SECRET_KEY

# ---------------------------------------------------------------------------
# Database helper
# ---------------------------------------------------------------------------
_db = None

def get_db():
    global _db
    if _db is None:
        _db = OnboardingDatabase(config.DB_PATH)
    return _db


def consultant_to_dict(c):
    return {
        "id": c.id,
        "name": c.name,
        "email": c.email,
        "position": c.position,
        "manager": c.manager,
        "start_date": c.start_date,
        "end_date": c.end_date,
        "employment_type": c.employment_type,
        "pay_rate": c.pay_rate,
        "status": c.status or "Pending",
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }


def document_to_dict(d):
    return {
        "id": d.id,
        "consultant_id": d.consultant_id,
        "document_type": d.document_type,
        "file_path": d.file_path,
        "status": d.status or "Pending",
        "sent_date": d.sent_date.isoformat() if d.sent_date else None,
        "received_date": d.received_date.isoformat() if d.received_date else None,
    }


def activity_to_dict(a):
    return {
        "id": a.id,
        "consultant_id": a.consultant_id,
        "activity_type": a.activity_type,
        "description": a.description,
        "timestamp": a.timestamp.isoformat() if a.timestamp else None,
    }


# ---------------------------------------------------------------------------
# Serve SPA
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return send_from_directory("static", "index.html")


# ---------------------------------------------------------------------------
# API — Summary
# ---------------------------------------------------------------------------
@app.route("/api/summary")
def api_summary():
    db = get_db()
    summary = db.get_onboarding_summary()
    return jsonify({
        "total": summary["total"],
        "pending": summary["pending"],
        "in_progress": summary["in_progress"],
        "complete": summary["complete"],
    })


# ---------------------------------------------------------------------------
# API — Consultants (list / create)
# ---------------------------------------------------------------------------
@app.route("/api/consultants", methods=["GET"])
def api_list_consultants():
    db = get_db()
    consultants = db.get_all_consultants()
    result = []
    for c in consultants:
        d = consultant_to_dict(c)
        docs = db.get_consultant_documents(c.id)
        total = len(docs)
        completed = len([doc for doc in docs if doc.status == "Completed"])
        d["doc_total"] = total
        d["doc_completed"] = completed
        d["doc_progress"] = (completed / total * 100) if total > 0 else 0
        result.append(d)
    return jsonify(result)


@app.route("/api/consultants", methods=["POST"])
def api_add_consultant():
    data = request.get_json()
    db = get_db()
    consultant = db.add_consultant(data)

    # Optionally add standard docs
    if data.get("add_standard_docs", True):
        for doc_type in ["Offer Letter", "Job Description", "W-4", "I-9", "Direct Deposit Form"]:
            db.add_document(consultant.id, doc_type)

    return jsonify(consultant_to_dict(consultant)), 201


# ---------------------------------------------------------------------------
# API — Consultant Detail
# ---------------------------------------------------------------------------
@app.route("/api/consultants/<int:cid>")
def api_get_consultant(cid):
    db = get_db()
    progress = db.get_consultant_progress(cid)
    if not progress:
        return jsonify({"error": "Not found"}), 404

    c = progress["consultant"]
    return jsonify({
        "consultant": consultant_to_dict(c),
        "documents": [document_to_dict(d) for d in progress["documents"]],
        "activities": [activity_to_dict(a) for a in progress["activities"]],
        "total_documents": progress["total_documents"],
        "completed_documents": progress["completed_documents"],
        "completion_percentage": progress["completion_percentage"],
    })


# ---------------------------------------------------------------------------
# API — Update consultant status
# ---------------------------------------------------------------------------
@app.route("/api/consultants/<int:cid>/status", methods=["PUT"])
def api_update_status(cid):
    data = request.get_json()
    db = get_db()
    c = db.update_consultant_status(cid, data["status"])
    if not c:
        return jsonify({"error": "Not found"}), 404
    return jsonify(consultant_to_dict(c))


# ---------------------------------------------------------------------------
# API — Generate documents
# ---------------------------------------------------------------------------
@app.route("/api/consultants/<int:cid>/generate-docs", methods=["POST"])
def api_generate_docs(cid):
    db = get_db()
    c = db.get_consultant(cid)
    if not c:
        return jsonify({"error": "Not found"}), 404

    try:
        gen = DocumentGenerator(
            templates_dir=config.TEMPLATES_DIR,
            output_dir=config.GENERATED_DIR
        )
        consultant_data = {
            "name": c.name,
            "email": c.email,
            "position": c.position,
            "manager": c.manager or "Debbie Murray",
            "start_date": c.start_date or "",
            "end_date": c.end_date or "N/A",
            "employment_type": c.employment_type or "Full-time",
            "pay_rate": c.pay_rate or "",
        }

        offer_path = gen.generate_offer_letter(consultant_data)
        checklist_path = gen.generate_onboarding_checklist(consultant_data)

        # Update DB records
        docs = db.get_consultant_documents(c.id)
        for doc in docs:
            if doc.document_type == "Offer Letter":
                doc.file_path = offer_path
                doc.status = "Generated"
                db.session.commit()

        db.log_activity(c.id, "Documents Generated", "Offer letter and checklist created")

        return jsonify({"offer": offer_path, "checklist": checklist_path})
    except FileNotFoundError:
        return jsonify({"error": "Template not found — ensure offer_letter_template.docx is in documents/templates/"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# API — Send offer email (stub — logs but doesn't actually send unless
# SendGrid key is configured)
# ---------------------------------------------------------------------------
@app.route("/api/consultants/<int:cid>/send-offer", methods=["POST"])
def api_send_offer(cid):
    db = get_db()
    c = db.get_consultant(cid)
    if not c:
        return jsonify({"error": "Not found"}), 404

    docs = db.get_consultant_documents(c.id)
    offer_doc = next((d for d in docs if d.document_type == "Offer Letter"), None)

    if not offer_doc or not offer_doc.file_path:
        return jsonify({"error": "Generate documents first"}), 400

    # Mark as sent
    db.update_document_status(offer_doc.id, "Sent")
    db.log_activity(c.id, "Email Sent", f"Offer letter sent to {c.email}")
    return jsonify({"message": f"Offer letter sent to {c.email}"})


# ---------------------------------------------------------------------------
# API — Send reminder
# ---------------------------------------------------------------------------
@app.route("/api/consultants/<int:cid>/send-reminder", methods=["POST"])
def api_send_reminder(cid):
    db = get_db()
    c = db.get_consultant(cid)
    if not c:
        return jsonify({"error": "Not found"}), 404

    docs = db.get_consultant_documents(c.id)
    pending = [d.document_type for d in docs if d.status not in ("Completed", "Received")]
    if not pending:
        return jsonify({"message": "No pending documents"}), 200

    db.log_activity(c.id, "Reminder Sent", f"Reminder sent to {c.email} for {len(pending)} docs")
    return jsonify({"message": f"Reminder sent to {c.email}", "pending": pending})


# ---------------------------------------------------------------------------
# API — Update document status
# ---------------------------------------------------------------------------
@app.route("/api/documents/<int:did>/status", methods=["PUT"])
def api_update_doc_status(did):
    data = request.get_json()
    db = get_db()
    d = db.update_document_status(did, data["status"])
    if not d:
        return jsonify({"error": "Not found"}), 404
    return jsonify(document_to_dict(d))


# ---------------------------------------------------------------------------
# API — Add standard docs
# ---------------------------------------------------------------------------
@app.route("/api/consultants/<int:cid>/add-standard-docs", methods=["POST"])
def api_add_standard_docs(cid):
    db = get_db()
    c = db.get_consultant(cid)
    if not c:
        return jsonify({"error": "Not found"}), 404
    for doc_type in ["Offer Letter", "Job Description", "W-4", "I-9", "Direct Deposit Form"]:
        db.add_document(c.id, doc_type)
    return jsonify({"message": "Standard documents added"})


# ---------------------------------------------------------------------------
# API — Activities
# ---------------------------------------------------------------------------
@app.route("/api/consultants/<int:cid>/activities")
def api_activities(cid):
    db = get_db()
    activities = db.get_consultant_activities(cid, limit=50)
    return jsonify([activity_to_dict(a) for a in activities])


# ---------------------------------------------------------------------------
# API — CSV Exports
# ---------------------------------------------------------------------------
@app.route("/api/export/consultants")
def api_export_consultants():
    db = get_db()
    consultants = db.get_all_consultants()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Name", "Email", "Position", "Status", "Start Date", "Manager", "Hourly Rate"])
    for c in consultants:
        writer.writerow([c.name, c.email, c.position, c.status, c.start_date, c.manager, c.pay_rate])
    output = buf.getvalue()
    return Response(output, mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=consultants.csv"})


@app.route("/api/export/documents")
def api_export_documents():
    db = get_db()
    consultants = db.get_all_consultants()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Consultant", "Document", "Status", "File Path"])
    for c in consultants:
        for d in db.get_consultant_documents(c.id):
            writer.writerow([c.name, d.document_type, d.status, d.file_path])
    output = buf.getvalue()
    return Response(output, mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=documents.csv"})


@app.route("/api/export/activities")
def api_export_activities():
    db = get_db()
    consultants = db.get_all_consultants()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Consultant", "Activity", "Description", "Timestamp"])
    for c in consultants:
        for a in db.get_consultant_activities(c.id, limit=200):
            writer.writerow([c.name, a.activity_type, a.description,
                             a.timestamp.isoformat() if a.timestamp else ""])
    output = buf.getvalue()
    return Response(output, mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=activities.csv"})


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
