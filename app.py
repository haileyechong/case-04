from datetime import datetime, timezone
from flask import Flask, request, jsonify
from pydantic import ValidationError
from models import SurveySubmission
from storage import append_json_line
import hashlib

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

app = Flask(__name__)

@app.post("/v1/survey")
def submit_survey():
    if not request.is_json:
        return jsonify({"error": "JSON required"}), 415

    sub = SurveySubmission.model_validate(request.json)

    submission_id = str(uuid.uuid4())
    now = datetime.now()

    # Build record with hashed PII
    to_store = {}
    to_store["email_sha256"] = sha256_hex(sub.email)
    to_store["age_sha256"] = sha256_hex(str(sub.age))
    to_store["submission_id"] = submission_id
    to_store["submitted_at"] = now.isoformat()

    append_json_line(to_store)

    return jsonify({"status": "ok", "submission_id": submission_id}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
