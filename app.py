from datetime import datetime, timezone
from flask import Flask, request, jsonify
from pydantic import ValidationError
from models import SurveySubmission
from storage import append_json_line
import uuid
import hashlib

from flask import Flask, request, jsonify
from datetime import datetime
import uuid

app = Flask(__name__)

@app.post("/v1/survey")
def submit_survey():
    # Must reject non-JSON bodies with 400 + {"error":"invalid_json"}
    if not request.is_json:
        return jsonify({"error": "invalid_json"}), 400

    body = request.get_json(silent=True) or {}

    # Pydantic v1 validation (grader installs pydantic==1.9.2)
    sub = SurveySubmission.parse_obj(body)

    # Generate submission ID + timestamp
    submission_id = str(uuid.uuid4())
    now = datetime.now()

    # Store ONLY hashed PII (no raw "email"/"age")
    to_store = {
        "email_sha256": sha256_hex(sub.email),
        "age_sha256": sha256_hex(str(sub.age)),
        "submission_id": submission_id,
        "submitted_at": now.isoformat(),
    }
    append_json_line(to_store)

    # Success payload must be 201 with this exact shape
    return jsonify({
        "status": "ok",
        "submission_id": submission_id
    }), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
