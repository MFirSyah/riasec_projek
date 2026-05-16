"""
pages/2_academic_input.py — Academic Scores Input Page
======================================================
Halaman input 10 nilai mata pelajaran dan GPA.
"""

import streamlit as st

# === Page Configuration ===
st.set_page_config(
    page_title="Input Nilai Rapor",
    page_icon="📊",
    layout="wide"
)

# === Subject Definitions ===
SUBJECTS = [
    {'key': 'bahasa_indonesia', 'label': 'Bahasa Indonesia', 'icon': '📖'},
    {'key': 'bahasa_inggris', 'label': 'Bahasa Inggris', 'icon': '🌍'},
    {'key': 'matematika', 'label': 'Matematika', 'icon': '📐'},
    {'key': 'informatika', 'label': 'Informatika / TIK', 'icon': '💻'},
    {'key': 'ipa', 'label': 'IPA (Ilmu Pengetahuan Alam)', 'icon': '🔬'},
    {'key': 'ips', 'label': 'IPS (Ilmu Pengetahuan Sosial)', 'icon': '🌐'},
    {'key': 'ppkn', 'label': 'PPKn / PKn', 'icon': '🏛️'},
    {'key': 'penjas', 'label': 'Penjasorkes / PJOK', 'icon': '⚽'},
    {'key': 'seni', 'label': 'Seni Budaya', 'icon': '🎨'},
    {'key': 'gpa', 'label': 'GPA (Nilai Rata-rata)', 'icon': '📈'},
]

# Subject groups for visual organization
SUBJECT_GROUPS = [
    {
        'title': '📚 Mata Pelajaran Inti',
        'subjects': SUBJECTS[:4]
    },
    {
        'title': '🔬 IPA & IPS',
        'subjects': SUBJECTS[4:6]
    },
    {
        'title': '🎯 Mata Pelajaran Umum',
        'subjects': SUBJECTS[6:9]
    },
    {
        'title': '📊 Nilai Akademik',
        'subjects': SUBJECTS[9:]
    },
]

# === Validation Functions ===
def validate_score(value, field_name):
    """Validate a single score."""
    if value is None or value == '':
        return False, f"{field_name} tidak boleh kosong", None

    try:
        num_value = float(value)
    except (ValueError, TypeError):
        return False, f"{field_name} harus berupa angka", None

    if num_value < 0 or num_value > 100:
        return False, f"{field_name} harus antara 0-100", None

    return True, None, num_value


def validate_all_scores(scores: dict) -> tuple[bool, list[str]]:
    """Validate all scores."""
    errors = []

    for subject in SUBJECTS:
        key = subject['key']
        label = subject['label']

        if key not in scores or scores[key] is None:
            errors.append(f"{label} belum diisi")
            continue

        is_valid, error_msg, _ = validate_score(scores[key], label)
        if not is_valid:
            errors.append(error_msg)

    return len(errors) == 0, errors


# === UI Components ===
def render_score_input(subject: dict, col):
    """Render score input for a single subject."""
    with col:
        st.markdown(f"### {subject['icon']} {subject['label']}")

        value = st.number_input(
            label=f"Nilai {subject['label']}",
            min_value=0.0,
            max_value=100.0,
            value=70.0,
            step=0.1,
            key=f"input_{subject['key']}",
            help=f"Masukkan nilai {subject['label']} (0-100)"
        )

        # Visual indicator
        if value >= 80:
            st.markdown("🟢 <span style='color: green; font-size: 12px;'>Sangat Baik</span>", unsafe_allow_html=True)
        elif value >= 70:
            st.markdown("🔵 <span style='color: blue; font-size: 12px;'>Baik</span>", unsafe_allow_html=True)
        elif value >= 60:
            st.markdown("🟡 <span style='color: orange; font-size: 12px;'>Cukup</span>", unsafe_allow_html=True)
        else:
            st.markdown("🔴 <span style='color: red; font-size: 12px;'>Perlu Ditingkatkan</span>", unsafe_allow_html=True)

        return value


def render_summary_card(scores: dict):
    """Render summary card of entered scores."""
    st.markdown("### 📊 Ringkasan Nilai")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    # Calculate statistics
    subject_scores = [scores[s['key']] for s in SUBJECTS if s['key'] != 'gpa']
    avg = sum(subject_scores) / len(subject_scores) if subject_scores else 0

    with col1:
        st.metric("Rata-rata", f"{avg:.1f}")

    with col2:
        st.metric("Tertinggi", f"{max(subject_scores):.1f}" if subject_scores else "-")

    with col3:
        st.metric("Terendah", f"{min(subject_scores):.1f}" if subject_scores else "-")

    with col4:
        st.metric("GPA", f"{scores.get('gpa', 0):.1f}")

    # Mini bar chart
    st.markdown("#### Distribusi Nilai")
    bars = ""
    for subject in SUBJECTS[:-1]:
        score = scores.get(subject['key'], 0)

        if score >= 80:
            color = "#27ae60"
        elif score >= 70:
            color = "#3498db"
        elif score >= 60:
            color = "#f39c12"
        else:
            color = "#e74c3c"

        bars += f"""
        <div style="margin-bottom: 8px;">
            <span style="display: inline-block; width: 120px; font-size: 12px;">{subject['icon']} {subject['label'][:12]}</span>
            <span style="display: inline-block; width: 50px; text-align: right; font-size: 12px; font-weight: bold;">{score:.0f}</span>
            <div style="display: inline-block; width: 200px; background-color: #eee; border-radius: 3px; vertical-align: middle;">
                <div style="width: {score}%; background-color: {color}; height: 15px; border-radius: 3px;"></div>
            </div>
        </div>
        """
    st.markdown(bars, unsafe_allow_html=True)


# === Main Page ===
# === Access Control ===
if 'user' not in st.session_state or not st.session_state.user:
    st.error("Silakan login terlebih dahulu")
    st.stop()

if st.session_state.user.get('role') != 'siswa':
    st.warning("Halaman ini hanya untuk siswa")
    st.stop()

# Check if RIASEC scores exist
if not st.session_state.get('riasec_scores'):
    st.warning("⚠️ Harap isi Kuesioner RIASEC terlebih dahulu")
    if st.button("➡️ Ke Kuesioner RIASEC"):
        st.switch_page("pages/1_questionnaire.py")
    st.stop()

# === Header ===
st.title("📊 Input Nilai Akademik")
st.markdown("---")

st.info("""
**Petunjuk:** Masukkan nilai rapor kamu untuk 10 mata pelajaran dan GPA.
Semua nilai menggunakan skala 0-100.

Nilai ini akan dikombinasikan dengan profil RIASEC untuk memberikan rekomendasi program studi yang lebih akurat.
""")

# === Check for existing data ===
if 'academic_scores' in st.session_state and st.session_state.academic_scores:
    st.success("✅ Kamu sudah mengisi nilai akademik sebelumnya")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Isi Ulang Nilai", use_container_width=True):
            del st.session_state.academic_scores
            st.rerun()

    with col2:
        if st.button("➡️ Lihat Rekomendasi", use_container_width=True):
            st.switch_page("pages/3_result.py")

    st.markdown("---")
    render_summary_card(st.session_state.academic_scores)
    st.stop()

# === Track if form was submitted ===
if 'form_submitted' not in st.session_state:
    st.session_state['form_submitted'] = False
    st.session_state['submitted_scores'] = None

# === Input Form ===
st.markdown("### 📝 Masukkan Nilai Rapor")

# Create form
with st.form("academic_form"):
    scores = {}

    # Render subjects in groups
    for group in SUBJECT_GROUPS:
        st.markdown(f"#### {group['title']}")
        st.markdown("---")

        subjects = group['subjects']
        cols = st.columns(len(subjects)) if len(subjects) <= 4 else st.columns(2)

        for i, subject in enumerate(subjects):
            if len(subjects) <= 4:
                scores[subject['key']] = render_score_input(subject, cols[i])
            else:
                col_idx = i % 2
                if i > 0 and i % 2 == 0:
                    cols = st.columns(2)
                scores[subject['key']] = render_score_input(subject, cols[col_idx])

        st.markdown("---")

    # Submit button - use form_submit_button instead of st.button
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        submitted = st.form_submit_button(
            "🎯 Lihat Rekomendasi Program Studi",
            type="primary",
            use_container_width=True
        )

    if submitted:
        # Validate all scores
        is_valid, errors = validate_all_scores(scores)

        if is_valid:
            # Save to session state
            st.session_state.academic_scores = scores
            st.session_state.current_step = 3
            st.session_state['form_submitted'] = True
            st.session_state['submitted_scores'] = scores
            st.rerun()
        else:
            for error in errors:
                st.error(f"⚠️ {error}")

# === Show Preview AFTER form submission (outside form) ===
if st.session_state.get('form_submitted') and st.session_state.get('submitted_scores'):
    st.markdown("---")
    st.success("✅ Nilai berhasil disimpan!")
    st.balloons()

    st.markdown("### 📋 Preview Nilai")
    col1, col2 = st.columns([2, 1])

    with col1:
        render_summary_card(st.session_state['submitted_scores'])

    with col2:
        st.markdown("### 📈 Profil RIASEC")
        riasec = st.session_state.riasec_scores
        for dim in ['r', 'i', 'a', 's', 'e', 'c']:
            st.write(f"**{dim.upper()}:** {riasec.get(dim, 0):.1f}")

    st.markdown("---")

    if st.button("➡️ Lanjut ke Hasil Rekomendasi", type="primary", use_container_width=True):
        st.switch_page("pages/3_result.py")

# === Tips ===
st.markdown("---")
st.caption("""
💡 **Tips:**
- Nilai bisa berupa desimal (contoh: 85.5)
- Pastikan nilai yang dimasukkan sesuai dengan rapor kamu
- GPA adalah nilai rata-rata keseluruhan semester
- Kamu bisa mengisi ulang nilai sebelum melihat rekomendasi
""")