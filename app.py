from flask import Flask, render_template, request, jsonify, send_file
from ultralytics import YOLO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
import os
from datetime import datetime

app = Flask(__name__)

# Load YOLO model
model = YOLO('models/eye_model.pt')

# Ensure folders exist
os.makedirs('static/images', exist_ok=True)
os.makedirs('static/reports', exist_ok=True)

# Homepage
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

# API for detection
@app.route('/api/detect', methods=['POST'])
def api_detect():
    patient_name = request.form['patientName']
    patient_id = request.form['patientId']
    patient_age = request.form['patientAge']

    # Save uploaded image
    file = request.files['eyeImage']
    image_path = f'static/images/{file.filename}'
    file.save(image_path)

    # Predict disease
    results = model(image_path)
    diseases = []
    overall_confidence = 0

    for box in results[0].boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0]) * 100
        disease_name = model.names[class_id]
        diseases.append({'name': disease_name, 'confidence': confidence})
        overall_confidence += confidence

    overall_confidence = overall_confidence / len(diseases) if diseases else 100

    # Create styled PDF
    report_file = f'static/reports/{patient_id}_report.pdf'
    create_pdf(report_file, patient_name, patient_id, patient_age, diseases, overall_confidence, image_path)

    return jsonify({
        'diseases': diseases,
        'overallConfidence': overall_confidence,
        'imageQuality': 'Good',
        'riskLevel': 'Low',
        'reportUrl': report_file
    })

# PDF generation function
def create_pdf(filename, name, pid, age, diseases, confidence, image_path):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Styles
    styles = getSampleStyleSheet()

    # Header
    c.setFillColor(colors.HexColor('#1E90FF'))  # Dodger blue
    c.setFont("Helvetica-Bold", 20)
    c.drawString(2*cm, height - 2*cm, "ALPHA EYE DIAGNOSIS LAB")
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 12)
    c.drawString(2*cm, height - 2.7*cm, "Eye Disease Detection Center")
    c.drawString(2*cm, height - 3.2*cm, "Contact: +91 9944889390 | Email: alphalab@gmail.com")

    # Draw line under header
    c.setStrokeColor(colors.HexColor('#1E90FF'))
    c.setLineWidth(2)
    c.line(2*cm, height - 3.5*cm, width - 2*cm, height - 3.5*cm)

    # Patient Info Table
    patient_data = [
        ['Patient Name', name],
        ['Patient ID', pid],
        ['Patient Age', age],
        ['Report Date', datetime.now().strftime('%d %b %Y %I:%M %p')]
    ]
    table = Table(patient_data, colWidths=[7*cm, 10*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#87CEFA')),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('ALIGN',(0,0),(-1,-1),'LEFT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (5,5), 2),
        ('BACKGROUND',(0,1),(-1,-1),colors.whitesmoke),
        ('GRID',(0,0),(-1,-1),1,colors.gray)
    ]))
    table.wrapOn(c, width, height)
    table.drawOn(c, 2*cm, height - 6*cm)

    # Image Heading
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor('#1E90FF'))
    c.drawString(2*cm, height - 7*cm, "Patient Eye Image")
    c.setFillColor(colors.black)

    # Uploaded Image
    c.drawImage(image_path, width - 14*cm, height - 13*cm, width=6*cm, height=6*cm)

    # Disease Results Table
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor('#1E90FF'))
    c.drawString(2*cm, height - 14*cm, "Disease Detection Results")
    c.setFillColor(colors.black)

    if diseases:
        disease_data = [['Disease', 'Confidence (%)']]
        for d in diseases:
            disease_data.append([d['name'], f"{d['confidence']:.1f}"])
        disease_table = Table(disease_data, colWidths=[8*cm, 9*cm])
        disease_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#87CEFA')),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 4),
            ('BACKGROUND',(0,1),(-1,-1),colors.whitesmoke),
            ('GRID',(0,0),(-1,-1),1,colors.gray)
        ]))
        disease_table.wrapOn(c, width, height)
        disease_table.drawOn(c, 2*cm, height - 16*cm)
        y_offset = height - 18*cm - len(diseases)*1.2*cm - 0.5*cm
    else:
        c.setFont("Helvetica", 12)
        c.drawString(2*cm, height - 14*cm, "No diseases detected.")
        y_offset = height - 15*cm

    # Overall Confidence
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y_offset, f"Overall Confidence: {confidence:.1f}%")

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(colors.gray)
    c.drawString(2*cm, 2*cm, "Generated by ALPHA EYE DIAGNOSIS LAB")
    c.drawString(2*cm, 1.5*cm, f"Page 1 of 1")

    c.showPage()
    c.save()

# Run Flask
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
