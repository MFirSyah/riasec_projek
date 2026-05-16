"""
supabase_client.py — Supabase client and database helper functions
================================================================
Koneksi ke Supabase dan helper untuk tabel profiles, hasil_tes, dan feedback.
Mendukung local development (.env) dan Streamlit Cloud (secrets.toml)
"""

import os
from typing import Optional

# Check if we're in Streamlit Cloud environment
def _get_secrets():
    """Load secrets from Streamlit Cloud or .env file."""
    try:
        import streamlit as st
        # We're in Streamlit - try to use secrets
        return st.secrets.get("SUPABASE_URL", ""), st.secrets.get("SUPABASE_ANON_KEY", "")
    except:
        # We're in local environment - use .env
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv('SUPABASE_URL', ''), os.getenv('SUPABASE_ANON_KEY', '')

# Get credentials
SUPABASE_URL: str
SUPABASE_ANON_KEY: str
SUPABASE_URL, SUPABASE_ANON_KEY = _get_secrets()

from supabase import create_client, Client

# Initialize client
_client: Optional[Client] = None


def get_client() -> Client:
    """Get or create Supabase client singleton."""
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_ANON_KEY:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_ANON_KEY must be set. "
                "For local: set in .env file. For Streamlit Cloud: set in Secrets."
            )
        _client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    return _client


def get_user():
    """Get authenticated user from current session."""
    client = get_client()
    return client.auth.get_user()


# =============================================================================
# PROFILES TABLE
# =============================================================================

def get_profile(user_id: str) -> Optional[dict]:
    """Get user profile by user_id."""
    client = get_client()
    response = client.table('profiles').select('*').eq('id', user_id).execute()
    if response.data:
        return response.data[0]
    return None


def create_profile(user_id: str, full_name: str, role: str, school: str = '') -> dict:
    """Create a new profile for a user."""
    client = get_client()
    data = {
        'id': user_id,
        'full_name': full_name,
        'role': role,
        'school': school
    }
    response = client.table('profiles').insert(data).execute()
    return response.data[0]


def update_profile(user_id: str, updates: dict) -> dict:
    """Update user profile fields."""
    client = get_client()
    response = client.table('profiles').update(updates).eq('id', user_id).execute()
    return response.data[0]


# =============================================================================
# HASIL_TES TABLE
# =============================================================================

def save_test_result(
    user_id: str,
    riasec_scores: dict,
    nilai_akademik: dict,
    top5_rekomendasi: list[dict],
    school: str = ''
) -> dict:
    """Save test result to hasil_tes table.

    Args:
        user_id: UUID of the authenticated user
        riasec_scores: {'r': float, 'i': float, 'a': float, 's': float, 'e': float, 'c': float}
        nilai_akademik: dict with academic scores
        top5_rekomendasi: list of 5 recommendation dicts
        school: school name for multi-school filtering

    Returns:
        Created row data
    """
    client = get_client()
    data = {
        'user_id': user_id,
        'school': school,
        'riasec_r': riasec_scores.get('r', 0),
        'riasec_i': riasec_scores.get('i', 0),
        'riasec_a': riasec_scores.get('a', 0),
        'riasec_s': riasec_scores.get('s', 0),
        'riasec_e': riasec_scores.get('e', 0),
        'riasec_c': riasec_scores.get('c', 0),
        'nilai_akademik': nilai_akademik,
        'top5_rekomendasi': top5_rekomendasi
    }
    response = client.table('hasil_tes').insert(data).execute()
    return response.data[0]


def get_test_results(user_id: str) -> list[dict]:
    """Get all test results for a user."""
    client = get_client()
    response = (
        client.table('hasil_tes')
        .select('*')
        .eq('user_id', user_id)
        .order('created_at', desc=True)
        .execute()
    )
    return response.data


def get_all_test_results() -> list[dict]:
    """Get all test results (for guru_bk dashboard)."""
    client = get_client()
    response = (
        client.table('hasil_tes')
        .select('*')
        .order('created_at', desc=True)
        .execute()
    )
    return response.data


def get_test_count() -> int:
    """Get total number of tests conducted."""
    client = get_client()
    response = client.table('hasil_tes').select('id', count='exact').execute()
    return response.count if hasattr(response, 'count') else len(response.data)


def get_all_profiles() -> dict:
    """Get all profiles as a dict mapping user_id to profile data.

    Returns:
        Dict: {user_id: {full_name, school, role}}
    """
    client = get_client()
    response = client.table('profiles').select('id, full_name, school, role').execute()
    return {r['id']: r for r in response.data}


# =============================================================================
# FEEDBACK TABLE
# =============================================================================

def save_feedback(
    user_id: str,
    hasil_id: str,
    rating: int,
    komentar: str = ''
) -> dict:
    """Save user feedback for a test result.

    Args:
        user_id: UUID of the authenticated user
        hasil_id: UUID of the hasil_tes record
        rating: 1-5 rating
        komentar: Optional comment

    Returns:
        Created row data
    """
    client = get_client()
    data = {
        'user_id': user_id,
        'hasil_id': hasil_id,
        'rating': rating,
        'komentar': komentar
    }
    response = client.table('feedback').insert(data).execute()
    return response.data[0]


def get_feedback_stats() -> dict:
    """Get feedback statistics (avg rating, count)."""
    client = get_client()
    response = (
        client.table('feedback')
        .select('rating')
        .execute()
    )
    if not response.data:
        return {'avg_rating': 0, 'count': 0}

    ratings = [r['rating'] for r in response.data]
    return {
        'avg_rating': sum(ratings) / len(ratings),
        'count': len(ratings)
    }
