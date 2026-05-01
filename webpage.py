from flask import Flask, request, jsonify, render_template_string, redirect, url_for
import Database as db

app = Flask(__name__)
app.secret_key = "election-dev-key"

LOGIN_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Voter Login</title>
  <style>
    body { font-family: Arial, sans-serif; background:#111827; color:#e5e7eb; margin:0; }
    .wrap { max-width:480px; margin:60px auto; background:#1f2937; border-radius:12px; padding:32px; }
    h2 { margin:0 0 24px; }
    label { display:block; font-size:13px; color:#9ca3af; margin-top:16px; margin-bottom:4px; }
    input { width:100%; padding:10px; border-radius:8px; border:1px solid #374151; background:#0f172a; color:#e5e7eb; box-sizing:border-box; font-size:14px; }
    button { margin-top:24px; width:100%; padding:11px; background:#2563eb; color:white; font-weight:700; border:none; border-radius:8px; cursor:pointer; font-size:14px; }
    button:hover { background:#1d4ed8; }
    .msg { color:#fca5a5; margin-top:14px; font-size:13px; }
  </style>
</head>
<body>
  <div class="wrap">
    <h2>Voter Login</h2>
    <form method="post">
      <label>Election ID</label>
      <input name="election_id" required value="{{ election_id }}" placeholder="e.g. 1">
      <label>Student ID No</label>
      <input name="id_no" required placeholder="Your roll number">
      <button type="submit">Continue</button>
    </form>
    {% if message %}<div class="msg">{{ message }}</div>{% endif %}
  </div>
</body>
</html>
"""

BALLOT_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Ballot</title>
  <style>
    body { font-family: Arial, sans-serif; background:#111827; color:#e5e7eb; margin:0; }
    .wrap { max-width:720px; margin:32px auto; background:#1f2937; border-radius:12px; padding:28px; }
    h2 { margin:0 0 6px; }
    .meta { color:#9ca3af; font-size:13px; margin-bottom:24px; }
    .role { border:1px solid #374151; border-radius:10px; padding:16px; margin-top:14px; }
    .role h3 { margin:0 0 12px; color:#93c5fd; font-size:15px; }
    label { display:block; margin-top:8px; padding:8px 10px; border-radius:6px; cursor:pointer; font-size:14px; }
    label:hover { background:#374151; }
    input[type=radio] { margin-right:8px; }
    button { margin-top:24px; padding:12px 24px; background:#16a34a; color:#fff; border:none; border-radius:8px; font-weight:700; cursor:pointer; font-size:14px; }
    button:hover { background:#15803d; }
  </style>
</head>
<body>
  <div class="wrap">
    <h2>{{ election["e_name"] }}</h2>
    <div class="meta">ID: {{ student["id_no"] }}  |  Kutumba: {{ student["kutumba"] or "-" }}</div>
    <form method="post" action="{{ url_for('submit_vote_web') }}">
      <input type="hidden" name="id_no" value="{{ student['id_no'] }}">
      <input type="hidden" name="election_id" value="{{ election['election_id'] }}">
      {% for role, candidates in ballot.items() %}
        <div class="role">
          <h3>{{ role }}</h3>
          {% for c in candidates %}
            <label>
              <input type="radio" name="role_{{ role }}" value="{{ c['id'] }}" required>
              {{ c["name"] }}{% if c["kutumba"] %} - {{ c["kutumba"] }}{% endif %}
            </label>
          {% endfor %}
        </div>
      {% endfor %}
      <button type="submit">Submit Vote</button>
    </form>
  </div>
</body>
</html>
"""

RESULT_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Vote Submitted</title>
  <style>
    body { font-family: Arial, sans-serif; background:#111827; color:#e5e7eb; margin:0; }
    .wrap { max-width:560px; margin:60px auto; background:#1f2937; border-radius:12px; padding:28px; }
    h2 { margin:0 0 20px; }
    ul { padding-left:18px; }
    li { margin:8px 0; font-size:14px; }
    .ok { color:#86efac; }
    .fail { color:#fca5a5; }
    a { color:#93c5fd; display:inline-block; margin-top:20px; font-size:14px; }
  </style>
</head>
<body>
<div class="wrap">
  <h2>Vote Submitted</h2>
  <ul>
  {% for item in messages %}
    <li class="{{ 'ok' if item.success else 'fail' }}">{{ item.role }}: {{ item.message }}</li>
  {% endfor %}
  </ul>
  <a href="{{ url_for('login_page') }}">Back to login</a>
</div>
</body>
</html>
"""


@app.get("/health")
def health():
    return jsonify({"success": True})

@app.get("/")
def home():
    return redirect(url_for("login_page"))

@app.get("/elections")
def elections():
    return jsonify(db.list_elections())

@app.get("/elections/<int:election_id>/ballot")
def ballot(election_id):
    election = db.get_election(election_id)
    if not election:
        return jsonify({"success": False, "message": "Election not found."}), 404
    return jsonify({"success": True, "election": election, "ballot": db.ballot_for_election(election_id)})

@app.route("/login", methods=["GET", "POST"])
def login_page():
    election_id = request.args.get("election_id", "").strip()
    message = ""
    if request.method == "POST":
        election_id = (request.form.get("election_id") or "").strip()
        id_no = (request.form.get("id_no") or "").strip()
        if not election_id.isdigit():
            message = "Enter a valid Election ID."
        else:
            election = db.get_election(int(election_id))
            student = db.student_login_for_election(id_no, int(election_id))
            if not election:
                message = "Election not found."
            elif not student:
                message = "Invalid ID or you are not registered for this election."
            else:
                return redirect(url_for("ballot_page", election_id=election_id, id_no=id_no))
    return render_template_string(LOGIN_HTML, message=message, election_id=election_id)

@app.get("/ballot")
def ballot_page():
    election_id = (request.args.get("election_id") or "").strip()
    id_no = (request.args.get("id_no") or "").strip()
    if not election_id.isdigit():
        return redirect(url_for("login_page"))
    election = db.get_election(int(election_id))
    student = db.student_login_for_election(id_no, int(election_id))
    if not election or not student:
        return redirect(url_for("login_page", election_id=election_id))
    ballot = db.ballot_for_election(int(election_id), student["kutumba"])
    return render_template_string(BALLOT_HTML, election=election, student=student, ballot=ballot)

@app.post("/submit")
def submit_vote_web():
    id_no = (request.form.get("id_no") or "").strip()
    election_id = int((request.form.get("election_id") or "0").strip())
    student = db.student_login_for_election(id_no, election_id)
    election = db.get_election(election_id)
    if not student or not election:
        return redirect(url_for("login_page"))
    ballot = db.ballot_for_election(election_id, student["kutumba"])
    messages = []
    for role in ballot.keys():
        selected = request.form.get(f"role_{role}")
        if not selected:
            messages.append({"role": role, "success": False, "message": "not selected"})
            continue
        result = db.submit_vote(student["id"], election_id, int(selected))
        messages.append({"role": role, "ok": result["success"], "message": result["message"]})
    return render_template_string(RESULT_HTML, messages=messages)

@app.post("/auth/login")
def login_api():
    data = request.get_json(silent=True) or {}
    id_no = (data.get("id_no") or "").strip()
    election_id = data.get("election_id")
    if not id_no or not election_id:
        return jsonify({"success": False, "message": "id_no and election_id are required."}), 400
    student = db.student_login_for_election(id_no, int(election_id))
    if not student:
        return jsonify({"success": False, "message": "Invalid login or not registered for this election."}), 401
    return jsonify({"success": True, "student": {"id": student["id"], "id_no": student["id_no"], "kutumba": student["kutumba"]}})

@app.post("/vote")
def vote_api():
    data = request.get_json(silent=True) or {}
    id_no = (data.get("id_no") or "").strip()
    election_id = data.get("election_id")
    candidate_id = data.get("candidate_id")
    if not id_no or not election_id or not candidate_id:
        return jsonify({"success": False, "message": "id_no, election_id, candidate_id are required."}), 400
    student = db.student_login_for_election(id_no, int(election_id))
    if not student:
        return jsonify({"success": False, "message": "Invalid login or not registered for this election."}), 401
    result = db.submit_vote(student["id"], int(election_id), int(candidate_id))
    return jsonify(result), (200 if result["success"] else 400)