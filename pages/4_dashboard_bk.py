"""
pages/4_dashboard_bk.py — BK Teacher Dashboard
===============================================
Dashboard untuk guru BK melihat statistik dan histori tes siswa.
Hanya bisa diakses oleh role guru_bk.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

from utils.supabase_client import (
    get_all_test_results,
    get_test_count,
    get_feedback_stats,
    get_all_profiles
)

# === Page Configuration ===
st.set_page_config(
    page_title="Dashboard BK",
    page_icon="📊",
    layout="wide"
)


# === Helper Functions ===
def create_riasec_distribution(results: list) -> go.Figure:
    """Create bar chart for RIASEC score distribution."""
    if not results:
        return go.Figure()

    # Calculate average RIASEC scores
    riasec_keys = ['riasec_r', 'riasec_i', 'riasec_a', 'riasec_s', 'riasec_e', 'riasec_c']
    labels = ['R', 'I', 'A', 'S', 'E', 'C']

    totals = {key: 0 for key in riasec_keys}
    for result in results:
        for key in riasec_keys:
            totals[key] += result.get(key, 0)

    avg_scores = [totals[key] / len(results) if results else 0 for key in riasec_keys]

    fig = go.Figure(data=[
        go.Bar(
            x=labels,
            y=avg_scores,
            marker_color=['#e74c3c', '#3498db', '#9b59b6', '#2ecc71', '#f1c40f', '#34495e'],
            text=[f"{s:.1f}" for s in avg_scores],
            textposition='outside'
        )
    ])

    fig.update_layout(
        title="Rata-rata Skor RIASEC Siswa",
        yaxis_title="Skor Rata-rata",
        xaxis_title="Dimensi RIASEC",
        height=300,
        margin=dict(t=50, b=30, l=30, r=30)
    )

    return fig


def create_recommendation_chart(results: list) -> go.Figure:
    """Create pie chart for top recommendations distribution."""
    if not results:
        return go.Figure()

    # Count top recommendations
    top_programs = {}
    for result in results:
        top5 = result.get('top5_rekomendasi', [])
        if top5:
            top1 = top5[0]
            prog_name = top1.get('program_name', 'Unknown')
            top_programs[prog_name] = top_programs.get(prog_name, 0) + 1

    # Sort by count and take top 10
    sorted_programs = sorted(top_programs.items(), key=lambda x: x[1], reverse=True)[:10]
    names = [p[0] for p in sorted_programs]
    counts = [p[1] for p in sorted_programs]

    fig = go.Figure(data=[
        go.Bar(
            x=counts,
            y=names,
            orientation='h',
            marker_color='#1a5276',
            text=counts,
            textposition='outside'
        )
    ])

    fig.update_layout(
        title="Top 10 Program Studi yang Direkomendasikan",
        xaxis_title="Jumlah Siswa",
        yaxis_title="Program Studi",
        height=400,
        margin=dict(t=50, b=30, l=200, r=30),
        yaxis={'categoryorder': 'total ascending'}
    )

    return fig


def create_confidence_chart(results: list) -> go.Figure:
    """Create histogram of confidence scores."""
    if not results:
        return go.Figure()

    confidences = []
    for result in results:
        top5 = result.get('top5_rekomendasi', [])
        if top5:
            confidences.append(top5[0].get('confidence', 0) * 100)

    if not confidences:
        return go.Figure()

    fig = px.histogram(
        x=confidences,
        nbins=10,
        labels={'x': 'Confidence Score (%)', 'y': 'Jumlah Siswa'},
        title="Distribusi Confidence Score"
    )

    fig.update_layout(height=250, margin=dict(t=50, b=30, l=30, r=30))
    fig.update_traces(marker_color='#1a5276')

    return fig


def render_test_history_table(results: list, profiles: dict, date_filter: str = None):
    """Render test history table with filtering.

    Args:
        results: List of test results
        profiles: Dict mapping user_id to profile data {user_id: {full_name, school}}
        date_filter: Optional date string to filter by
    """
    if not results:
        st.info("Belum ada data tes siswa.")
        return

    # Filter by date if specified
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
            filtered_results = []
            for r in results:
                created_at = r.get('created_at', '')
                if created_at:
                    try:
                        r_date = datetime.fromisoformat(created_at.replace('Z', '+00:00')).date()
                        if r_date == filter_date:
                            filtered_results.append(r)
                    except:
                        filtered_results.append(r)
            results = filtered_results
        except:
            pass

    # Build table data
    table_data = []
    for r in results:
        top5 = r.get('top5_rekomendasi', [])
        top_program = top5[0].get('program_name', '-') if top5 else '-'
        confidence = top5[0].get('confidence', 0) if top5 else 0

        created_at = r.get('created_at', '')
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                formatted_date = dt.strftime("%d/%m/%Y %H:%M")
            except:
                formatted_date = created_at
        else:
            formatted_date = '-'

        # Get student name from profiles dict
        user_id = r.get('user_id', '')
        profile = profiles.get(user_id, {})
        full_name = profile.get('full_name', 'Siswa') if profile else 'Siswa'
        school = profile.get('school', '-') if profile else '-'

        table_data.append({
            'Tanggal': formatted_date,
            'Nama': full_name,
            'Sekolah': school[:20] + '...' if len(school) > 20 else school,
            'RIASEC Dominan': f"R:{r.get('riasec_r', 0):.0f} I:{r.get('riasec_i', 0):.0f} A:{r.get('riasec_a', 0):.0f}",
            'Rekomendasi Teratas': top_program[:30] + '...' if len(top_program) > 30 else top_program,
            'Confidence': f"{confidence * 100:.1f}%"
        })

    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True
    )


# === Main Page ===
# === Access Control - GURU BK ONLY ===
if 'user' not in st.session_state or not st.session_state.user:
    st.error("Silakan login terlebih dahulu")
    st.stop()

if st.session_state.user.get('role') != 'guru_bk':
    st.error("🚫 Akses Ditolak")
    st.warning("Halaman ini hanya dapat diakses oleh Guru BK.")
    st.info("Jika kamu adalah siswa, silakan gunakan menu sidebar untuk mengakses fitur siswa.")
    st.stop()

# === Header ===
st.title("📊 Dashboard Bimbingan dan Konseling")
st.markdown("---")

user = st.session_state.user
st.markdown(f"**Guru BK:** {user.get('full_name', 'User')} | **Sekolah:** {user.get('school', '-')}")

# === Load Data ===
with st.spinner("Memuat data..."):
    try:
        all_results = get_all_test_results()
        all_profiles = get_all_profiles()
        total_tests = len(all_results)
        feedback_stats = get_feedback_stats()
    except Exception as e:
        st.error(f"Error memuat data: {str(e)}")
        all_results = []
        all_profiles = {}
        total_tests = 0
        feedback_stats = {'avg_rating': 0, 'count': 0}

# === Statistics Cards ===
st.markdown("### 📈 Statistik Keseluruhan")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Siswa Tes", total_tests)

with col2:
    unique_students = len(set(r.get('user_id') for r in all_results))
    st.metric("Siswa Unik", unique_students)

with col3:
    if feedback_stats['count'] > 0:
        st.metric("Rating Rata-rata", f"{feedback_stats['avg_rating']:.1f}/5")
    else:
        st.metric("Rating Rata-rata", "N/A")

with col4:
    # Calculate average confidence
    if all_results:
        avg_conf = []
        for r in all_results:
            top5 = r.get('top5_rekomendasi', [])
            if top5:
                avg_conf.append(top5[0].get('confidence', 0) * 100)
        avg_confidence = sum(avg_conf) / len(avg_conf) if avg_conf else 0
        st.metric("Avg Confidence", f"{avg_confidence:.1f}%")
    else:
        st.metric("Avg Confidence", "N/A")

st.markdown("---")

# === Charts ===
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(create_riasec_distribution(all_results), use_container_width=True, key="riasec_chart")

with col2:
    st.plotly_chart(create_confidence_chart(all_results), use_container_width=True, key="confidence_chart")

st.markdown("---")

# === Recommendation Distribution ===
st.markdown("### 🎓 Distribusi Rekomendasi Program Studi")
st.plotly_chart(create_recommendation_chart(all_results), use_container_width=True, key="recommendation_chart")

st.markdown("---")

# === Test History ===
st.markdown("### 📋 Histori Tes Siswa")

# Date filter
col1, col2 = st.columns([1, 3])
with col1:
    date_filter = st.date_input(
        "Filter Tanggal",
        value=None,
        help="Pilih tanggal untuk melihat tes pada tanggal tersebut"
    )

if date_filter:
    date_str = date_filter.strftime("%Y-%m-%d")
else:
    date_str = None

with col2:
    st.write(f"Menampilkan {len(all_results)} hasil tes")

render_test_history_table(all_results, all_profiles, date_str if date_str else None)

# === Export Data ===
st.markdown("---")
st.markdown("### 📤 Export Data")

col1, col2, col3 = st.columns(3)

with col1:
    st.download_button(
        label="📥 Download CSV",
        data="dummy",  # TODO: Generate actual CSV
        file_name="dashboard_bk_export.csv",
        mime="text/csv",
        use_container_width=True,
        disabled=True
    )
    st.caption("Fitur coming soon")

with col2:
    st.download_button(
        label="📊 Download Laporan PDF",
        data="dummy",  # TODO: Generate actual PDF report
        file_name="laporan_bk.pdf",
        mime="application/pdf",
        use_container_width=True,
        disabled=True
    )
    st.caption("Fitur coming soon")

with col3:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

# === Footer ===
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%d/%m/%Y %H:%M')}")