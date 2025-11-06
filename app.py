# server.py
from flask import Flask, request, send_file, jsonify, render_template_string, safe_join
from flask_cors import CORS
import sqlite3, os, datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(_name_, static_folder='uploads')
CORS(app)

DB = "park_entry.db"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        client_name TEXT,
        client_contact TEXT,
        client_nationality TEXT,
        car_type TEXT,
        car_reg TEXT,
        driver_name TEXT,
        driver_phone TEXT,
        activities TEXT,
        group_file TEXT,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/submit", methods=["POST"])
def submit():
    form = request.form
    files = request.files
    category = form.get("form_type", "tourist")

    # Collect lists (safe even if not present)
    client_names = form.getlist("client_name[]")
    contacts = form.getlist("client_contact[]")
    nationalities = form.getlist("client_nationality[]")

    car_types = form.getlist("car_type[]")
    car_regs = form.getlist("car_reg[]")
    driver_names = form.getlist("driver_name[]")
    driver_phones = form.getlist("driver_phone[]")

    # For transit/student single fields
    if category == "transit":
        client_names = [form.get("transit_name", "")]
        contacts = [""]
        nationalities = [form.get("transit_nationality", "")]
        car_regs = [form.get("transit_reg", "")]
        car_types = [form.get("transit_reg", "")]
    if category == "student":
        client_names = [form.get("student_name", "")]
        contacts = [""]
        nationalities = [form.get("student_nationality", "")]
        # other fields remain blank

    activities = ", ".join(form.getlist("activities"))

    # Handle uploaded group file
    group_file = files.get("group_upload")
    saved_group_filename = None
    if group_file and group_file.filename:
        # sanitize filename in simple way
        safe_name = f"{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}{group_file.filename.replace(' ', '')}"
        path = os.path.join(UPLOAD_DIR, safe_name)
        group_file.save(path)
        saved_group_filename = safe_name

    # Save entries: if multiple clients, create a row for each (or at least first)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    now = datetime.datetime.utcnow().isoformat()
    max_rows = max(1, len(client_names))
    for i in range(max_rows):
        cn = client_names[i] if i < len(client_names) else ""
        ct = contacts[i] if i < len(contacts) else ""
        nat = nationalities[i] if i < len(nationalities) else ""
        car = car_types[i] if i < len(car_types) else (car_types[0] if car_types else "")
        reg = car_regs[i] if i < len(car_regs) else (car_regs[0] if car_regs else "")
        drv = driver_names[i] if i < len(driver_names) else (driver_names[0] if driver_names else "")
        drvphone = driver_phones[i] if i < len(driver_phones) else (driver_phones[0] if driver_phones else "")

        cur.execute("""
        INSERT INTO entries (category, client_name, client_contact, client_nationality, car_type, car_reg, driver_name, driver_phone, activities, group_file, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (category, cn, ct, nat, car, reg, drv, drvphone, activities, saved_group_filename, now))
    conn.commit()
    conn.close()

    # Build PDF receipt
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = []

    # Add logo if exists
    logo_path = os.path.join(os.getcwd(), "uwa_logo.png")
    if os.path.exists(logo_path):
        try:
            im = Image(logo_path, width=80, height=80)
            story.append(im)
        except Exception as e:
            # ignore image errors
            print("Logo error:", e)

    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Uganda Wildlife Authority</b>", styles["Title"]))
    story.append(Paragraph("Murchison Falls National Park", styles["Normal"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>PARK ENTRY RECEIPT - {category.title()}</b>", styles["Heading2"]))
    story.append(Spacer(1, 8))

    # Clients table
    client_data = [["Client Name", "Contact", "Nationality"]]
    for i in range(len(client_names)):
        client_data.append([client_names[i], contacts[i] if i < len(contacts) else "", nationalities[i] if i < len(nationalities) else ""])
    if len(client_data) == 1:
        client_data.append(["-", "-", "-"])

    tbl = Table(client_data, colWidths=[200, 120, 120])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgreen),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold")
    ]))
    story.append(tbl)
    story.append(Spacer(1, 10))

    # Vehicles table (if any)
    if any(car_types) or any(car_regs):
        vehicle_data = [["Car Type", "Reg. Number", "Driver Name", "Driver Phone"]]
        max_v = max(len(car_types), len(car_regs), len(driver_names), len(driver_phones))
        for i in range(max_v):
            vehicle_data.append([
                car_types[i] if i < len(car_types) else "",
                car_regs[i] if i < len(car_regs) else "",
                driver_names[i] if i < len(driver_names) else "",
                driver_phones[i] if i < len(driver_phones) else ""
            ])
        vtbl = Table(vehicle_data, colWidths=[120, 100, 160, 100])
        vtbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold")
        ]))
        story.append(Paragraph("<b>Vehicle Details</b>", styles["Heading3"]))
        story.append(vtbl)
        story.append(Spacer(1, 10))

    # Activities
    story.append(Paragraph(f"<b>Activities:</b> {activities}", styles["Normal"]))
    story.append(Spacer(1, 12))
    if saved_group_filename:
        story.append(Paragraph(f"Group upload file: {saved_group_filename}", styles["Normal"]))
        story.append(Spacer(1, 6))

    story.append(Paragraph("Thank you for visiting Uganda Wildlife Authority!", styles["Normal"]))
    doc.build(story)
    buffer.seek(0)

    return send_file(buffer, mimetype="application/pdf", as_attachment=False, download_name="park_entry_receipt.pdf")


# Simple dashboard to view entries (for admin)
@app.route("/view_entries")
def view_entries():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id, category, client_name, client_contact, client_nationality, car_reg, activities, group_file, created_at FROM entries ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()

    html = """
    <h2>Entries</h2>
    <table border="1" cellpadding="6" cellspacing="0">
      <tr><th>ID</th><th>Category</th><th>Name</th><th>Contact</th><th>Nationality</th><th>Car Reg</th><th>Activities</th><th>Group File</th><th>Created</th></tr>
      {% for r in rows %}
      <tr>
        <td>{{r[0]}}</td><td>{{r[1]}}</td><td>{{r[2]}}</td><td>{{r[3]}}</td><td>{{r[4]}}</td><td>{{r[5]}}</td>
        <td>{{r[6]}}</td>
        <td>{% if r[7] %}<a href="/uploads/{{r[7]}}" target="_blank">Download</a>{% else %}-{% endif %}</td>
        <td>{{r[8]}}</td>
      </tr>
      {% endfor %}
    </table>
    """
    return render_template_string(html, rows=rows)

if _name_ == "_main_":
    app.run(host="0.0.0.0", port=5000, debug=True)