from flask import Flask, request, jsonify, send_file, render_template, redirect, url_for
from flask_cors import CORS
import sqlite3, io, datetime, json, csv
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from pathlib import Path

DB = "database.db"
app = Flask(_name_, template_folder="templates", static_folder="static")
CORS(app)

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # Store structured JSON in data column and keep form_type & visitor_type columns
    c.execute("""
    CREATE TABLE IF NOT EXISTS forms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        form_type TEXT,
        visitor_type TEXT,
        data TEXT,
        date_submitted TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

def save_form_to_db(form_type, visitor_type, data_dict):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "INSERT INTO forms (form_type, visitor_type, data, date_submitted) VALUES (?, ?, ?, ?)",
        (form_type, visitor_type, json.dumps(data_dict), datetime.datetime.now().isoformat())
    )
    conn.commit()
    form_id = c.lastrowid
    conn.close()
    return form_id

def generate_pdf_bytes(form_id, form_type, visitor_type, data_dict):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    elements.append(Paragraph("<b>UGANDA WILDLIFE AUTHORITY</b>", None))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(f"<b>Form ID:</b> {form_id}", None))
    elements.append(Paragraph(f"<b>Form Type:</b> {form_type}", None))
    elements.append(Paragraph(f"<b>Visitor Type:</b> {visitor_type}", None))
    elements.append(Spacer(1, 8))

    # Flatten data to table-friendly rows
    table_data = [["Field", "Value"]]
    def add_row(k, v):
        if isinstance(v, list):
            vstr = ", ".join([str(x) for x in v])
        elif isinstance(v, dict):
            vstr = json.dumps(v)
        else:
            vstr = str(v)
        table_data.append([k, vstr])

    # Put clients, vehicles, activities first if present
    for key in ["clients", "vehicles", "activities"]:
        if key in data_dict:
            add_row(key.title(), data_dict[key])

    for k, v in data_dict.items():
        if k not in ("clients", "vehicles", "activities"):
            add_row(k, v)

    table = Table(table_data, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.darkgreen),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit_form", methods=["POST"])
def submit_form():
    # form_type (tourist/transit/student), visitor_type (FNR, FR, ROA, EAC, CHILD)
    form_type = request.form.get("form_type", "")
    visitor_type = request.form.get("visitor_type", "")
    # Build structured payload
    payload = {}

    # Clients (client_name[], client_contact[], client_nationality[])
    # If these fields exist, group them
    clients = []
    names = request.form.getlist("client_name[]")
    contacts = request.form.getlist("client_contact[]")
    nationalities = request.form.getlist("client_nationality[]")
    for i in range(max(len(names), len(contacts), len(nationalities))):
        client = {}
        if i < len(names) and names[i].strip():
            client["name"] = names[i].strip()
        if i < len(contacts) and contacts[i].strip():
            client["contact"] = contacts[i].strip()
        if i < len(nationalities) and nationalities[i].strip():
            client["nationality"] = nationalities[i].strip()
        if client:
            clients.append(client)
    if clients:
        payload["clients"] = clients

    # Vehicles (car_type[], car_reg[], driver_name[], driver_phone[])
    vehicle_types = request.form.getlist("car_type[]")
    vehicle_regs = request.form.getlist("car_reg[]")
    driver_names = request.form.getlist("driver_name[]")
    driver_phones = request.form.getlist("driver_phone[]")
    vehicles = []
    for i in range(max(len(vehicle_types), len(vehicle_regs), len(driver_names), len(driver_phones))):
        v = {}
        if i < len(vehicle_types) and vehicle_types[i].strip(): v["type"] = vehicle_types[i].strip()
        if i < len(vehicle_regs) and vehicle_regs[i].strip(): v["reg"] = vehicle_regs[i].strip()
        if i < len(driver_names) and driver_names[i].strip(): v["driver_name"] = driver_names[i].strip()
        if i < len(driver_phones) and driver_phones[i].strip(): v["driver_phone"] = driver_phones[i].strip()
        if v:
            vehicles.append(v)
    if vehicles:
        payload["vehicles"] = vehicles

    # Activities (multiple checkboxes named activities[])
    activities = request.form.getlist("activities")
    if activities:
        payload["activities"] = activities

    # Also save other single fields generically
    for key in request.form:
        if key in ("client_name[]","client_contact[]","client_nationality[]",
                   "car_type[]","car_reg[]","driver_name[]","driver_phone[]",
                   "activities"):
            continue
        if key in ("form_type","visitor_type"):
            continue
        # only include if not already captured
        payload.setdefault("fields", {})
        payload["fields"][key] = request.form.get(key)

    # Persist
    form_id = save_form_to_db(form_type, visitor_type, payload)

    # Generate PDF and return it (also used for printing)
    pdf_buffer = generate_pdf_bytes(form_id, form_type, visitor_type, payload)
    # Return PDF and instruct front-end to auto-open print (front-end handles printing)
    return send_file(pdf_buffer, as_attachment=True, download_name=f"park_entry_{form_id}.pdf", mimetype="application/pdf")

@app.route("/admin")
def admin():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, form_type, visitor_type, date_submitted FROM forms ORDER BY id DESC")
    records = c.fetchall()
    conn.close()
    return render_template("admin.html", records=records)

@app.route("/view/<int:form_id>")
def view_form(form_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM forms WHERE id=?", (form_id,))
    record = c.fetchone()
    conn.close()
    if not record:
        return "Not found", 404
    # record: (id, form_type, visitor_type, data, date_submitted)
    try:
        data = json.loads(record[3])
    except Exception:
        data = {"raw": record[3]}
    return render_template("view_form.html", record=record, record_data=data)

@app.route("/stats")
def stats():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # by visitor_type
    c.execute("SELECT visitor_type, COUNT(*) FROM forms GROUP BY visitor_type")
    by_type = {row[0] if row[0] else "UNKNOWN": row[1] for row in c.fetchall()}

    now = datetime.datetime.now()
    def count_since(days):
        since = (now - datetime.timedelta(days=days)).isoformat()
        c.execute("SELECT COUNT(*) FROM forms WHERE date_submitted >= ?", (since,))
        return c.fetchone()[0]

    periods = {
        "today": count_since(1),
        "week": count_since(7),
        "month": count_since(30),
        "quarter": count_since(90),
        "year": count_since(365)
    }
    conn.close()
    return jsonify({"by_type": by_type, "by_period": periods})

@app.route("/export_csv")
def export_csv():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, form_type, visitor_type, data, date_submitted FROM forms ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id","form_type","visitor_type","data","date_submitted"])
    for r in rows:
        writer.writerow([r[0], r[1], r[2], r[3], r[4]])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), as_attachment=True, download_name="forms_export.csv", mimetype="text/csv")

@app.route("/search")
def search():
    # Query params: q (text), type (visitor_type), from_date, to_date
    q = request.args.get("q", "").strip()
    vtype = request.args.get("type", "").strip()
    from_date = request.args.get("from")
    to_date = request.args.get("to")
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    base = "SELECT id, form_type, visitor_type, date_submitted, data FROM forms WHERE 1=1"
    params = []
    if vtype:
        base += " AND visitor_type = ?"
        params.append(vtype)
    if from_date:
        base += " AND date_submitted >= ?"
        params.append(from_date)
    if to_date:
        base += " AND date_submitted <= ?"
        params.append(to_date)
    c.execute(base + " ORDER BY id DESC", params)
    rows = c.fetchall()
    results = []
    for r in rows:
        # If q in name or nationality or other fields, include
        include = True
        if q:
            text = json.dumps(r[4]).lower()
            include = q.lower() in text
        if include:
            results.append({"id": r[0], "form_type": r[1], "visitor_type": r[2], "date_submitted": r[3]})
    conn.close()
    return jsonify(results)

if _name_ == "_main_":
    app.run(host="0.0.0.0", port=5000, debug=True)