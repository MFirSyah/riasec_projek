"""
app.py — Entry Point for RIASEC Career App
===========================================
Streamlit application with authentication and role-based routing.
"""

import streamlit as st

from utils.supabase_client import (
    get_client,
    get_profile
)

# === Theme Configuration ===
THEMES = {
    "light": {
        "primaryColor": "#1a5276",
        "backgroundColor": "#ffffff",
        "secondaryBackgroundColor": "#f0f2f6",
        "textColor": "#262730",
        "font": "sans-serif",
        "css": """
            <style>
            /* Light Mode Styles */
            :root {
                --primary: #1a5276;
                --bg: #ffffff;
                --bg-secondary: #f0f2f6;
                --text: #262730;
            }
            .stApp { background-color: var(--bg); }
            </style>
        """
    },
    "dark": {
        "primaryColor": "#3498db",
        "backgroundColor": "#0e1117",
        "secondaryBackgroundColor": "#262730",
        "textColor": "#fafafa",
        "font": "sans-serif",
        "css": """
            <style>
            /* Dark Mode Styles */
            :root {
                --primary: #3498db;
                --bg: #0e1117;
                --bg-secondary: #262730;
                --text: #fafafa;
            }
            .stApp { background-color: var(--bg); }
            .css-1d391kg, .css-1v0md5e, .css-1offfwp { background-color: var(--bg-secondary) !important; }
            .st-bb, .st-at { background-color: var(--bg) !important; }
            h1, h2, h3, h4, h5, h6, p, span, label { color: var(--text) !important; }
            .st-cj, .st-c0, .st-c1 { color: var(--text) !important; }
            .st-dm, .st-dn, .st-do, .st-dp { color: var(--text) !important; }
            div[data-testid="stToolbar"] { background-color: var(--bg-secondary); }
            .streamlit-expanderHeader { background-color: var(--bg-secondary); color: var(--text); }
            </style>
        """
    }
}


def get_theme_css(theme_name: str) -> str:
    """Get CSS for the selected theme."""
    return THEMES.get(theme_name, THEMES["light"]).get("css", "")


def apply_theme_config(theme_name: str):
    """Apply theme configuration to Streamlit."""
    theme = THEMES.get(theme_name, THEMES["light"])
    st.session_state['theme_config'] = {
        "primaryColor": theme["primaryColor"],
        "backgroundColor": theme["backgroundColor"],
        "secondaryBackgroundColor": theme["secondaryBackgroundColor"],
        "textColor": theme["textColor"],
    }


# === Page Config (will be called with theme) ===
def setup_page_config():
    """Setup page configuration with theme."""
    # Get theme from session state, default to light
    theme_name = st.session_state.get('theme', 'light')

    # Apply theme config
    apply_theme_config(theme_name)

    # Inject CSS
    st.markdown(get_theme_css(theme_name), unsafe_allow_html=True)

    # Set page config
    st.set_page_config(
        page_title="RIASEC Career App",
        page_icon="🎓",
        layout="centered",
        initial_sidebar_state="collapsed"
    )


def init_session_state():
    """Initialize session state variables."""
    defaults = {
        'user': None,
        'profile': None,
        'riasec_scores': None,
        'academic_scores': None,
        'recommendations': None,
        'authenticated': False,
        'theme': 'light',  # Default to light mode
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# === Theme Toggle Component ===
def render_theme_toggle():
    """Render theme toggle in sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎨 Tema")

    col1, col2 = st.sidebar.columns(2)

    current_theme = st.session_state.get('theme', 'light')

    with col1:
        if st.button("☀️ Light", use_container_width=True,
                     type="secondary" if current_theme != 'light' else "primary"):
            st.session_state['theme'] = 'light'
            st.rerun()

    with col2:
        if st.button("🌙 Dark", use_container_width=True,
                     type="secondary" if current_theme != 'dark' else "primary"):
            st.session_state['theme'] = 'dark'
            st.rerun()

    st.sidebar.markdown("---")

# === Supabase Auth Helper ===
def init_supabase():
    """Initialize Supabase client."""
    try:
        client = get_client()
        return client
    except ValueError as e:
        st.error(f"Konfigurasi Supabase tidak ditemukan: {e}")
        st.info("Pastikan file .env berisi SUPABASE_URL dan SUPABASE_ANON_KEY")
        return None


# === Authentication Functions ===
def login_user(email: str, password: str):
    """Login user with email and password."""
    client = init_supabase()
    if not client:
        return None

    try:
        session = client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return session
    except Exception as e:
        st.error(f"Login gagal: {str(e)}")
        return None


def register_user(email: str, password: str, full_name: str, role: str, school: str = ''):
    """Register new user - profile will be auto-created by database trigger."""
    client = init_supabase()
    if not client:
        return None, "Konfigurasi Supabase tidak ditemukan"

    try:
        # Create auth user with metadata
        # Database trigger will auto-create profile in public.profiles table
        session = client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name,
                    "role": role,
                    "school": school
                }
            }
        })

        if session and session.user:
            return session, None
        else:
            return None, "Registrasi gagal. Silakan coba lagi."

    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            return None, "Email sudah terdaftar. Silakan login."
        return None, f"Registrasi gagal: {error_msg}"


def logout_user():
    """Logout current user."""
    client = init_supabase()
    if client:
        client.auth.sign_out()


def get_current_user():
    """Get current authenticated user."""
    client = init_supabase()
    if not client:
        return None

    try:
        user = client.auth.get_user()
        return user.user if user else None
    except Exception:
        return None


def get_user_profile(user_id: str):
    """Get user profile from database."""
    return get_profile(user_id)


# === Session State Initialization ===
def init_session_state():
    """Initialize session state variables."""
    defaults = {
        'user': None,
        'profile': None,
        'riasec_scores': None,
        'academic_scores': None,
        'recommendations': None,
        'authenticated': False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# === UI Components ===
def render_login_form():
    """Render login form."""
    st.title("🎓 RIASEC Career App")
    st.markdown("---")
    st.subheader("Login")

    with st.form("login_form"):
        email = st.text_input("Email", placeholder="email@contoh.com")
        password = st.text_input("Password", type="password")

        col1, col2 = st.columns([1, 1])
        with col1:
            submitted = st.form_submit_button("Login", use_container_width=True)
        with col2:
            if st.form_submit_button("Daftar Akun Baru", use_container_width=True):
                st.session_state['show_register'] = True
                st.rerun()

        if submitted:
            if not email or not password:
                st.warning("Mohon isi semua field")
            else:
                with st.spinner("Login..."):
                    session = login_user(email, password)
                    if session:
                        user_profile = get_user_profile(session.user.id)
                        st.session_state['user'] = {
                            'id': session.user.id,
                            'email': session.user.email,
                            'role': user_profile.get('role', 'siswa') if user_profile else 'siswa',
                            'full_name': user_profile.get('full_name', '') if user_profile else '',
                            'school': user_profile.get('school', '') if user_profile else ''
                        }
                        st.session_state['profile'] = user_profile
                        st.session_state['authenticated'] = True
                        st.success("Login berhasil!")
                        st.rerun()
                    else:
                        st.error("Email atau password salah")


def render_register_form():
    """Render registration form."""
    st.title("🎓 RIASEC Career App")
    st.markdown("---")
    st.subheader("Daftar Akun Baru")

    with st.form("register_form"):
        full_name = st.text_input("Nama Lengkap", placeholder="Masukkan nama lengkap")
        email = st.text_input("Email", placeholder="email@contoh.com")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Konfirmasi Password", type="password")

        st.markdown("**Role:**")
        role = st.radio(
            "Pilih role kamu:",
            options=['siswa', 'guru_bk'],
            format_func=lambda x: "👨‍🎓 Siswa" if x == 'siswa' else "👨‍🏫 Guru BK",
            horizontal=True
        )

        school = st.text_input("Nama Sekolah (opsional)", placeholder="Contoh: SMA Negeri 1 Jakarta")

        col1, col2 = st.columns([1, 1])
        with col1:
            submitted = st.form_submit_button("Daftar", use_container_width=True)
        with col2:
            if st.form_submit_button("Kembali ke Login", use_container_width=True):
                st.session_state['show_register'] = False
                st.rerun()

        if submitted:
            # Validation
            if not full_name or not email or not password:
                st.warning("Mohon isi semua field yang wajib")
            elif password != confirm_password:
                st.error("Password tidak cocok")
            elif len(password) < 6:
                st.error("Password minimal 6 karakter")
            else:
                with st.spinner("Mendaftar..."):
                    session, error = register_user(email, password, full_name, role, school)
                    if error:
                        st.error(error)
                    else:
                        st.success("Registrasi berhasil! Silakan login.")
                        st.session_state['show_register'] = False
                        st.rerun()


def render_role_selector():
    """Show role selection when user is logged in."""
    # Theme toggle
    render_theme_toggle()

    st.sidebar.success(f"👤 {st.session_state.user.get('full_name', 'User')}")
    st.sidebar.markdown(f"**Role:** {'👨‍🎓 Siswa' if st.session_state.user.get('role') == 'siswa' else '👨‍🏫 Guru BK'}")

    if st.sidebar.button("Logout", use_container_width=True):
        logout_user()
        st.session_state.clear()
        st.rerun()


def render_siswa_sidebar():
    """Render sidebar for siswa role."""
    st.sidebar.title("📋 Langkah Tes")
    st.sidebar.markdown("---")

    steps = [
        ("1️⃣", "Kuesioner RIASEC", "1_questionnaire"),
        ("2️⃣", "Input Nilai Rapor", "2_academic_input"),
        ("3️⃣", "Hasil Rekomendasi", "3_result"),
    ]

    current_page = st.session_state.get('current_step', 1)

    for i, (icon, title, _) in enumerate(steps, 1):
        if i < current_page:
            status = "✅"
        elif i == current_page:
            status = "🔵"
        else:
            status = "⬜"

        st.sidebar.write(f"{status} {icon} {title}")

    # Show completion status
    st.sidebar.markdown("---")
    if st.session_state.get('riasec_scores'):
        st.sidebar.success("✅ Kuesioner RIASEC selesai")
    else:
        st.sidebar.info("⬜ Kuesioner RIASEC belum diisi")

    if st.session_state.get('academic_scores'):
        st.sidebar.success("✅ Input nilai rapor selesai")
    else:
        st.sidebar.info("⬜ Input nilai rapor belum diisi")


def render_guru_bk_sidebar():
    """Render sidebar for guru_bk role."""
    st.sidebar.title("📊 Menu BK")
    st.sidebar.markdown("---")

    pages = [
        ("📈", "Dashboard", "4_dashboard_bk"),
        ("👤", "Profil", "5_profile"),
    ]

    for icon, title, page in pages:
        st.sidebar.write(f"{icon} {title}")

    st.sidebar.markdown("---")
    st.sidebar.info("Dashboard ini menampilkan data seluruh siswa yang telah melakukan tes.")


def render_landing():
    """Render landing page for unauthenticated users."""
    # Theme toggle at top
    render_theme_toggle()

    st.title("🎓 RIASEC Career App")
    st.markdown("---")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("""
        ### Tentang Aplikasi

        Aplikasi ini membantu siswa SMA/SMK menentukan pilihan program studi berdasarkan:

        1. **Profil Kepribadian RIASEC** — Berdasarkan teori Holland
        2. **Nilai Akademik** — Dari rapor semester

        ### Fitur

        - 📝 Kuesioner RIASEC 24 item
        - 📊 Input 10 nilai rapor
        - 🎯 Rekomendasi 5 program studi
        - 📄 Export hasil ke PDF
        - 📈 Dashboard untuk Guru BK
        """)

    with col2:
        st.markdown("""
        ### Cara Kerja

        1. **Daftar/Login** — Pilih role sebagai Siswa atau Guru BK
        2. **Isi Kuesioner** — Jawab 24 pertanyaan kepribadian
        3. **Input Nilai** — Masukkan nilai rapor kamu
        4. **Dapatkan Rekomendasi** — Lihat 5 program studi yang cocok
        5. **Simpan & Export** — Simpan hasil atau export ke PDF

        ### Mulai Sekarang

        Pilih **Login** atau **Daftar Akun Baru** untuk memulai!
        """)

    st.markdown("---")

    # Show login/register forms
    if st.session_state.get('show_register', False):
        render_register_form()
    else:
        render_login_form()


def render_main_app():
    """Render main application for authenticated users."""
    user = st.session_state.user
    role = user.get('role', 'siswa')

    # Render role-specific sidebar
    if role == 'siswa':
        render_siswa_sidebar()
    else:
        render_guru_bk_sidebar()

    render_role_selector()

    # Welcome message
    st.title(f"👋 Selamat Datang, {user.get('full_name', 'User')}!")

    if role == 'siswa':
        # Guide siswa through the steps
        if not st.session_state.get('riasec_scores'):
            st.info("👈 Mulai dengan mengisi Kuesioner RIASEC di menu sidebar")
            st.markdown("""
            ### Panduan Tes

            Ikuti langkah-langkah berikut untuk mendapatkan rekomendasi program studi:

            1. **Kuesioner RIASEC** — Jawab 24 pertanyaan tentang kepribadian kamu
            2. **Input Nilai Rapor** — Masukkan nilai 10 mata pelajaran
            3. **Hasil Rekomendasi** — Lihat 5 program studi yang cocok untukmu

            Klik menu di sidebar untuk memulai!
            """)
        elif not st.session_state.get('academic_scores'):
            st.info("👈 Lanjutkan dengan mengisi Input Nilai Rapor")
            st.markdown("""
            ### Langkah Selanjutnya

            Kamu sudah menyelesaikan kuesioner RIASEC. Sekarang lanjutkan ke langkah berikutnya!
            """)
        else:
            st.success("🎉 Kamu sudah menyelesaikan semua tes!")
            st.markdown("""
            ### Hasil Tes

            Klik **"Hasil Rekomendasi"** di sidebar untuk melihat program studi yang direkomendasikan untukmu.

            Kamu juga bisa:
            - 📄 Export hasil ke PDF
            - 💾 Simpan hasil ke database
            - 📊 Lihat detail setiap program studi
            """)
    else:
        # Guru BK dashboard
        st.markdown("""
        ### Dashboard Guru BK

        Selamat datang di dashboard bimbingan dan konseling!

        Gunakan menu di sidebar untuk:
        - 📈 Melihat statistik dan grafik
        - 📋 Melihat histori tes siswa
        - 👤 Mengelola profil
        """)


# === Main Application ===
def main():
    """Main application entry point."""
    # Initialize session state
    init_session_state()

    # Apply theme CSS
    st.markdown(get_theme_css(st.session_state.get('theme', 'light')), unsafe_allow_html=True)

    # Check authentication
    if st.session_state.authenticated and st.session_state.user:
        render_main_app()
    else:
        render_landing()


if __name__ == "__main__":
    main()
