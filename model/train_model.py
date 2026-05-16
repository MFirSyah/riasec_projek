"""
train_model.py — Training script for RIASEC Career Recommendation Model
========================================================================
Script ini melatih Random Forest Classifier menggunakan dataset
riasec_academic_68programs.csv dan menyimpan model serta scaler.
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

# === Konfigurasi ===
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', '01_riasec_academic_68programs.csv')
MODEL_DIR = os.path.dirname(__file__)
RF_MODEL_PATH = os.path.join(MODEL_DIR, 'rf_model.pkl')
SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.pkl')

# 16 fitur sesuai AGENTS.md
FEATURE_COLUMNS = [
    'riasec_r', 'riasec_i', 'riasec_a', 'riasec_s', 'riasec_e', 'riasec_c',
    'bahasa_indonesia', 'bahasa_inggris', 'matematika', 'informatika',
    'ipa', 'ips', 'ppkn', 'penjas', 'seni', 'gpa'
]
TARGET_COLUMN = 'program_id'


def load_data(path: str) -> pd.DataFrame:
    """Load dataset dari file CSV."""
    df = pd.read_csv(path)
    print(f"[INFO] Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"[INFO] Unique program_id (classes): {df[TARGET_COLUMN].nunique()}")
    return df


def prepare_data(df: pd.DataFrame):
    """Pisahkan fitur dan target, lalu split train/test."""
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"[INFO] Train size: {len(X_train)}, Test size: {len(X_test)}")
    return X_train, X_test, y_train, y_test


def scale_features(X_train: pd.DataFrame, X_test: pd.DataFrame) -> tuple:
    """StandardScaler fit pada train, transform pada train dan test."""
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Simpan scaler
    scaler_path = SCALER_PATH
    joblib.dump(scaler, scaler_path)
    print(f"[INFO] Scaler saved to: {scaler_path}")

    return X_train_scaled, X_test_scaled, scaler


def train_model(X_train_scaled: np.ndarray, y_train: pd.Series) -> RandomForestClassifier:
    """Train RandomForestClassifier dengan konfigurasi sesuai AGENTS.md."""
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight='balanced',
        n_jobs=-1  # gunakan semua core CPU
    )
    model.fit(X_train_scaled, y_train)
    print(f"[INFO] Model trained with {len(model.estimators_)} trees")
    return model


def evaluate_model(model: RandomForestClassifier, X_test_scaled: np.ndarray,
                   y_test: pd.Series) -> dict:
    """Evaluasi model dan return metrics."""
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"\n{'='*60}")
    print(f"MODEL EVALUATION RESULTS")
    print(f"{'='*60}")
    print(f"Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")

    # Classification report (hanya tampilkan beberapa baris pertama)
    print(f"\nClassification Report (sample):")
    report = classification_report(y_test, y_pred, zero_division=0)
    print(report)

    return {'accuracy': accuracy, 'report': report}


def save_model(model: RandomForestClassifier) -> str:
    """Simpan model ke file .pkl."""
    model_path = RF_MODEL_PATH
    joblib.dump(model, model_path)
    print(f"[INFO] Model saved to: {model_path}")
    return model_path


def main():
    print("="*60)
    print("RIASEC Career Model Training")
    print("="*60)

    # 1. Load data
    df = load_data(DATA_PATH)

    # 2. Prepare data
    X_train, X_test, y_train, y_test = prepare_data(df)

    # 3. Scale features
    X_train_scaled, X_test_scaled, scaler = scale_features(X_train, X_test)

    # 4. Train model
    model = train_model(X_train_scaled, y_train)

    # 5. Evaluate model
    metrics = evaluate_model(model, X_test_scaled, y_test)

    # 6. Save model
    model_path = save_model(model)

    # Summary
    print(f"\n{'='*60}")
    print("TRAINING COMPLETE")
    print(f"{'='*60}")
    print(f"Model file: {model_path}")
    print(f"Scaler file: {SCALER_PATH}")
    print(f"Accuracy: {metrics['accuracy']*100:.2f}%")
    print(f"\nNext step: Model siap digunakan oleh utils/predict.py")


if __name__ == '__main__':
    main()