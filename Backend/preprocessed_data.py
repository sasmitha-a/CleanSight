import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.impute import SimpleImputer

def generate_preprocessed_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df_clean = df.copy()

    # Clean column names
    df_clean.columns = df_clean.columns.str.strip().str.lower().str.replace(' ', '_').str.replace(r'[^a-zA-Z0-9_]', '', regex=True)

    # Identify numeric and categorical columns
    num_cols = df_clean.select_dtypes(include=['number']).columns
    cat_cols = df_clean.select_dtypes(include=['object', 'category']).columns

    # Impute missing values
    if len(num_cols) > 0:
        num_imputer = SimpleImputer(strategy='mean')
        df_clean[num_cols] = num_imputer.fit_transform(df_clean[num_cols])

    if len(cat_cols) > 0:
        cat_imputer = SimpleImputer(strategy='most_frequent')
        df_clean[cat_cols] = cat_imputer.fit_transform(df_clean[cat_cols])

    # Remove duplicates
    df_clean = df_clean.drop_duplicates()

    # Encode categorical features
    label_enc = LabelEncoder()
    for col in cat_cols:
        try:
            df_clean[col] = label_enc.fit_transform(df_clean[col].astype(str))
        except Exception as e:
            print(f"Label encoding failed for {col}: {e}")

    # Scale numeric features
    if len(num_cols) > 0:
        scaler = MinMaxScaler()
        df_clean[num_cols] = scaler.fit_transform(df_clean[num_cols])

    return df_clean
