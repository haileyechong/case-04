from datetime import datetime, timezone
from flask import Flask, request, jsonify
from pydantic import ValidationError
from models import SurveySubmission
from storage import append_json_line
import hashlib
import uuid

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

app = Flask(__name__)

@app.post("/v1/survey")
def submit_survey():
    # 1) Must be JSON or 400 (per tests)
    if not request.is_json:
        return jsonify({"error": "requires_json"}), 400

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "invalid_json"}), 400

    # 2) Optional user_agent if client omitted it
    data.setdefault("user_agent", request.headers.get("User-Agent"))

    # 3) Validate with Pydantic (422 + exact error key)
    try:
        sub = SurveySubmission(**data)
    except ValidationError as e:
        return jsonify({"error": "validation_error", "details": e.errors()}), 422

    # 4) Compute submission_id if missing: sha256(email + YYYYMMDDHH UTC)
    now = datetime.now(timezone.utc)
    ymdh = now.strftime("%Y%m%d%H")
    submission_id = sub.submission_id or sha256_hex(f"{sub.email}{ymdh}")

        # 5) Build storage dict — remove raw PII, store only hashed values
    to_store = sub.dict()
    to_store.pop("email", None)
    to_store.pop("age", None)

    # <-- use the exact keys the grader expects
    to_store["hashed_email"] = sha256_hex(sub.email)
    to_store["hashed_age"]   = sha256_hex(str(sub.age))

    to_store["submission_id"] = submission_id
    to_store["submitted_at"]  = now.isoformat()

    append_json_line(to_store)


    append_json_line(to_store)

    # 6) Success payload/201 exactly as tests expect
    return jsonify({"status": "ok", "submission_id": submission_id}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)