from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import sqlite3, io, datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

app = Flask(_name_)
CORS(app)

# ----------------- DATABASE SETUP -----------------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS forms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    form_type TEXT,
                    data TEXT,
                    date_submitted TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# ----------------- FORM SUBMISSION -----------------
@app.route("/submit_form", methods=["POST"])
def submit_form():
    form_type = request.form.get("form_type")
    data = dict(request.form)
    del data["form_type"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO forms (form_type, data, date_submitted) VALUES (?, ?, ?)",
              (form_type, str(data), str(datetime.datetime.now())))
    conn.commit()
    conn.close()

    # Generate instant PDF receipt
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
    elements = []
    elements.append(Paragraph("<b>UGANDA WILDLIFE AUTHORITY</b>", None))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>Visitor Category:</b> {form_type.title()}", None))
    elements.append(Spacer(1, 12))

    table_data = [["Field", "Value"]] + [[k, v] for k, v in data.items()]
    table = Table(table_data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)
    pdf_buffer.seek(0)

    return send_file(pdf_buffer, as_attachment=True, download_name="park_entry_receipt.pdf", mimetype="application/pdf")

# ----------------- ADMIN DASHBOARD -----------------
@app.route("/admin")
def admin():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT id, form_type, date_submitted FROM forms ORDER BY id DESC")
    records = c.fetchall()
    conn.close()
    return render_template("admin.html", records=records)

# ----------------- VIEW SINGLE RECORD -----------------
@app.route("/view/<int:form_id>")
def view_form(form_id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM forms WHERE id=?", (form_id,))
    record = c.fetchone()
    conn.close()
    return jsonify(record)

if _name_ == "_main_":
    app.run(host="0.0.0.0", port=5000, debug=True)