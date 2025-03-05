import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def generate_report(file_path):
    """Generates a summary report from an Excel file."""
    try:
        df = pd.read_excel(file_path, sheet_name=0)
        
        # Generate report content
        report = {
            "columns": df.columns.tolist(),
            "shape": df.shape,
            "summary": df.describe().to_html(),
            "missing_values": df.isnull().sum().to_dict(),
            "sample_data": df.head().to_html()
        }
        return report
    except Exception as e:
        return {"error": str(e)}

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return redirect(request.url)
        
        file = request.files["file"]
        if file.filename == "":
            return redirect(request.url)
        
        if file:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(file_path)
            return redirect(url_for("report", filename=file.filename))

    return render_template("upload.html")

@app.route("/report/<filename>")
def report(filename):
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    report_data = generate_report(file_path)
    
    if "error" in report_data:
        return f"<h3>Error: {report_data['error']}</h3>"
    
    return render_template("report.html", report=report_data)

if __name__ == "__main__":
    app.run(debug=True)