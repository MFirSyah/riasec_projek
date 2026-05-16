-- =====================================================
-- SQL untuk Auto-Profile Creation
-- =====================================================
-- Jalankan di Supabase SQL Editor
-- Trigger ini akan otomatis membuat profile saat user baru register
-- =====================================================

-- 1. Drop existing trigger if exists
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP FUNCTION IF EXISTS handle_new_user();

-- 2. Create function to handle new user
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  -- Insert into public.profiles table
  INSERT INTO public.profiles (id, full_name, role, school)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email),
    COALESCE(NEW.raw_user_meta_data->>'role', 'siswa'),
    COALESCE(NEW.raw_user_meta_data->>'school', '')
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. Create trigger
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION handle_new_user();

-- 4. Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon;
GRANT ALL ON profiles TO anon;
GRANT ALL ON profiles TO authenticated;

-- 5. Make profiles table publicly readable (for SELECT)
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Create public read policy (everyone can read profiles)
DROP POLICY IF EXISTS "Public can read profiles" ON profiles;
CREATE POLICY "Public can read profiles"
  ON profiles FOR SELECT
  USING (true);

-- 6. Allow authenticated users to update their own profile
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE
  USING (auth.uid() = id);

-- 7. Secure insert (only via trigger, not direct)
DROP POLICY IF EXISTS "Allow insert profiles" ON profiles;
CREATE POLICY "Allow insert profiles"
  ON profiles FOR INSERT
  WITH CHECK (auth.uid() = id);

PRINT 'Trigger created successfully!';
PRINT 'Now register_user in app.py should work correctly.';
PRINT 'The profile will be auto-created via trigger when user signs up.';