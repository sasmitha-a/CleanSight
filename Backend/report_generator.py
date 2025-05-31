import pandas as pd
from fpdf import FPDF
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
import hashlib
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

def safe_filename(text, max_length=50):
    safe = re.sub(r'[^\w\-_\. ]', '_', text)
    if len(safe) > max_length:
        hash_suffix = hashlib.md5(safe.encode()).hexdigest()[:8]
        safe = safe[:max_length] + "_" + hash_suffix
    return safe

def generate_report(data_profile: dict, outliers: dict, df: pd.DataFrame, filename="DataQualityReport.pdf"):
    os.makedirs("temp_plots", exist_ok=True)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title & Branding
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 10, "CleanSight", ln=True, align="C")
    pdf.set_font("Arial", '', 14)
    pdf.cell(0, 10, "Data Quality Report", ln=True, align="C")
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)

    pdf.ln(10)

    # Dataset Overview
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. Dataset Overview", ln=True)
    pdf.set_font("Arial", '', 12)
    for k, v in data_profile['overview'].items():
        pdf.cell(0, 8, f"{k}: {v}", ln=True)

    pdf.ln(5)

    # Column-wise Statistics
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "2. Column-wise Statistics", ln=True)

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(50, 8, "Feature", 1)
    pdf.cell(30, 8, "Data Type", 1)
    pdf.cell(30, 8, "Missing %", 1)
    pdf.cell(30, 8, "Mean", 1)
    pdf.cell(30, 8, "Std", 1)
    pdf.ln()

    pdf.set_font("Arial", '', 9)
    for col, stats in data_profile['columns'].items():
        pdf.cell(50, 8, col[:20], 1)
        pdf.cell(30, 8, str(stats.get('data_type', '')), 1)
        pdf.cell(30, 8, str(stats.get('missing_percentage', '')), 1)
        mean = stats.get('stats', {}).get('mean', '-')
        std = stats.get('stats', {}).get('std', '-')
        pdf.cell(30, 8, f"{mean:.2f}" if isinstance(mean, (float, int)) else '-', 1)
        pdf.cell(30, 8, f"{std:.2f}" if isinstance(std, (float, int)) else '-', 1)
        pdf.ln()

    pdf.ln(5)

    # Outlier Visuals
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "3. Outlier Analysis (Visuals)", ln=True)

    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        if df[col].dropna().empty:
            continue

        plt.figure(figsize=(4, 2))
        sns.boxplot(x=df[col].dropna())
        plt.title(f"Boxplot - {col}")
        plt.tight_layout()

        safe_col = safe_filename(col)
        plot_path = f"temp_plots/{safe_col}_boxplot.png"
        plt.savefig(plot_path)
        plt.close()

        pdf.image(plot_path, w=90)
        pdf.ln(3)

    # Isolation Forest Scatter
    if len(numeric_cols) >= 2:
        try:
            X = df[numeric_cols].fillna(0)
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            iso = IsolationForest(contamination=0.05, random_state=42)
            y_pred = iso.fit_predict(X_scaled)

            plt.figure(figsize=(4, 3))
            plt.scatter(X_scaled[:, 0], X_scaled[:, 1], c=y_pred, cmap='coolwarm', s=10)
            plt.title("Isolation Forest Outliers")
            plt.xlabel(numeric_cols[0])
            plt.ylabel(numeric_cols[1])
            plt.tight_layout()
            plot_path = "temp_plots/isolation_forest.png"
            plt.savefig(plot_path)
            plt.close()

            pdf.image(plot_path, w=120)
            pdf.ln(5)
        except Exception as e:
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 8, f"Isolation Forest plot error: {e}", ln=True)

    # Clean up temp plots
    for f in os.listdir("temp_plots"):
        os.remove(os.path.join("temp_plots", f))

    pdf.output(filename)
    print(f"Report generated: {filename}")
