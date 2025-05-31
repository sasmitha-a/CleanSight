import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.preprocessing import PolynomialFeatures

def generate_data_quality_report(df: pd.DataFrame) -> dict:
    report = {}

    # Column header check
    headers_with_trailing_spaces = [col for col in df.columns if col != col.strip()]
    report['columns_with_trailing_spaces'] = headers_with_trailing_spaces

    # Missing values
    missing_count = df.isnull().sum()
    missing_percentage = (df.isnull().mean() * 100).round(2)
    report['missing_values'] = missing_count.to_dict()
    report['missing_percentage'] = missing_percentage.to_dict()

    # Duplicates
    duplicate_rows = df.duplicated().sum()
    report['duplicate_rows'] = int(duplicate_rows)

    # Data types
    data_types = df.dtypes.astype(str)
    report['data_types'] = data_types.to_dict()

    # Basic statistics
    numeric_summary = df.describe().to_dict()
    report['numeric_summary'] = numeric_summary

    # Normalization (Min-Max)
    numeric_cols = df.select_dtypes(include=['number']).columns
    scaler_minmax = MinMaxScaler()
    if not numeric_cols.empty:
        df_minmax = pd.DataFrame(scaler_minmax.fit_transform(df[numeric_cols]), columns=numeric_cols)
        report['normalized_sample'] = df_minmax.head(5).to_dict(orient='records')

    # Standardization (Z-score)
    scaler_standard = StandardScaler()
    if not numeric_cols.empty:
        df_standard = pd.DataFrame(scaler_standard.fit_transform(df[numeric_cols]), columns=numeric_cols)
        report['standardized_sample'] = df_standard.head(5).to_dict(orient='records')

    # Dimensionality Reduction (PCA)
    if len(numeric_cols) > 1:
        pca = PCA(n_components=2)
        pca_result = pca.fit_transform(df[numeric_cols].fillna(0))
        report['pca_explained_variance_ratio'] = pca.explained_variance_ratio_.round(3).tolist()
        report['pca_sample'] = pd.DataFrame(pca_result, columns=['PC1', 'PC2']).head(5).to_dict(orient='records')
    else:
        report['pca_message'] = 'Not enough numeric features for PCA'

    # Feature Encoding (One-Hot + Label)
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    if not cat_cols.empty:
        # Convert all to strings to avoid mixed-type errors
        df[cat_cols] = df[cat_cols].astype(str)

        ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        ohe_result = ohe.fit_transform(df[cat_cols].fillna('Missing'))
        ohe_df = pd.DataFrame(ohe_result, columns=ohe.get_feature_names_out(cat_cols))
        report['one_hot_encoded_sample'] = ohe_df.head(5).to_dict(orient='records')

        label_encoded = {}
        for col in cat_cols:
            le = LabelEncoder()
            df[f"{col}_label"] = le.fit_transform(df[col])
            label_encoded[col] = df[[col, f"{col}_label"]].drop_duplicates().to_dict(orient='records')
        report['label_encoded_mapping'] = label_encoded
    else:
        report['categorical_encoding_message'] = 'No categorical features detected'

    # Interaction Features (PolynomialFeatures degree 2)
    if len(numeric_cols) > 1:
        poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
        poly_result = poly.fit_transform(df[numeric_cols].fillna(0))
        poly_cols = poly.get_feature_names_out(numeric_cols)
        poly_df = pd.DataFrame(poly_result, columns=poly_cols)
        report['interaction_features_sample'] = poly_df.head(5).to_dict(orient='records')
    else:
        report['interaction_message'] = 'Not enough numeric features for interactions'

    return report
