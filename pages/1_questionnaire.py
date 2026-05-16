"""
pages/1_questionnaire.py — RIASEC Questionnaire Page
====================================================
Halaman kuesioner RIASEC 24 item dengan radar chart hasil.
"""

import streamlit as st
import json
import os
import plotly.graph_objects as go
import plotly.express as px

# === Page Configuration ===
st.set_page_config(
    page_title="Kuesioner RIASEC",
    page_icon="📝",
    layout="wide"
)

# === Load Questionnaire Data ===
@st.cache_data
def load_questionnaire():
    """Load questionnaire from JSON file."""
    path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'data',
        'questionnaire.json'
    )
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# === Scoring Functions ===
def calculate_dimension_score(answers: list, dimension: str) -> float:
    """Calculate normalized score for a dimension.

    Formula: (raw_score - 4) / 16 * 100
    Raw score = sum of 4 answers (4-20)
    Output: 0-100

    Args:
        answers: List of 4 integer answers (1-5)
        dimension: Dimension letter (R, I, A, S, E, C)

    Returns:
        Normalized score 0-100
    """
    raw_score = sum(answers)
    normalized = ((raw_score - 4) / 16) * 100
    return round(normalized, 2)


def calculate_all_scores(answers: dict) -> dict:
    """Calculate all RIASEC scores from answers.

    Args:
        answers: {question_id: answer_value}

    Returns:
        {'r': float, 'i': float, 'a': float, 's': float, 'e': float, 'c': float}
    """
    dimensions = ['R', 'I', 'A', 'S', 'E', 'C']
    scores = {}

    for dim in dimensions:
        dim_answers = [
            answers[q['id']]
            for q in questionnaire['questions']
            if q['dimension'] == dim
        ]
        scores[dim.lower()] = calculate_dimension_score(dim_answers, dim)

    return scores


# === UI Functions ===
def render_scale_labels():
    """Render scale value labels for slider."""
    return {
        1: "Sangat Tidak Setuju",
        2: "Tidak Setuju",
        3: "Netral",
        4: "Setuju",
        5: "Sangat Setuju"
    }


def create_radar_chart(scores: dict) -> go.Figure:
    """Create radar chart for RIASEC scores using Plotly.

    Args:
        scores: {'r': float, 'i': float, 'a': float, 's': float, 'e': float, 'c': float}

    Returns:
        Plotly Figure object
    """
    dimensions = ['Realistic', 'Investigative', 'Artistic', 'Social', 'Enterprising', 'Conventional']
    short_dims = ['R', 'I', 'A', 'S', 'E', 'C']
    values = [
        scores.get('r', 0),
        scores.get('i', 0),
        scores.get('a', 0),
        scores.get('s', 0),
        scores.get('e', 0),
        scores.get('c', 0)
    ]
    # Close the polygon by appending first value
    values.append(values[0])
    short_dims.append('R')

    fig = go.Figure()

    # Add trace
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=short_dims,
        fill='toself',
        fillcolor='rgba(26, 82, 118, 0.3)',
        line=dict(color='#1a5276', width=2),
        name='Profil RIASEC',
        hovertemplate='<b>%{theta}</b><br>Skor: %{r:.1f}<extra></extra>'
    ))

    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10),
                angle=90
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color='#1a5276'),
                rotation=90,
                direction='clockwise'
            )
        ),
        showlegend=False,
        height=400,
        margin=dict(t=30, b=30, l=30, r=30),
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif")
    )

    return fig


def render_progress_bar(current: int, total: int):
    """Render progress bar."""
    progress = current / total
    st.progress(progress)
    st.caption(f"Pertanyaan {current} dari {total}")


def render_question_slider(question_num: int, question_text: str, key: str):
    """Render a single question with slider."""
    # Container for question
    st.markdown(f"""
    <div style="background-color: #ffffff; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #dee2e6; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <div style="display: flex; align-items: flex-start; gap: 12px;">
            <span style="background-color: #1a5276; color: white; padding: 6px 14px; border-radius: 20px; font-size: 14px; font-weight: bold; min-width: 40px; text-align: center;">
                {question_num}
            </span>
            <p style="margin: 0; font-size: 16px; line-height: 1.5; color: #212529;">
                {question_text}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Scale labels above slider
    st.markdown("<p style='text-align: center; color: #6c757d; font-size: 12px; margin-bottom: 5px;'>Pilih jawaban:</p>", unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    with col1:
        st.markdown("<p style='text-align:center; font-size:11px; color:#dc3545; font-weight: bold;'>1</p>", unsafe_allow_html=True)
    with col2:
        st.markdown("<p style='text-align:center; font-size:11px; color:#fd7e14; font-weight: bold;'>2</p>", unsafe_allow_html=True)
    with col3:
        st.markdown("<p style='text-align:center; font-size:11px; color:#ffc107; font-weight: bold;'>3</p>", unsafe_allow_html=True)
    with col4:
        st.markdown("<p style='text-align:center; font-size:11px; color:#28a745; font-weight: bold;'>4</p>", unsafe_allow_html=True)
    with col5:
        st.markdown("<p style='text-align:center; font-size:11px; color:#17a2b8; font-weight: bold;'>5</p>", unsafe_allow_html=True)

    st.markdown("""
    <p style='text-align: center; font-size: 10px; color: #adb5bd;'>STS &nbsp;&nbsp;&nbsp;&nbsp; TS &nbsp;&nbsp;&nbsp;&nbsp; N &nbsp;&nbsp;&nbsp;&nbsp; S &nbsp;&nbsp;&nbsp;&nbsp; SS</p>
    """, unsafe_allow_html=True)

    value = st.slider(
        label=f"Slider untuk pertanyaan #{question_num}",
        min_value=1,
        max_value=5,
        value=3,
        step=1,
        key=f"q_{key}",
        label_visibility="collapsed"
    )

    return value


# === Main Page ===
# Load data
questionnaire = load_questionnaire()
questions = questionnaire['questions']

# === Access Control ===
if 'user' not in st.session_state or not st.session_state.user:
    st.error("Silakan login terlebih dahulu")
    st.stop()

if st.session_state.user.get('role') != 'siswa':
    st.warning("Halaman ini hanya untuk siswa")
    st.stop()

# === Header ===
st.title("📝 Kuesioner RIASEC")
st.markdown("---")

# Instructions
st.info(f"""
**Petunjuk:** {questionnaire['meta']['instructions']}

Pilih angka 1-5 yang paling menggambarkan dirimu saat ini.
""")

# Dimension info
dimensions = questionnaire['meta']['dimensions']
st.markdown(f"""
**6 Dimensi RIASEC:**
{' • '.join([f'`{d}`' for d in dimensions])}

Setiap dimensi memiliki 4 pertanyaan.
""")

st.markdown("---")

# === Initialize Session State ===
if 'answers' not in st.session_state:
    st.session_state.answers = {}

if 'current_section' not in st.session_state:
    st.session_state.current_section = 0

# Section definitions (4 questions each)
sections = [
    {'dimension': 'R', 'label': 'Realistic', 'questions': [q for q in questions if q['dimension'] == 'R']},
    {'dimension': 'I', 'label': 'Investigative', 'questions': [q for q in questions if q['dimension'] == 'I']},
    {'dimension': 'A', 'label': 'Artistic', 'questions': [q for q in questions if q['dimension'] == 'A']},
    {'dimension': 'S', 'label': 'Social', 'questions': [q for q in questions if q['dimension'] == 'S']},
    {'dimension': 'E', 'label': 'Enterprising', 'questions': [q for q in questions if q['dimension'] == 'E']},
    {'dimension': 'C', 'label': 'Conventional', 'questions': [q for q in questions if q['dimension'] == 'C']},
]

# Dimension colors
dim_colors = {
    'R': '#e74c3c',  # Red
    'I': '#3498db',  # Blue
    'A': '#9b59b6',  # Purple
    'S': '#2ecc71',  # Green
    'E': '#f1c40f',  # Yellow
    'C': '#34495e',  # Dark Gray
}

# === Section Navigation ===
st.sidebar.title("📋 Dimensi RIASEC")
st.sidebar.markdown("---")

total_questions = len(questions)
answered = len(st.session_state.answers)

# Progress in sidebar
st.sidebar.progress(answered / total_questions, text="Kemajuan")
st.sidebar.caption(f"{answered}/{total_questions} pertanyaan dijawab")

st.sidebar.markdown("---")

# Dimension status
for i, section in enumerate(sections):
    dim = section['dimension']
    dim_questions = section['questions']
    dim_answered = sum(1 for q in dim_questions if q['id'] in st.session_state.answers)

    color = dim_colors[dim]

    if dim_answered == len(dim_questions):
        status = "✅"
    elif dim_answered > 0:
        status = "🔄"
    else:
        status = "⬜"

    if st.sidebar.button(
        f"{status} `{dim}` {section['label']} ({dim_answered}/{len(dim_questions)})",
        key=f"nav_{i}"
    ):
        st.session_state.current_section = i
        st.rerun()

st.sidebar.markdown("---")

# === Main Content ===
if 'show_results' in st.session_state and st.session_state.show_results:
    # === RESULTS VIEW ===
    st.subheader("🎯 Hasil Profil RIASEC Kamu")

    scores = st.session_state.riasec_scores

    # Create columns for scores display
    col1, col2 = st.columns([2, 1])

    with col1:
        # Radar chart
        fig = create_radar_chart(scores)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Skor per Dimensi")
        for dim in ['r', 'i', 'a', 's', 'e', 'c']:
            dim_upper = dim.upper()
            score = scores.get(dim, 0)
            color = dim_colors[dim_upper]
            label = next(s['label'] for s in sections if s['dimension'] == dim_upper)

            # Create progress bar for each dimension
            st.markdown(f"""
            <div style="margin-bottom: 10px;">
                <span style="font-weight: bold; color: {color};">{dim_upper} - {label}</span>
                <div style="background-color: #e0e0e0; border-radius: 5px; height: 20px; overflow: hidden;">
                    <div style="width: {score}%; background-color: {color}; height: 100%; border-radius: 5px; display: flex; align-items: center; justify-content: center;">
                        <span style="color: white; font-weight: bold; font-size: 12px;">{score:.0f}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Interpretation
        max_dim = max(scores, key=scores.get)
        max_label = next(s['label'] for s in sections if s['dimension'] == max_dim.upper())
        st.info(f"**Dominan:** {max_dim.upper()} - {max_label}")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Isi Ulang Kuesioner", use_container_width=True):
            st.session_state.answers = {}
            st.session_state.show_results = False
            st.session_state.current_section = 0
            st.rerun()

    with col2:
        if st.button("➡️ Lanjut ke Input Nilai Rapor", use_container_width=True):
            st.switch_page("pages/2_academic_input.py")

else:
    # === QUESTIONNAIRE VIEW ===
    current_section = st.session_state.current_section
    section = sections[current_section]

    # Section header
    dim = section['dimension']
    dim_color = dim_colors[dim]
    dim_questions = section['questions']

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {dim_color}20, {dim_color}40); padding: 20px; border-radius: 15px; margin-bottom: 20px; border: 2px solid {dim_color};">
        <h2 style="color: {dim_color}; margin: 0;">{dim} - {section['label']}</h2>
        <p style="color: #666; margin: 5px 0 0 0;">4 pertanyaan tentang dimensi {section['label']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Progress
    total_in_section = len(dim_questions)
    answered_in_section = sum(1 for q in dim_questions if q['id'] in st.session_state.answers)
    progress = answered_in_section / total_in_section
    st.progress(progress)
    st.caption(f"{answered_in_section}/{total_in_section} dijawab")

    # Render questions
    answers = {}
    for idx, question in enumerate(dim_questions):
        answer = render_question_slider(
            question_num=question['id'],
            question_text=question['text'],
            key=f"{dim}_{idx}"
        )
        answers[question['id']] = answer

        # Update session state for each answer
        st.session_state.answers[question['id']] = answer

    st.markdown("---")

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if current_section > 0:
            if st.button("⬅️ Dimensi Sebelumnya", use_container_width=True):
                st.session_state.current_section = current_section - 1
                st.rerun()

    with col2:
        # Check if section is complete
        section_complete = all(q['id'] in st.session_state.answers for q in dim_questions)

        if section_complete:
            st.success("✅ Semua pertanyaan terjawab")
        else:
            missing = sum(1 for q in dim_questions if q['id'] not in st.session_state.answers)
            st.warning(f"⬜ {missing} pertanyaan belum dijawab")

    with col3:
        if current_section < len(sections) - 1:
            if st.button("Dimensi Berikutnya ➡️", use_container_width=True):
                st.session_state.current_section = current_section + 1
                st.rerun()
        else:
            # Final section - show submit button
            all_answered = len(st.session_state.answers) == total_questions
            if all_answered:
                if st.button("🎯 Lihat Hasil Profil", type="primary", use_container_width=True):
                    # Calculate scores
                    scores = calculate_all_scores(st.session_state.answers)
                    st.session_state.riasec_scores = scores
                    st.session_state.show_results = True
                    st.rerun()
            else:
                remaining = total_questions - len(st.session_state.answers)
                st.button(f"🔒 Selesaikan semua ({remaining} tersisa)", disabled=True, use_container_width=True)

# === Footer ===
st.markdown("---")
st.caption("""
💡 **Tips:** Jawablah berdasarkan apa yang kamu rasakan saat ini, bukan siapa yang ingin kamu menjadi.
Hasil kuesioner ini akan digabungkan dengan nilai akademik untuk memberikan rekomendasi program studi.
""")