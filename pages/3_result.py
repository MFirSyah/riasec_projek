"""
pages/3_result.py — Results & Recommendations Page
===================================================
Halaman hasil rekomendasi program studi berdasarkan RIASEC dan nilai akademik.
"""

import streamlit as st
import plotly.graph_objects as go

from utils.predict import predict_top5, get_program_details
from utils.pdf_export import generate_pdf, save_pdf_to_file
from utils.supabase_client import save_test_result

# === Page Configuration ===
st.set_page_config(
    page_title="Hasil Rekomendasi",
    page_icon="🎯",
    layout="wide"
)


# === Helper Functions ===
def create_confidence_bar(confidence: float) -> go.Figure:
    """Create a horizontal confidence bar chart."""
    fig = go.Figure(go.Indicator(
        domain={'x': [0, 1], 'y': [0, 1]},
        value=confidence * 100,
        mode="gauge+number",
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#1a5276"},
            'steps': [
                {'range': [0, 40], 'color': '#e74c3c'},
                {'range': [40, 70], 'color': '#f1c40f'},
                {'range': [70, 100], 'color': '#27ae60'},
            ],
        },
        number={'suffix': '%'}
    ))
    fig.update_layout(
        height=100,
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor='transparent'
    )
    return fig


def create_riasec_radar(scores: dict) -> go.Figure:
    """Create RIASEC radar chart."""
    dimensions = ['R', 'I', 'A', 'S', 'E', 'C']
    values = [
        scores.get('r', 0), scores.get('i', 0), scores.get('a', 0),
        scores.get('s', 0), scores.get('e', 0), scores.get('c', 0)
    ]
    values.append(values[0])  # Close the polygon
    theta = dimensions + ['R']

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=theta,
        fill='toself',
        fillcolor='rgba(26, 82, 118, 0.3)',
        line=dict(color='#1a5276', width=2),
        name='Profil RIASEC'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        height=200,
        margin=dict(t=20, b=20, l=20, r=20)
    )
    return fig


def render_recommendation_card(rec: dict, rank: int, details: dict):
    """Render a single recommendation card."""
    confidence = rec['confidence']
    confidence_pct = confidence * 100

    # Color based on confidence
    if confidence_pct >= 70:
        conf_color = "#27ae60"
        conf_label = "Sangat Cocok"
    elif confidence_pct >= 50:
        conf_color = "#3498db"
        conf_label = "Cukup Cocok"
    elif confidence_pct >= 30:
        conf_color = "#f39c12"
        conf_label = "Kurang Cocok"
    else:
        conf_color = "#e74c3c"
        conf_label = "Cocok Sebagian"

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #f8f9fa, #e9ecef); padding: 20px; border-radius: 15px; margin-bottom: 20px; border-left: 5px solid {conf_color};">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="background-color: {conf_color}; color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 18px; margin-right: 15px;">
                    #{rank}
                </span>
                <span style="font-size: 20px; font-weight: bold; color: #1a5276;">{rec['program_name']}</span>
            </div>
            <div style="text-align: right;">
                <span style="font-size: 24px; font-weight: bold; color: {conf_color};">{confidence_pct:.1f}%</span>
                <br>
                <span style="font-size: 12px; color: #666;">{conf_label}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Top features explanation
    if rec.get('top_features'):
        st.markdown("**🔍 Mengapa cocok untuk kamu:**")
        for feature in rec['top_features']:
            st.markdown(f"• {feature}")
        st.markdown("")

    # Details expander
    with st.expander("📋 Lihat Detail Program Studi"):
        if details:
            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown(f"**📚 Jenjang:** {details.get('jenjang', '-')}")
                st.markdown(f"**⏱️ Durasi:** {details.get('durasi_studi', '-')}")
                st.markdown(f"**🏆 Akreditasi:** {details.get('akreditasi_umum', '-')}")

            with col2:
                st.markdown(f"**💰 Estimasi Biaya:**")
                st.markdown(f"_{details.get('est_biaya', '-')}_")

            st.markdown("---")
            st.markdown(f"**📖 Deskripsi:**")
            st.write(details.get('deskripsi', '-'))

            st.markdown(f"**💼 Prospek Kerja:**")
            st.write(details.get('prospek_kerja', '-'))

            if details.get('mata_kuliah_unggulan'):
                st.markdown(f"**📗 Mata Kuliah Unggulan:**")
                st.write(details.get('mata_kuliah_unggulan', '-'))

            if details.get('top_kampus_prodi'):
                st.markdown("---")
                st.markdown("**🏛️ Top Kampus untuk Prodi Ini:**")
                st.write(details.get('top_kampus_prodi', '-'))

            if details.get('list_kampus_prodi'):
                st.markdown("**📍 Daftar Kampus:**")
                st.write(details.get('list_kampus_prodi', '-'))

        else:
            st.warning("Detail program tidak ditemukan")


# === Main Page ===
# === Access Control ===
if 'user' not in st.session_state or not st.session_state.user:
    st.error("Silakan login terlebih dahulu")
    st.stop()

if st.session_state.user.get('role') != 'siswa':
    st.warning("Halaman ini hanya untuk siswa")
    st.stop()

# Check required data
if not st.session_state.get('riasec_scores'):
    st.warning("⚠️ Harap isi Kuesioner RIASEC terlebih dahulu")
    if st.button("➡️ Ke Kuesioner RIASEC"):
        st.switch_page("pages/1_questionnaire.py")
    st.stop()

if not st.session_state.get('academic_scores'):
    st.warning("⚠️ Harap isi Input Nilai Akademik terlebih dahulu")
    if st.button("➡️ Ke Input Nilai"):
        st.switch_page("pages/2_academic_input.py")
    st.stop()

# === Header ===
st.title("🎯 Hasil Rekomendasi Program Studi")
st.markdown("---")

# User info
user = st.session_state.user
st.markdown(f"**Siswa:** {user.get('full_name', 'User')} | **Role:** {user.get('role', 'siswa').title()}")

# === Get Predictions ===
if 'recommendations' not in st.session_state or not st.session_state.recommendations:
    with st.spinner("🧠 Menganalisis profil kamu..."):
        riasec_scores = st.session_state.riasec_scores
        academic_scores = st.session_state.academic_scores

        # Get predictions
        recommendations = predict_top5(riasec_scores, academic_scores)
        st.session_state.recommendations = recommendations

        # Get program details
        program_details = []
        for rec in recommendations:
            details = get_program_details(rec['program_id'])
            program_details.append(details)
        st.session_state.program_details = program_details
else:
    recommendations = st.session_state.recommendations
    program_details = st.session_state.get('program_details', [])

# === Summary Section ===
st.markdown("### 📊 Ringkasan Profil Kamu")

col1, col2 = st.columns([1, 2])

with col1:
    # RIASEC Radar
    st.markdown("**Profil RIASEC:**")
    fig = create_riasec_radar(st.session_state.riasec_scores)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Academic scores summary
    st.markdown("**Nilai Akademik:**")
    academic_scores = st.session_state.academic_scores

    cols = st.columns(5)
    subjects = ['bahasa_indonesia', 'bahasa_inggris', 'matematika', 'informatika', 'ipa',
                 'ips', 'ppkn', 'penjas', 'seni', 'gpa']
    subject_labels = ['B. Indo', 'B. Inggris', 'MTK', 'INF', 'IPA', 'IPS', 'PPKn', 'Penjas', 'Seni', 'GPA']

    for i, (subj, label) in enumerate(zip(subjects, subject_labels)):
        with cols[i % 5]:
            score = academic_scores.get(subj, 0)
            st.metric(label, f"{score:.1f}")

st.markdown("---")

# === Recommendations ===
st.markdown("### 🎓 5 Program Studi yang Direkomendasikan")

# Render recommendation cards
for i, (rec, details) in enumerate(zip(recommendations, program_details), 1):
    render_recommendation_card(rec, i, details)

# === Actions ===
st.markdown("---")
st.markdown("### 💾 Aksi")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💾 Simpan Hasil ke Database", use_container_width=True):
        try:
            # Get school from user profile
            school = user.get('school', '')

            # Save to Supabase
            hasil = save_test_result(
                user_id=user['id'],
                riasec_scores=st.session_state.riasec_scores,
                nilai_akademik=st.session_state.academic_scores,
                top5_rekomendasi=recommendations,
                school=school
            )
            st.success(f"✅ Hasil berhasil disimpan! ID: {hasil.get('id', 'N/A')}")
        except Exception as e:
            st.error(f"❌ Gagal menyimpan: {str(e)}")

with col2:
    if st.button("📄 Export ke PDF", use_container_width=True):
        with st.spinner("📄 Membuat PDF..."):
            try:
                # Generate PDF
                user_name = user.get('full_name', 'User')
                riasec_scores = st.session_state.riasec_scores
                academic_scores = st.session_state.academic_scores

                pdf_bytes = generate_pdf(
                    user_name=user_name,
                    riasec_scores=riasec_scores,
                    academic_scores=academic_scores,
                    recommendations=recommendations,
                    program_details=program_details
                )

                # Save to file
                filename = f"RIASEC_Rekomendasi_{user_name.replace(' ', '_')}.pdf"
                filepath = save_pdf_to_file(pdf_bytes, filename)

                st.success(f"✅ PDF berhasil di-export!")
                st.info(f"📁 Disimpan ke: {filepath}")

                # Provide download button
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ Gagal export PDF: {str(e)}")

with col3:
    if st.button("🔄 Tes Ulang", use_container_width=True):
        # Clear session state
        for key in ['riasec_scores', 'academic_scores', 'recommendations', 'program_details', 'answers', 'show_results', 'current_step']:
            if key in st.session_state:
                del st.session_state[key]
        st.switch_page("pages/1_questionnaire.py")

st.markdown("---")

# === Feedback Section ===
st.markdown("### 📝 Feedback")
st.markdown("Bantu kami meningkatkan aplikasi ini dengan memberikan feedback!")

with st.form("feedback_form"):
    rating = st.slider("Bagaimana pengalamanmu dengan aplikasi ini?", 1, 5, 3)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if rating == 1:
            st.write("😞 Sangat Tidak Puas")
        elif rating == 2:
            st.write("😕 Tidak Puas")
        elif rating == 3:
            st.write("😐 Netral")
        elif rating == 4:
            st.write("😊 Puas")
        else:
            st.write("😄 Sangat Puas")

    komentar = st.text_area("Komentar (opsional)", placeholder="Ceritakan pengalamanmu...")

    submitted = st.form_submit_button("Kirim Feedback")
    if submitted:
        st.success("✅ Terima kasih atas feedback kamu!")
        st.info("Feedback kamu sangat membantu kami untuk meningkatkan aplikasi ini.")

# === Footer ===
st.markdown("---")
st.caption("""
💡 **Catatan:** Rekomendasi ini berdasarkan analisis machine learning dan hanya sebagai panduan.
Keputusan akhir tetap ada di tangan kamu dan orang tua/wali.
""")