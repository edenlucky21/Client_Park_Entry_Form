from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import sqlite3
import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
CORS(app)

# Create database if not exists
if not os.path.exists("park_entry.db"):
    conn = sqlite3.connect("park_entry.db")
    conn.execute("""
    CREATE TABLE entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT,
        client_contact TEXT,
        client_nationality TEXT,
        car_type TEXT,
        car_reg TEXT,
        driver_name TEXT,
        driver_phone TEXT,
        activities TEXT
    )
    """)
    conn.close()


@app.route("/submit", methods=["POST"])
def submit():
    conn = sqlite3.connect("park_entry.db")
    cur = conn.cursor()

    client_names = request.form.getlist("client_name[]")
    contacts = request.form.getlist("client_contact[]")
    nationalities = request.form.getlist("client_nationality[]")
    car_types = request.form.getlist("car_type[]")
    car_regs = request.form.getlist("car_reg[]")
    driver_names = request.form.getlist("driver_name[]")
    driver_phones = request.form.getlist("driver_phone[]")
    activities = ", ".join(request.form.getlist("activities"))

    # Save data
    for i in range(len(client_names)):
        cur.execute("""
        INSERT INTO entries (client_name, client_contact, client_nationality, car_type, car_reg, driver_name, driver_phone, activities)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            client_names[i],
            contacts[i],
            nationalities[i],
            car_types[i] if i < len(car_types) else car_types[0] if car_types else None,
            car_regs[i] if i < len(car_regs) else car_regs[0] if car_regs else None,
            driver_names[i] if i < len(driver_names) else driver_names[0] if driver_names else None,
            driver_phones[i] if i < len(driver_phones) else driver_phones[0] if driver_phones else None,
            activities
        ))

    conn.commit()
    conn.close()

    # Generate PDF receipt
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    title = Paragraph("<b>Uganda Wildlife Authority</b><br/>Murchison Falls National Park<br/><br/><b>PARK ENTRY RECEIPT</b>", styles["Title"])
    story.append(title)
    story.append(Spacer(1, 0.2 * inch))

    # Table for clients
    client_data = [["Client Name", "Contact", "Nationality"]]
    for i in range(len(client_names)):
        client_data.append([client_names[i], contacts[i], nationalities[i]])

    client_table = Table(client_data, colWidths=[2.5 * inch, 2 * inch, 2 * inch])
    client_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgreen),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")
    ]))

    story.append(Paragraph("<b>Client Details:</b>", styles["Heading2"]))
    story.append(client_table)
    story.append(Spacer(1, 0.3 * inch))

    # Vehicle details
    vehicle_data = [["Car Type", "Reg. Number", "Driver Name", "Driver Phone"]]
    for i in range(len(car_types)):
        vehicle_data.append([
            car_types[i] if i < len(car_types) else "",
            car_regs[i] if i < len(car_regs) else "",
            driver_names[i] if i < len(driver_names) else "",
            driver_phones[i] if i < len(driver_phones) else ""
        ])

    vehicle_table = Table(vehicle_data, colWidths=[1.5 * inch, 1.5 * inch, 2 * inch, 2 * inch])
    vehicle_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")
    ]))

    story.append(Paragraph("<b>Vehicle Details:</b>", styles["Heading2"]))
    story.append(vehicle_table)
    story.append(Spacer(1, 0.3 * inch))

    # Activities
    story.append(Paragraph(f"<b>Activities:</b> {activities}", styles["Normal"]))
    story.append(Spacer(1, 0.4 * inch))

    story.append(Paragraph("<b>Thank you for visiting Uganda Wildlife Authority!</b>", styles["Normal"]))

    doc.build(story)
    pdf_buffer.seek(0)

    return send_file(pdf_buffer, mimetype="application/pdf", as_attachment=False, download_name="park_entry_receipt.pdf")


if __name__ == "__main__":
    app.run(debug=True)