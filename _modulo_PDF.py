from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.pdfgen import canvas

# Create a PDF document
doc = SimpleDocTemplate("reportlab_demo.pdf", pagesize=A4)

# Container for the 'Flowable' objects
elements = []

# Set up a sample stylesheet
styles = getSampleStyleSheet()
styleN = styles['Normal']
styleH = styles['Heading1']

# Add a title
title = "ReportLab Demonstration"
elements.append(Paragraph(title, styleH))

# Add a paragraph
text = "ReportLab is a powerful PDF generation library for Python. " \
       "It allows for the creation of complex PDFs with text, images, " \
       "shapes, tables, and more."
elements.append(Paragraph(text, styleN))

# Add some space
elements.append(Spacer(1, 12))

# Add an image
image_path = "OUTPUT/default1.png"  # Replace with your image path
im = Image(image_path)
im.drawHeight = 5.25 * inch * im.drawHeight / im.drawWidth
im.drawWidth = 5.25 * inch
elements.append(im)

# Explicitly add a new page
elements.append(PageBreak())

# Add a title for the new page
new_page_title = "This is a New Page"
elements.append(Paragraph(new_page_title, styleH))

# Add a table
data = [
    ['Header 1', 'Header 2', 'Header 3'],
    ['Row 1, Col 1', 'Row 1, Col 2', 'Row 1, Col 3'],
    ['Row 2, Col 1', 'Row 2, Col 2', 'Row 2, Col 3'],
    ['Row 3, Col 1', 'Row 3, Col 2', 'Row 3, Col 3'],
]

table = Table(data)
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
]))

elements.append(table)

doc.build(elements)

print("PDF created successfully!")
