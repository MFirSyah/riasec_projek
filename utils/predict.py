"""
predict.py — ML Prediction Functions for RIASEC Career App
==========================================================
Fungsi prediksi dan scoring menggunakan model Random Forest.
"""

import os
import pandas as pd
import joblib

# === Paths ===
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'model')
RF_MODEL_PATH = os.path.join(MODEL_DIR, 'rf_model.pkl')
SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.pkl')
PRODI_INFO_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'prodi_info.csv')

# === Feature columns (sesuai AGENTS.md) ===
FEATURE_COLUMNS = [
    'riasec_r', 'riasec_i', 'riasec_a', 'riasec_s', 'riasec_e', 'riasec_c',
    'bahasa_indonesia', 'bahasa_inggris', 'matematika', 'informatika',
    'ipa', 'ips', 'ppkn', 'penjas', 'seni', 'gpa'
]

# === RIASEC dimension names ===
RIASEC_DIMENSIONS = {
    'r': 'Realistic',
    'i': 'Investigative',
    'a': 'Artistic',
    's': 'Social',
    'e': 'Enterprising',
    'c': 'Conventional'
}

# === Academic subject names ===
SUBJECT_NAMES = {
    'bahasa_indonesia': 'Bahasa Indonesia',
    'bahasa_inggris': 'Bahasa Inggris',
    'matematika': 'Matematika',
    'informatika': 'Informatika',
    'ipa': 'IPA',
    'ips': 'IPS',
    'ppkn': 'PPKn',
    'penjas': 'Penjas',
    'seni': 'Seni',
    'gpa': 'GPA'
}

# === Feature labels for explanation ===
FEATURE_LABELS = {
    'riasec_r': 'Skor Realistic',
    'riasec_i': 'Skor Investigative',
    'riasec_a': 'Skor Artistic',
    'riasec_s': 'Skor Social',
    'riasec_e': 'Skor Enterprising',
    'riasec_c': 'Skor Conventional',
    'bahasa_indonesia': 'Nilai Bahasa Indonesia',
    'bahasa_inggris': 'Nilai Bahasa Inggris',
    'matematika': 'Nilai Matematika',
    'informatika': 'Nilai Informatika',
    'ipa': 'Nilai IPA',
    'ips': 'Nilai IPS',
    'ppkn': 'Nilai PPKn',
    'penjas': 'Nilai Penjas',
    'seni': 'Nilai Seni',
    'gpa': 'Nilai GPA'
}

# === Model & Scaler (lazy loaded) ===
_model = None
_scaler = None
_prodi_info = None


def _load_model():
    """Lazy load model."""
    global _model
    if _model is None:
        _model = joblib.load(RF_MODEL_PATH)
    return _model


def _load_scaler():
    """Lazy load scaler."""
    global _scaler
    if _scaler is None:
        _scaler = joblib.load(SCALER_PATH)
    return _scaler


def _load_prodi_info() -> pd.DataFrame:
    """Lazy load prodi info."""
    global _prodi_info
    if _prodi_info is None:
        _prodi_info = pd.read_csv(PRODI_INFO_PATH)
    return _prodi_info


def _build_feature_vector(riasec_scores: dict, academic_scores: dict) -> pd.DataFrame:
    """Build feature vector from scores.

    Args:
        riasec_scores: {'r': float, 'i': float, 'a': float, 's': float, 'e': float, 'c': float}
        academic_scores: {'bahasa_indonesia': float, ..., 'gpa': float}

    Returns:
        DataFrame with 16 features
    """
    # Map lowercase keys to column names
    riasec_mapping = {
        'r': 'riasec_r', 'i': 'riasec_i', 'a': 'riasec_a',
        's': 'riasec_s', 'e': 'riasec_e', 'c': 'riasec_c'
    }

    features = {}
    for key, col in riasec_mapping.items():
        features[col] = riasec_scores.get(key, 0)

    for col in FEATURE_COLUMNS[6:]:  # Academic features
        features[col] = academic_scores.get(col, 0)

    return pd.DataFrame([features])


def _get_top_features(
    feature_importances: pd.Series,
    input_features: pd.DataFrame,
    top_n: int = 3
) -> list[str]:
    """Generate explanation list for top influential features.

    Logic:
    1. Get top N features by importance
    2. Filter to features where user value > average
    3. Generate human-readable explanation

    Args:
        feature_importances: Feature importance scores from model
        input_features: User's feature values
        top_n: Number of top features to return

    Returns:
        List of explanation strings
    """
    # Sort by importance and get top N
    sorted_importance = feature_importances.sort_values(ascending=False)
    top_features = sorted_importance.head(top_n).index.tolist()

    # Get average values for comparison (using training data mean as reference)
    scaler = _load_scaler()
    prodi_info = _load_prodi_info()

    # Calculate approximate average from prodi info dataset for reference
    # For RIASEC scores, avg is around 50 (0-100 range)
    riasec_avg = 50.0
    # For academic scores, avg is around 70 (0-100 range)
    academic_avg = 70.0

    explanations = []
    for feat in top_features:
        user_value = input_features[feat].values[0]

        # Determine threshold based on feature type
        if feat.startswith('riasec_'):
            threshold = riasec_avg
        else:
            threshold = academic_avg

        label = FEATURE_LABELS.get(feat, feat)

        if user_value > threshold:
            explanations.append(f"Nilai {label} kamu di atas rata-rata")
        elif user_value >= threshold * 0.8:
            explanations.append(f"Skor {label} kamu cukup tinggi")

    # If we don't have enough explanations, add generic ones
    if len(explanations) < top_n:
        for feat in top_features[len(explanations):top_n]:
            label = FEATURE_LABELS.get(feat, feat)
            if feat.startswith('riasec_'):
                dim_key = feat.split('_')[1]
                dim_name = RIASEC_DIMENSIONS.get(dim_key, feat)
                explanations.append(f"Skor {dim_name} kamu berkontribusi pada rekomendasi ini")
            else:
                explanations.append(f"Nilai {label} kamu mendukung rekomendasi ini")

    return explanations[:top_n]


def predict_top5(
    riasec_scores: dict,
    academic_scores: dict
) -> list[dict]:
    """Predict top 5 program studi recommendations.

    Args:
        riasec_scores: {'r': float, 'i': float, 'a': float, 's': float, 'e': float, 'c': float}
        academic_scores: {'bahasa_indonesia': float, ..., 'gpa': float}

    Returns:
        List of 5 dicts, each containing:
        {
            'program_id': int,
            'program_name': str,
            'confidence': float,      # probability 0.0-1.0
            'top_features': list[str]  # 3 influential features explanation
        }
    """
    model = _load_model()
    scaler = _load_scaler()
    prodi_info = _load_prodi_info()

    # Build feature vector
    X = _build_feature_vector(riasec_scores, academic_scores)

    # Scale features
    X_scaled = scaler.transform(X)

    # Get predictions and probabilities
    probs = model.predict_proba(X_scaled)[0]
    classes = model.classes_

    # Get top 5 indices (highest probability)
    top5_indices = probs.argsort()[-5:][::-1]

    # Get feature importances for explanation
    feature_importances = pd.Series(
        model.feature_importances_,
        index=FEATURE_COLUMNS
    )

    results = []
    for idx in top5_indices:
        program_id = int(classes[idx])
        confidence = float(probs[idx])

        # Get program name from prodi_info
        program_row = prodi_info[prodi_info['program_id'] == program_id]
        if len(program_row) > 0:
            program_name = program_row['program_name'].values[0]
        else:
            program_name = f"Program {program_id}"

        # Get top features explanation
        top_features = _get_top_features(feature_importances, X, top_n=3)

        results.append({
            'program_id': program_id,
            'program_name': program_name,
            'confidence': confidence,
            'top_features': top_features
        })

    return results


def get_program_details(program_id: int) -> dict:
    """Get full details for a program studi.

    Args:
        program_id: Program ID (1-68)

    Returns:
        Dict with program details or empty dict if not found
    """
    prodi_info = _load_prodi_info()
    program_row = prodi_info[prodi_info['program_id'] == program_id]

    if len(program_row) == 0:
        return {}

    row = program_row.iloc[0]
    return {
        'program_id': int(row['program_id']),
        'program_name': row['program_name'],
        'deskripsi': row.get('deskripsi', ''),
        'prospek_kerja': row.get('prospek_kerja', ''),
        'mata_kuliah_unggulan': row.get('mata_kuliah_unggulan', ''),
        'durasi_studi': row.get('durasi_studi', ''),
        'jenjang': row.get('jenjang', ''),
        'kelompok_prodi': row.get('kelompok_prodi', ''),
        'akreditasi_umum': row.get('akreditasi_umum', ''),
        'top_kampus_prodi': row.get('top_kampus_prodi', ''),
        'est_biaya': row.get('est_biaya', ''),
        'list_kampus_prodi': row.get('list_kampus_prodi', '')
    }