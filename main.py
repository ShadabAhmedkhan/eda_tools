from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from ydata_profiling import ProfileReport
import pandas as pd
import uuid
import shutil
import os

app = FastAPI()

UPLOAD_DIR = "uploads"
REPORT_DIR = "reports"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

app.mount("/reports", StaticFiles(directory=REPORT_DIR), name="reports")


@app.get("/", response_class=HTMLResponse)
async def upload_form(report_url: str = ""):
    iframe_html = ""
    if report_url:
        # Generate a unique report URL for the iframe
        report_url = f"/reports/{report_url.split('/')[-1]}"
    iframe_html = f"""
    <br><br>
    <a href="{report_url}" download target="_blank">
    <button type="button">Download Report</button>
    </a>
    <br><br>
    <h3>Profiling Report:</h3>
    <iframe src="{report_url}" width="100%" height="800px"></iframe>
    """ if report_url else ""

    return f"""
    <html>
        <head>
            <title>CSV Profiling</title>
        </head>
        <body>
            <h2>Upload a CSV file</h2>
            <form action="/profile" enctype="multipart/form-data" method="post">
                <input name="file" type="file" accept=".csv">
                <input type="submit" value="Generate Report">
            </form>
            <br>
            {iframe_html}
        </body>
    </html>
    """


@app.post("/profile", response_class=HTMLResponse)
async def generate_profile(file: UploadFile = File(...)):
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        df = pd.read_csv(file_path)
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="latin1")

    report_id = str(uuid.uuid4())
    report_filename = f"report_{report_id}.html"
    report_path = f"{REPORT_DIR}/{report_filename}"

    profile = ProfileReport(df, title="YData Profiling Report", explorative=True)
    profile.to_file(report_path)

    return await upload_form(report_url=f"/reports/{report_filename}")
