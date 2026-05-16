"""
pages/5_profile.py — User Profile Page
======================================
Halaman profil pengguna dengan info akun dan histori tes.
"""

import streamlit as st
from datetime import datetime

from utils.supabase_client import (
    get_test_results,
    update_profile,
    get_profile
)

# === Page Configuration ===
st.set_page_config(
    page_title="Profil Saya",
    page_icon="👤",
    layout="wide"
)


# === Helper Functions ===
def render_riasec_summary(scores: dict) -> str:
    """Generate text summary of dominant RIASEC dimensions."""
    if not scores:
        return "Data tidak tersedia"

    # Sort by score
    sorted_dims = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_dims = sorted_dims[:3]  # Top 3

    dim_labels = {
        'r': 'Realistic', 'i': 'Investigative', 'a': 'Artistic',
        's': 'Social', 'e': 'Enterprising', 'c': 'Conventional'
    }

    return ', '.join([f"{dim_labels[d[0]].upper()} ({d[1]:.0f})" for d in top_dims])


def render_test_history_item(result: dict, index: int):
    """Render a single test history item."""
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])

        # Date
        created_at = result.get('created_at', '')
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                date_str = dt.strftime("%d %B %Y, %H:%M")
            except:
                date_str = created_at
        else:
            date_str = '-'

        with col1:
            st.markdown(f"**📅 {date_str}**")

        # Top recommendation
        top5 = result.get('top5_rekomendasi', [])
        if top5:
            top = top5[0]
            confidence = top.get('confidence', 0) * 100
            with col2:
                st.markdown(f"**🎓 {top.get('program_name', '-')}**")
                st.caption(f"Tingkat kecocokan: {confidence:.1f}%")
        else:
            with col2:
                st.markdown("Data tidak tersedia")

        # Action
        with col3:
            st.markdown("**Detail:**")
            riasec = {
                'r': result.get('riasec_r', 0),
                'i': result.get('riasec_i', 0),
                'a': result.get('riasec_a', 0),
                's': result.get('riasec_s', 0),
                'e': result.get('riasec_e', 0),
                'c': result.get('riasec_c', 0)
            }

            with st.expander("Lihat Detail"):
                st.markdown("**Profil RIASEC:**")
                st.write(render_riasec_summary(riasec))

                st.markdown("**Top 5 Rekomendasi:**")
                for i, rec in enumerate(top5, 1):
                    st.write(f"{i}. {rec.get('program_name', '-')} ({rec.get('confidence', 0)*100:.1f}%)")

                if result.get('nilai_akademik'):
                    st.markdown("**Nilai Akademik:**")
                    nilai = result['nilai_akademik']
                    st.write(f"GPA: {nilai.get('gpa', '-'):.1f}" if isinstance(nilai.get('gpa'), (int, float)) else "GPA: -")

        st.markdown("---")


# === Main Page ===
# === Access Control ===
if 'user' not in st.session_state or not st.session_state.user:
    st.error("Silakan login terlebih dahulu")
    st.stop()

# === Header ===
st.title("👤 Profil Saya")
st.markdown("---")

user = st.session_state.user
role = user.get('role', 'siswa')
role_display = "👨‍🎓 Siswa" if role == 'siswa' else "👨‍🏫 Guru BK"

st.markdown(f"""
<div style="background: linear-gradient(135deg, #1a5276, #2980b9); padding: 25px; border-radius: 15px; color: white; margin-bottom: 20px;">
    <h2 style="margin: 0; color: white;">{user.get('full_name', 'User')}</h2>
    <p style="margin: 5px 0 0 0; opacity: 0.9;">{role_display}</p>
</div>
""", unsafe_allow_html=True)

# === Profile Info Section ===
st.markdown("### 📝 Informasi Akun")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Nama Lengkap:**")
    st.write(user.get('full_name', '-'))

    st.markdown("**Email:**")
    st.write(user.get('email', '-'))

with col2:
    st.markdown("**Role:**")
    st.write(role_display)

    st.markdown("**Sekolah:**")
    st.write(user.get('school', '-') or 'Belum diisi')

# Edit profile button
with st.expander("✏️ Edit Profil"):
    with st.form("edit_profile_form"):
        st.markdown("**Update Informasi:**")

        new_full_name = st.text_input(
            "Nama Lengkap",
            value=user.get('full_name', '')
        )

        new_school = st.text_input(
            "Sekolah",
            value=user.get('school', '')
        )

        submitted = st.form_submit_button("💾 Simpan Perubahan")
        if submitted:
            try:
                updates = {
                    'full_name': new_full_name,
                    'school': new_school
                }
                update_profile(user['id'], updates)

                # Update session state
                st.session_state.user['full_name'] = new_full_name
                st.session_state.user['school'] = new_school

                st.success("✅ Profil berhasil diperbarui!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Gagal memperbarui: {str(e)}")

st.markdown("---")

# === Test History Section ===
st.markdown("### 📋 Histori Tes")

# Check if user has test results
with st.spinner("Memuat histori tes..."):
    try:
        test_results = get_test_results(user['id'])
    except Exception as e:
        st.error(f"Error memuat data: {str(e)}")
        test_results = []

if not test_results:
    st.info("📭 Kamu belum melakukan tes sama sekali.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Mulai Tes Sekarang")
        st.markdown("""
        Ikuti langkah-langkah berikut untuk mendapatkan rekomendasi program studi:

        1. **Isi Kuesioner RIASEC** — Jawab 24 pertanyaan tentang kepribadianmu
        2. **Masukkan Nilai Akademik** — Input nilai rapor kamu
        3. **Lihat Hasil** — Dapatkan 5 program studi yang cocok
        """)

    with col2:
        if st.button("🎯 Mulai Tes Sekarang", type="primary", use_container_width=True):
            if role == 'siswa':
                st.switch_page("pages/1_questionnaire.py")
            else:
                st.info("Halaman tes hanya untuk siswa")

    st.stop()

# Show test count
st.success(f"📊 Kamu sudah melakukan {len(test_results)} kali tes")

# Statistics
col1, col2, col3 = st.columns(3)

with col1:
    latest = test_results[0] if test_results else None
    if latest:
        top5 = latest.get('top5_rekomendasi', [])
        if top5:
            st.metric("Tes Terakhir", f"Top: {top5[0].get('program_name', '-')[:20]}...")

with col2:
    # Average confidence
    confidences = []
    for r in test_results:
        top5 = r.get('top5_rekomendasi', [])
        if top5:
            confidences.append(top5[0].get('confidence', 0) * 100)
    if confidences:
        avg_conf = sum(confidences) / len(confidences)
        st.metric("Rata-rata Confidence", f"{avg_conf:.1f}%")

with col3:
    # First test date
    if test_results:
        last_result = test_results[-1]
        created_at = last_result.get('created_at', '')
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                first_date = dt.strftime("%d %b %Y")
            except:
                first_date = '-'
        else:
            first_date = '-'
        st.metric("Tes Pertama", first_date)

st.markdown("---")

# === Test History List ===
st.markdown("### 📜 Detail Histori Tes")

# Sort by date (newest first)
test_results_sorted = sorted(
    test_results,
    key=lambda x: x.get('created_at', ''),
    reverse=True
)

for i, result in enumerate(test_results_sorted, 1):
    st.markdown(f"#### Tes #{len(test_results_sorted) - i + 1}")
    render_test_history_item(result, i)

# === Actions ===
st.markdown("---")
st.markdown("### 🔄 Aksi")

col1, col2 = st.columns(2)

with col1:
    if role == 'siswa':
        if st.button("🔄 Tes Ulang", type="primary", use_container_width=True):
            # Clear relevant session state
            for key in ['riasec_scores', 'academic_scores', 'recommendations',
                       'program_details', 'answers', 'show_results', 'current_step']:
                if key in st.session_state:
                    del st.session_state[key]
            st.switch_page("pages/1_questionnaire.py")
    else:
        st.button("🔄 Tes Ulang", disabled=True, use_container_width=True)
        st.caption("Fitur tes hanya untuk siswa")

with col2:
    if st.button("📊 Kembali ke Dashboard", use_container_width=True):
        st.switch_page("app.py")

# === Footer ===
st.markdown("---")
st.caption(f"Profil terakhir diperbarui: {datetime.now().strftime('%d/%m/%Y %H:%M')}")