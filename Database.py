import sqlite3
import os
import sys

def get_db_path():
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "election.db")

DB_PATH = get_db_path()

def connect_db():
    return sqlite3.connect(DB_PATH)

def init_db():
    con = connect_db()
    cursor = con.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS elections (
            election_id INTEGER PRIMARY KEY AUTOINCREMENT,
            e_name      TEXT NOT NULL,
            description TEXT,
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS candidates (
            c_id        INTEGER PRIMARY KEY AUTOINCREMENT,
            id_no       TEXT UNIQUE NOT NULL,
            name        TEXT NOT NULL,
            role        TEXT NOT NULL,
            kutumba     TEXT,
            election_id INTEGER,
            FOREIGN KEY (election_id) REFERENCES elections(election_id)
        );

        CREATE TABLE IF NOT EXISTS voters (
            v_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            id_no   TEXT UNIQUE NOT NULL,
            kutumba TEXT
        );

        CREATE TABLE IF NOT EXISTS election_voters (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            election_id INTEGER NOT NULL,
            voter_id    INTEGER NOT NULL,
            UNIQUE(election_id, voter_id),
            FOREIGN KEY (election_id) REFERENCES elections(election_id),
            FOREIGN KEY (voter_id)    REFERENCES voters(v_id)
        );

        CREATE TABLE IF NOT EXISTS votes (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            voter_id     INTEGER,
            candidate_id INTEGER,
            election_id  INTEGER,
            FOREIGN KEY (voter_id)     REFERENCES voters(v_id),
            FOREIGN KEY (candidate_id) REFERENCES candidates(c_id),
            FOREIGN KEY (election_id)  REFERENCES elections(election_id)
        );
    """)
    con.commit()
    con.close()

def step1_add(title, description):
    con = connect_db()
    cursor = con.cursor()
    cursor.execute("INSERT INTO elections (e_name, description) VALUES (?, ?)", (title, description))
    election_id = cursor.lastrowid
    con.commit()
    con.close()
    return election_id

def step2_add_many(election_id, candidate_rows):
    con = connect_db()
    cursor = con.cursor()
    rows = [(id_no, name, kutumba, role, election_id) for name, id_no, kutumba, role in candidate_rows]
    cursor.executemany("INSERT INTO candidates (id_no, name, kutumba, role, election_id) VALUES (?, ?, ?, ?, ?)", rows)
    con.commit()
    con.close()

def list_elections():
    con = connect_db()
    cursor = con.cursor()
    cursor.execute("SELECT election_id, e_name, description, created_at FROM elections ORDER BY election_id DESC")
    rows = cursor.fetchall()
    con.close()
    return [{"election_id": row[0], "e_name": row[1], "description": row[2], "created_at": row[3]} for row in rows]

def get_election(election_id):
    con = connect_db()
    cursor = con.cursor()
    cursor.execute("SELECT election_id, e_name, description, created_at FROM elections WHERE election_id = ?", (election_id,))
    row = cursor.fetchone()
    con.close()
    if row:
        return {"election_id": row[0], "e_name": row[1], "description": row[2], "created_at": row[3]}

def get_counts():
    con = connect_db()
    cursor = con.cursor()
    cursor.execute("SELECT COUNT(*) FROM elections")
    elections = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM candidates")
    candidates = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT voter_id) FROM election_voters")
    voters = cursor.fetchone()[0]
    con.close()
    return {"elections": elections, "candidates": candidates, "voters": voters}

def list_candidates(election_id):
    con = connect_db()
    cursor = con.cursor()
    cursor.execute("SELECT c_id, id_no, name, role, kutumba FROM candidates WHERE election_id = ? ORDER BY role ASC, name ASC",(election_id,))
    rows = cursor.fetchall()
    con.close()
    return [{"id": row[0], "id_no": row[1], "name": row[2], "role": row[3], "kutumba": row[4]} for row in rows]

def delete_candidate(candidate_id):
    con = connect_db()
    cursor = con.cursor()
    cursor.execute("DELETE FROM votes WHERE candidate_id = ?", (candidate_id,))
    cursor.execute("DELETE FROM candidates WHERE c_id = ?", (candidate_id,))
    con.commit()
    con.close()

def delete_election(election_id):
    con = connect_db()
    cursor = con.cursor()
    cursor.execute("DELETE FROM votes WHERE election_id = ?", (election_id,))
    cursor.execute("DELETE FROM candidates WHERE election_id = ?", (election_id,))
    cursor.execute("DELETE FROM election_voters WHERE election_id = ?", (election_id,))
    cursor.execute("DELETE FROM elections WHERE election_id = ?", (election_id,))
    cursor.execute("DELETE FROM voters WHERE v_id NOT IN (SELECT voter_id FROM election_voters)")
    con.commit()
    con.close()

def import_voters_for_election(election_id, voter_rows):
    con = connect_db()
    cursor = con.cursor()
    imported = 0
    skipped = 0

    valid_rows = []
    for row in voter_rows:
        id_no = str(row.get("id_no") or "").strip()
        kutumba = str(row.get("kutumba") or "").strip()
        if id_no and kutumba:
            if id_no not in [row[0] for row in valid_rows] :
                valid_rows.append((id_no, kutumba))
        else:
            skipped += 1

    for id_no, kutumba in valid_rows:
        cursor.execute("INSERT OR IGNORE INTO voters (id_no, kutumba) VALUES (?, ?) ",(id_no, kutumba))
        cursor.execute("SELECT v_id FROM voters WHERE id_no = ?", (id_no,))
        voter_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM election_voters WHERE election_id = ? AND voter_id = ?",(election_id, voter_id))
        if cursor.fetchone():
            skipped += 1
        else:
            cursor.execute("INSERT INTO election_voters (election_id, voter_id) VALUES (?, ?)",(election_id, voter_id))
            imported += 1

    con.commit()
    con.close()
    return imported, skipped

def list_voters_for_election(election_id):
    con = connect_db()
    cursor = con.cursor()
    cursor.execute("""SELECT voters.v_id, voters.id_no, voters.kutumba FROM voters 
           JOIN election_voters  ON election_voters.voter_id = voters.v_id
           WHERE election_voters.election_id = ? ORDER BY voters.id_no ASC""",(election_id,))
    rows = cursor.fetchall()
    con.close()
    return [{"id": row[0], "id_no": row[1], "kutumba": row[2]} for row in rows]

def remove_voter_from_election(election_id, voter_id):
    con = connect_db()
    cursor = con.cursor()
    cursor.execute("DELETE FROM election_voters WHERE election_id = ? AND voter_id = ?",(election_id, voter_id))
    cursor.execute("DELETE FROM voters WHERE v_id NOT IN (SELECT voter_id FROM election_voters)")
    con.commit()
    con.close()

def student_login_for_election(id_no, election_id):
    con = connect_db()
    cursor = con.cursor()
    cursor.execute(
        """SELECT voters.v_id, voters.id_no, voters.kutumba FROM voters 
           JOIN election_voters  ON election_voters.voter_id = voters.v_id
           WHERE voters.id_no = ? AND election_voters.election_id = ?""",(id_no, election_id))
    row = cursor.fetchone()
    con.close()
    if row:
        return {"id": row[0], "id_no": row[1], "kutumba": row[2]}

def ballot_for_election(election_id, voter_kutumba):
    con = connect_db()
    cursor = con.cursor()
    cursor.execute("SELECT c_id, id_no, name, role, kutumba FROM candidates WHERE election_id = ? ORDER BY role ASC, name ASC",(election_id,))
    rows = cursor.fetchall()
    con.close()
    ballot = {}
    for row in rows:
        cid, id_no, name, role, kutumba = row
        is_sports = "Sports Captain" in role
        if voter_kutumba:
            if not is_sports and kutumba != voter_kutumba:
                continue
        if role not in ballot:
            ballot[role] = []
        ballot[role].append({"id": cid, "id_no": id_no, "name": name, "role": role, "kutumba": kutumba})
    return ballot

def submit_vote(voter_id, election_id, candidate_id):
    con = connect_db()
    cursor = con.cursor()
    cursor.execute("SELECT role, kutumba FROM candidates WHERE c_id = ? AND election_id = ?", (candidate_id, election_id))
    row = cursor.fetchone()
    role, candidate_kutumba = row
    cursor.execute(
        "SELECT votes.id FROM votes  JOIN candidates  ON candidates.c_id = votes.candidate_id WHERE votes.voter_id = ? AND votes.election_id = ? AND candidates.role = ? LIMIT 1",(voter_id, election_id, role))
    if cursor.fetchone():
        con.close()
        return {"success": False, "message": f"Already voted for: {role}."}
    cursor.execute(
        "INSERT INTO votes (voter_id, candidate_id, election_id) VALUES (?, ?, ?)",
        (voter_id, candidate_id, election_id)
    )
    con.commit()
    con.close()
    return {"success": True, "message": "Vote submitted."}

def get_results_for_election(election_id):
    con = connect_db()
    cursor = con.cursor()
    cursor.execute(
        """SELECT candidates.role, candidates.name, candidates.kutumba, COUNT(votes.id) as vote_count
           FROM candidates 
           LEFT JOIN votes  ON votes.candidate_id = candidates.c_id AND votes.election_id = candidates.election_id
           WHERE candidates.election_id = ?
           GROUP BY candidates.c_id
           ORDER BY candidates.role ASC, vote_count DESC""",(election_id,))
    rows = cursor.fetchall()
    cursor.execute("SELECT COUNT(DISTINCT voter_id) FROM votes WHERE election_id = ?",(election_id,))
    total_votes = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM election_voters WHERE election_id = ?",(election_id,))
    total_voters = cursor.fetchone()[0]
    con.close()
    results = {}
    for row in rows:
        role = row[0]
        if role not in results:
            results[role] = []
        results[role].append({"name": row[1], "kutumba": row[2], "votes": row[3]})
    return {"results": results, "total_votes": total_votes, "total_voters": total_voters}
