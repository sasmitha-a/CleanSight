import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.cluster import DBSCAN

def detect_univariate_outliers(df: pd.DataFrame) -> dict:
    results = {}

    numeric_cols = df.select_dtypes(include=['number']).columns

    for col in numeric_cols:
        col_data = df[col].dropna()

        z_scores = (col_data - col_data.mean()) / col_data.std()
        z_outliers = col_data[np.abs(z_scores) > 3].index.tolist()

        # IQR method
        q1 = col_data.quantile(0.25)
        q3 = col_data.quantile(0.75)
        iqr = q3 - q1
        iqr_outliers = col_data[((col_data < (q1 - 1.5 * iqr)) | (col_data > (q3 + 1.5 * iqr)))].index.tolist()

        # Modified Z-score
        median = col_data.median()
        mad = np.median(np.abs(col_data - median))
        mod_z_scores = 0.6745 * (col_data - median) / mad if mad != 0 else np.zeros_like(col_data)
        mod_z_outliers = col_data[np.abs(mod_z_scores) > 3.5].index.tolist()

        results[col] = {
            'z_score_outliers': z_outliers,
            'iqr_outliers': iqr_outliers,
            'modified_z_outliers': mod_z_outliers
        }

    return results


def detect_multivariate_outliers(df: pd.DataFrame) -> dict:
    results = {}

    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) < 2:
        results['message'] = 'Not enough numeric features for multivariate detection'
        return results

    X = df[numeric_cols].fillna(0)

    # Isolation Forest
    iso = IsolationForest(contamination=0.05, random_state=42)
    iso_labels = iso.fit_predict(X)
    iso_outliers = X[iso_labels == -1].index.tolist()
    results['isolation_forest_outliers'] = iso_outliers

    # Local Outlier Factor (LOF)
    lof = LocalOutlierFactor(n_neighbors=20, contamination=0.05)
    lof_labels = lof.fit_predict(X)
    lof_outliers = X[lof_labels == -1].index.tolist()
    results['lof_outliers'] = lof_outliers

    # Clustering (DBSCAN)
    db = DBSCAN(eps=1.5, min_samples=5)
    db_labels = db.fit_predict(X)
    db_outliers = X[db_labels == -1].index.tolist()
    results['dbscan_outliers'] = db_outliers

    return results
