# CleanSight: Data Quality & Preprocessing Toolkit

CleanSight is a powerful tool that allows users to analyze, preprocess, and download high-quality datasets with just a few clicks. Built with FastAPI (backend) and Next.js (frontend), it simplifies the data cleaning process for analysts, developers, and data scientists.



## Features

- Upload datasets in CSV, Excel formats.  
- Paste datasets directly in the UI (CSV/JSON)  
- Data Quality Report with:
  - Missing values
  - Column-wise stats
  - Outlier detection and Visualizations

- Preprocessing pipeline with:
  - Column cleaning
  - Imputation for missing values 
  - Label Encoding for categorical features
  - Min-Max Scaling for numerical features

- Download: Data Quality Report (PDF), Preprocessed Dataset (CSV)



## Tech Stack

- Backend: FastAPI, Pandas, scikit-learn, Seaborn, Matplotlib, FPDF
- Frontend: Next.js + Tailwind + Shadcn/UI
- Data Formats: CSV, Excel, JSON(pasted)



## How It Works

Clone the repository:

  ```bash
  git clone https://github.com/your-username/cleansight.git
  cd cleansight
```



## Set Up Locally By

Backend Setup

  ```bash
  cd backend
  python -m venv venv
  source venv/bin/activate  # For Linux/Mac
  venv\Scripts\activate     # For Windows
  pip install -r requirements.txt
  uvicorn main:app --reload
```

Backend runs at http://localhost:8000.


Frontend Setup

  ```bash
  cd ../frontend
  npm install
  npm run dev
```

Frontend runs at http://localhost:5173.

