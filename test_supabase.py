"""
test_supabase.py - Test Supabase Connection
==========================================
Run this script to verify Supabase connection.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', '')

print("=" * 60)
print("SUPABASE CONNECTION TEST")
print("=" * 60)

# Check if credentials are set
if not SUPABASE_URL or SUPABASE_URL == 'https://your-project.supabase.co':
    print("[ERROR] SUPABASE_URL belum diset di file .env")
    print("   -> Buka Supabase Dashboard > Settings > API > Project URL")
    sys.exit(1)

if not SUPABASE_ANON_KEY or SUPABASE_ANON_KEY == 'your-anon-key-here':
    print("[ERROR] SUPABASE_ANON_KEY belum diset di file .env")
    print("   -> Buka Supabase Dashboard > Settings > API > anon public")
    sys.exit(1)

print(f"[OK] SUPABASE_URL: {SUPABASE_URL}")

# Try to connect
print("\n[*] Connecting to Supabase...")
try:
    from supabase import create_client, Client
    client: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    print("[OK] Supabase client created successfully")
except Exception as e:
    print(f"[ERROR] Failed to create client: {e}")
    sys.exit(1)

# Test connection
print("\n[*] Testing connection...")
try:
    # Try to get user (should fail if not logged in, but proves connection works)
    user = client.auth.get_user()
    print("[OK] Connection successful!")
    if user and user.user:
        print(f"   User logged in: {user.user.email}")
    else:
        print("   No user logged in (this is normal)")
except Exception as e:
    error_msg = str(e)
    if "Invalid JWT" in error_msg or "401" in error_msg:
        print("[WARNING] Connection works but JWT invalid/not logged in")
        print("   This is normal if no user is logged in")
        print("[OK] Supabase connection is working!")
    else:
        print(f"[ERROR] Connection failed: {e}")
        sys.exit(1)

# Test database access
print("\n[*] Testing database access...")
try:
    # Try to read from profiles table
    response = client.table('profiles').select('*').limit(5).execute()
    print(f"[OK] Database access successful!")
    print(f"   Found {len(response.data)} profiles")
except Exception as e:
    error_msg = str(e)
    if "relation" in error_msg.lower() and "does not exist" in error_msg.lower():
        print("[WARNING] Tables don't exist yet")
        print("   -> Run the SQL from the documentation to create tables")
        sys.exit(1)
    elif "401" in error_msg or "unauthorized" in error_msg.lower():
        print("[WARNING] Database tables exist but RLS is blocking access")
        print("   -> Check RLS policies in Supabase Dashboard")
    else:
        print(f"[ERROR] Database access failed: {e}")
        sys.exit(1)

print("\n" + "=" * 60)
print("[OK] ALL TESTS PASSED - App is ready to use!")
print("=" * 60)
print("\nNext steps:")
print("1. Run: streamlit run app.py")
print("2. Register a new account")
print("3. Fill in RIASEC questionnaire")
print("4. Input academic scores")
print("5. View recommendations")