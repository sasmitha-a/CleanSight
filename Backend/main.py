from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import tempfile
import os
import uuid
import io

from data_checker import generate_data_quality_report
from anamoly_detector import detect_univariate_outliers, detect_multivariate_outliers
from report_generator import generate_report
from preprocessed_data import generate_preprocessed_dataset

# Ensure the uploads directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

# CORS for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze/")
async def analyze(file: UploadFile = File(None), pasted_data: str = Form(None)):
    df = None

    # Case 1: If a file is uploaded
    if file:
        file_ext = os.path.splitext(file.filename)[-1].lower()
        try:
            if file_ext == '.csv':
                df = pd.read_csv(io.BytesIO(await file.read()))
            elif file_ext in ['.xls', '.xlsx']:
                df = pd.read_excel(io.BytesIO(await file.read()))
            elif file_ext == '.json':
                df = pd.read_json(io.BytesIO(await file.read()))
            else:
                return JSONResponse(status_code=400, content={"error": "Unsupported file format. Please upload CSV, Excel, or JSON files."})
        except Exception as e:
            return JSONResponse(status_code=400, content={"error": f"Failed to read file: {str(e)}"})

    # Case 2: If pasted data is provided
    elif pasted_data:
        try:
            # Check if data uses tabs (Excel-style) or commas
            delimiter = '\t' if '\t' in pasted_data else ','
            df = pd.read_csv(io.StringIO(pasted_data), delimiter=delimiter)
            print("Parsed pasted data as CSV with delimiter:", delimiter)
        except Exception as e_csv:
            print("CSV parsing failed:", e_csv)
            try:
                df = pd.read_json(io.StringIO(pasted_data))
                print("Parsed pasted data as JSON.")
            except Exception as e_json:
                print("JSON parsing failed:", e_json)
                return JSONResponse(status_code=400, content={"error": "Pasted data must be in CSV or JSON format. Please upload Excel files instead."})

    else:
        return JSONResponse(status_code=400, content={"error": "Please upload a file or paste your data."})

    # Generate unique report_id
    report_id = str(uuid.uuid4())

    # Preprocessed Dataset
    preprocessed_df = generate_preprocessed_dataset(df)
    preprocessed_filename = os.path.join(UPLOAD_DIR, f"PreprocessedData_{report_id}.csv")
    preprocessed_df.to_csv(preprocessed_filename, index=False)
    print("Saving preprocessed file at:", preprocessed_filename)

    # Data Quality Report
    data_profile = generate_data_quality_report(df)

    # Outlier Detection
    univariate_outliers = detect_univariate_outliers(df)
    multivariate_outliers = detect_multivariate_outliers(df)
    outliers = {
        "univariate": univariate_outliers,
        "multivariate": multivariate_outliers
    }

    # Prepare data_profile for report
    overview = {
        "Rows": df.shape[0],
        "Columns": df.shape[1]
    }
    columns = {}
    for col in df.columns:
        columns[col] = {
            "missing_values": data_profile["missing_values"].get(col, 0),
            "missing_percentage": data_profile["missing_percentage"].get(col, 0),
            "data_type": data_profile["data_types"].get(col, "unknown"),
            "stats": data_profile["numeric_summary"].get(col, {})
        }
    data_profile_for_report = {
        "overview": overview,
        "columns": columns
    }

    # Generate unique report filename
    report_filename = os.path.join(UPLOAD_DIR, f"DataQualityReport_{report_id}.pdf")
    generate_report(data_profile_for_report, outliers, df, filename=report_filename)

    summary = f"Dataset contains {overview['Rows']} rows and {overview['Columns']} columns."
    MISSING_WEIGHT = 0.6
    OUTLIER_WEIGHT = 0.4

    total_cells = df.shape[0] * df.shape[1]
    missing_values = int(sum(data_profile['missing_values'].values()))
    unique_outlier_indices = set()

    for indices in univariate_outliers.values():
        unique_outlier_indices.update(indices)

    for indices in multivariate_outliers.values():
        if isinstance(indices, list):
            unique_outlier_indices.update(indices)

    outlier_count = len(unique_outlier_indices)

    # Scores
    total_cells = df.shape[0] * df.shape[1]
    missing_score = 100 - (missing_values / total_cells * 100) if total_cells else 100
    outlier_score = 100 - (outlier_count / total_cells * 100) if total_cells else 100
    
    data_quality_score = int(MISSING_WEIGHT * missing_score + OUTLIER_WEIGHT * outlier_score)
    data_quality_score = max(0, min(100, data_quality_score))

    recommendations = []
    if missing_values > 0:
        recommendations.append(f"Remove or impute {missing_values} missing values.")
    if outlier_count > 0:
        recommendations.append(f"Investigate {outlier_count} outliers detected.")
    if data_quality_score < 90:
        recommendations.append("Consider further cleaning for higher data quality.")

    return {
        "report_id": report_id,
        "summary": summary,
        "data_quality": data_quality_score,
        "missing_values": missing_values,
        "outliers": outlier_count,
        "recommendations": recommendations,
    }


@app.get("/download-report/{report_id}")
def download_report(report_id: str):
    report_filename = os.path.join(UPLOAD_DIR, f"DataQualityReport_{report_id}.pdf")
    if not os.path.exists(report_filename):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(
        path=report_filename,
        filename="DataQualityReport.pdf",
        media_type="application/pdf"
    )

@app.get("/download-preprocessed/{report_id}")
def download_preprocessed(report_id: str):
    preprocessed_filename = os.path.join(UPLOAD_DIR, f"PreprocessedData_{report_id}.csv")
    if not os.path.exists(preprocessed_filename):
        raise HTTPException(status_code=404, detail="Preprocessed dataset not found")
    return FileResponse(
        path=preprocessed_filename,
        filename="PreprocessedDataset.csv",
        media_type="text/csv"
    )