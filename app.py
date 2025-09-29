from flask import request, jsonify
from datetime import datetime
import uuid
from pydantic import ValidationError

@app.post("/v1/survey")
def submit_survey():
    if not request.is_json:
        return jsonify({"error": "invalid_json"}), 400

    body = request.get_json(silent=True) or {}

    try:
        # Use pydantic v1 API
        sub = SurveySubmission.parse_obj(body)
    except ValidationError as e:
        # Invalid inputs should be 422 Unprocessable Entity
        return jsonify({"error": "invalid_input", "detail": e.errors()}), 422

    submission_id = str(uuid.uuid4())
    now = datetime.now()

    to_store = {
        "email_sha256": sha256_hex(sub.email),
        "age_sha256": sha256_hex(str(sub.age)),
        "submission_id": submission_id,
        "submitted_at": now.isoformat(),
    }
    append_json_line(to_store)

    return jsonify({"status": "ok", "submission_id": submission_id}), 201
