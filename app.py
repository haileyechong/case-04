from datetime import datetime, timezone
from flask import Flask, request, jsonify
from models import SurveySubmission
from storage import append_json_line
import hashlib

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()



app = Flask(__name__)

@app.post("/v1/survey")
def submit_survey():
    data = request.get_json(force=True)

    # Fill user_agent from headers if not provided (Exercise 11.1)
    data.setdefault("user_agent", request.headers.get("User-Agent"))

    sub = SurveySubmission(**data)

    # Compute submission_id if missing (Exercise 11.3)
    now = datetime.now(timezone.utc)
    ymdh = now.strftime("%Y%m%d%H")
    submission_id = sub.submission_id or sha256_hex(f"{sub.email}{ymdh}")

    # Keep original field names, just replace PII with hashes (Exercise 11.2)
    to_store = sub.model_dump()                  # dict with your original keys
    to_store["email"] = sha256_hex(sub.email)    # same key, hashed value
    to_store["age"]   = sha256_hex(str(sub.age)) # same key, hashed value
    to_store["submission_id"] = submission_id
    to_store["submitted_at"]  = now.isoformat()  # helpful timestamp

    append_json_line(to_store)
    return jsonify({"ok": True, "submission_id": submission_id})
