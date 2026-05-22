# Maintenance

## Delete a package

```sql
WITH find_package AS (
    -- Step 1: Just SELECT the package ID (do not delete yet)
    SELECT id FROM package WHERE name = 'package'
),
find_code_files AS (
    -- Step 2: Just SELECT the related code file IDs
    SELECT id FROM code_file
    WHERE package_id IN (SELECT id FROM find_package)
),
find_metadata_files AS (
    -- Step 3: Just SELECT the related metadata file IDs
    SELECT id FROM metadata_file
    WHERE code_file_id IN (SELECT id FROM find_code_files)
       OR package_id IN (SELECT id FROM find_package)
),
-- ---------------------------------------------------------
-- Now we delete from the bottom up to respect constraints
-- ---------------------------------------------------------
delete_metadata_hashes AS (
    DELETE FROM metadata_file_hash
    WHERE metadata_file_id IN (SELECT id FROM find_metadata_files)
),
delete_code_hashes AS (
    DELETE FROM code_file_hash
    WHERE code_file_id IN (SELECT id FROM find_code_files)
),
delete_metadata_files AS (
    DELETE FROM metadata_file
    WHERE id IN (SELECT id FROM find_metadata_files)
),
delete_code_files AS (
    DELETE FROM code_file
    WHERE id IN (SELECT id FROM find_code_files)
)
-- Step 5: Finally, safely delete the package row
DELETE FROM package
WHERE id IN (SELECT id FROM find_package);
```
