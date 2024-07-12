# import os
# from flask import Flask, render_template, request, send_file
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# import io
# import base64

# app = Flask(__name__)

# UPLOAD_FOLDER = 'uploads'
# ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'json'}

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         if 'file' not in request.files:
#             return render_template('index.html', error='No file part')
#         file = request.files['file']
#         if file.filename == '':
#             return render_template('index.html', error='No selected file')
#         if file and allowed_file(file.filename):
#             filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
#             file.save(filename)
#             return render_template('index.html', filename=file.filename)
#     return render_template('index.html')

# @app.route('/visualize', methods=['POST'])
# def visualize():
#     filename = request.form['filename']
#     filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
#     if filename.endswith('.csv'):
#         df = pd.read_csv(filepath)
#     elif filename.endswith('.xlsx'):
#         df = pd.read_excel(filepath)
#     elif filename.endswith('.json'):
#         df = pd.read_json(filepath)
#     else:
#         return render_template('index.html', error='Unsupported file format')

#     # Generate visualizations
#     visualizations = []
    
#     # Histogram for numeric columns
#     for col in df.select_dtypes(include=['int64', 'float64']).columns:
#         fig = px.histogram(df, x=col, title=f'Histogram of {col}')
#         visualizations.append(fig.to_html(full_html=False))
    
#     # Scatter plot for first two numeric columns
#     numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
#     if len(numeric_cols) >= 2:
#         fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], 
#                          title=f'Scatter plot of {numeric_cols[0]} vs {numeric_cols[1]}')
#         visualizations.append(fig.to_html(full_html=False))
    
#     # Summary statistics
#     summary_stats = df.describe().to_html()

#     return render_template('results.html', visualizations=visualizations, summary_stats=summary_stats)

# @app.route('/download_report')
# def download_report():
#     # Generate a simple PDF report (you may want to use a proper PDF library for more complex reports)
#     buffer = io.BytesIO()
#     buffer.write(b'EDA Report\n\n')
#     buffer.write(b'Summary Statistics:\n')
#     # Add summary statistics and other relevant information here
    
#     buffer.seek(0)
#     return send_file(buffer, as_attachment=True, attachment_filename='eda_report.pdf', mimetype='application/pdf')

# if __name__ == '__main__':
#     app.run(debug=True)


import os
from flask import Flask, render_template, request, send_file, session
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Set a secret key for session management

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'json'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file part')
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error='No selected file')
        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            return render_template('index.html', filename=file.filename)
    return render_template('index.html')

@app.route('/visualize', methods=['POST'])
def visualize():
    filename = request.form['filename']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if filename.endswith('.csv'):
        df = pd.read_csv(filepath)
    elif filename.endswith('.xlsx'):
        df = pd.read_excel(filepath)
    elif filename.endswith('.json'):
        df = pd.read_json(filepath)
    else:
        return render_template('index.html', error='Unsupported file format')

    # Generate visualizations
    visualizations = []
    
    # Histogram for numeric columns
    for col in df.select_dtypes(include=['int64', 'float64']).columns:
        fig = px.histogram(df, x=col, title=f'Histogram of {col}')
        visualizations.append(fig.to_html(full_html=False))
    
    # Scatter plot for first two numeric columns
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    if len(numeric_cols) >= 2:
        fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], 
                         title=f'Scatter plot of {numeric_cols[0]} vs {numeric_cols[1]}')
        visualizations.append(fig.to_html(full_html=False))
    
    # Summary statistics
    summary_stats = df.describe().to_html()

    # Store data in session for PDF generation
    session['summary_stats'] = summary_stats
    session['df_json'] = df.to_json()

    return render_template('results.html', visualizations=visualizations, summary_stats=summary_stats)

@app.route('/download_report')
def download_report():
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Add content to the PDF
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "EDA Report")
    
    p.setFont("Helvetica", 12)
    p.drawString(100, 730, "Summary Statistics:")
    
    # Retrieve data from session
    summary_stats = session.get('summary_stats', 'No data available')
    df = pd.read_json(session.get('df_json', '{}'))
    
    # Add summary statistics
    y_position = 710
    for line in summary_stats.split('\n'):
        if line.strip():
            p.drawString(100, y_position, line.strip())
            y_position -= 15
        if y_position < 50:
            p.showPage()
            y_position = 750
    
    # Add some basic insights
    p.showPage()
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 750, "Basic Insights:")
    p.setFont("Helvetica", 12)
    y_position = 730
    
    # Number of rows and columns
    p.drawString(100, y_position, f"Number of rows: {df.shape[0]}")
    y_position -= 20
    p.drawString(100, y_position, f"Number of columns: {df.shape[1]}")
    y_position -= 20
    
    # Data types
    p.drawString(100, y_position, "Data Types:")
    y_position -= 20
    for col, dtype in df.dtypes.items():
        p.drawString(120, y_position, f"{col}: {dtype}")
        y_position -= 15
        if y_position < 50:
            p.showPage()
            y_position = 750
    
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, 
                     download_name='eda_report.pdf', 
                     mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)