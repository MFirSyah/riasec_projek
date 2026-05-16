-- =====================================================
-- SQL untuk Multi-School Support
-- =====================================================
-- Jalankan di Supabase SQL Editor
-- =====================================================

-- 1. Tambah kolom school ke hasil_tes
ALTER TABLE hasil_tes ADD COLUMN IF NOT EXISTS school TEXT;

-- 2. Tambah kolom school ke feedback (opsional, untuk konsistensi)
ALTER TABLE feedback ADD COLUMN IF NOT EXISTS school TEXT;

-- 3. Drop old RLS policies
DROP POLICY IF EXISTS "Guru BK can view all test results" ON hasil_tes;
DROP POLICY IF EXISTS "Users can view their own test results" ON hasil_tes;
DROP POLICY IF EXISTS "Users can insert their own test results" ON hasil_tes;

-- 4. Buat RLS policies baru dengan filter school

-- Policy: Siswa bisa INSERT hasil tes sendiri
CREATE POLICY "Students can insert their own test results"
    ON hasil_tes FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Policy: Siswa bisa SELECT data sendiri
CREATE POLICY "Students can view their own test results"
    ON hasil_tes FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: BK hanya bisa SELECT hasil tes dari sekolahnya sendiri
CREATE POLICY "BK can view own school's test results"
    ON hasil_tes FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
            AND profiles.role = 'guru_bk'
            AND profiles.school = hasil_tes.school
        )
    );

-- 5. Buat juga RLS policy untuk UPDATE dan DELETE (opsional)
DROP POLICY IF EXISTS "Students can update their own test results" ON hasil_tes;
CREATE POLICY "Students can update their own test results"
    ON hasil_tes FOR UPDATE
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Students can delete their own test results" ON hasil_tes;
CREATE POLICY "Students can delete their own test results"
    ON hasil_tes FOR DELETE
    USING (auth.uid() = user_id);

-- 6. Verifikasi policies
SELECT
    tablename,
    policyname,
    cmd,
    qual
FROM pg_policies
WHERE tablename IN ('hasil_tes', 'profiles');

-- 7. Update data yang sudah ada (kalau ada) dengan school dari profiles
UPDATE hasil_tes ht
SET school = p.school
FROM profiles p
WHERE ht.user_id = p.id
AND ht.school IS NULL;

PRINT 'Multi-school support berhasil diaktifkan!';
PRINT 'Kolom school ditambahkan ke hasil_tes';
PRINT 'RLS policies diupdate - BK hanya bisa lihat sekolah sendiri';