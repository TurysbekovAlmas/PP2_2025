-- ============================================================================
-- PHONEBOOK DATABASE - STORED PROCEDURES AND FUNCTIONS
-- ============================================================================

-- Connect to phonebook_db
\c phonebook_db

-- ============================================================================
-- 1. FUNCTION: Search records by pattern
-- ============================================================================
-- Returns all records matching a pattern in name, surname, or phone number

CREATE OR REPLACE FUNCTION search_contacts_by_pattern(search_pattern VARCHAR)
RETURNS TABLE (
    user_id INTEGER,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone_number VARCHAR(20),
    phone_type VARCHAR(20)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.user_id,
        u.first_name,
        u.last_name,
        u.email,
        p.phone_number,
        p.phone_type
    FROM users u
    LEFT JOIN phones p ON u.user_id = p.user_id
    WHERE 
        u.first_name ILIKE '%' || search_pattern || '%'
        OR u.last_name ILIKE '%' || search_pattern || '%'
        OR u.email ILIKE '%' || search_pattern || '%'
        OR p.phone_number ILIKE '%' || search_pattern || '%'
    ORDER BY u.last_name, u.first_name;
END;
$$ LANGUAGE plpgsql;

-- Usage example:
-- SELECT * FROM search_contacts_by_pattern('john');
-- SELECT * FROM search_contacts_by_pattern('777');
-- SELECT * FROM search_contacts_by_pattern('gmail');


-- ============================================================================
-- 2. PROCEDURE: Insert new user or update phone if exists
-- ============================================================================
-- If user exists, updates their primary phone; otherwise creates new user

CREATE OR REPLACE PROCEDURE upsert_user_phone(
    p_first_name VARCHAR(50),
    p_last_name VARCHAR(50),
    p_email VARCHAR(100),
    p_phone_number VARCHAR(20),
    p_phone_type VARCHAR(20) DEFAULT 'mobile'
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_user_id INTEGER;
    v_phone_id INTEGER;
BEGIN
    -- Check if user exists by first name and last name
    SELECT user_id INTO v_user_id
    FROM users
    WHERE first_name = p_first_name AND last_name = p_last_name
    LIMIT 1;
    
    IF v_user_id IS NULL THEN
        -- User doesn't exist, create new user
        INSERT INTO users (first_name, last_name, email)
        VALUES (p_first_name, p_last_name, p_email)
        RETURNING user_id INTO v_user_id;
        
        -- Insert phone number
        INSERT INTO phones (user_id, phone_number, phone_type, is_primary)
        VALUES (v_user_id, p_phone_number, p_phone_type, TRUE);
        
        RAISE NOTICE 'New user created: % % (ID: %)', p_first_name, p_last_name, v_user_id;
    ELSE
        -- User exists, update their primary phone
        SELECT phone_id INTO v_phone_id
        FROM phones
        WHERE user_id = v_user_id AND is_primary = TRUE
        LIMIT 1;
        
        IF v_phone_id IS NOT NULL THEN
            -- Update existing primary phone
            UPDATE phones
            SET phone_number = p_phone_number, phone_type = p_phone_type
            WHERE phone_id = v_phone_id;
            
            RAISE NOTICE 'Phone updated for user: % % (ID: %)', p_first_name, p_last_name, v_user_id;
        ELSE
            -- No primary phone exists, insert new one
            INSERT INTO phones (user_id, phone_number, phone_type, is_primary)
            VALUES (v_user_id, p_phone_number, p_phone_type, TRUE);
            
            RAISE NOTICE 'Phone added for user: % % (ID: %)', p_first_name, p_last_name, v_user_id;
        END IF;
    END IF;
    
    COMMIT;
END;
$$;

-- Usage example:
-- CALL upsert_user_phone('John', 'Doe', 'john@example.com', '+77771234567', 'mobile');
-- CALL upsert_user_phone('John', 'Doe', 'john@example.com', '+77779999999', 'work');


-- ============================================================================
-- 3. PROCEDURE: Insert multiple users with validation
-- ============================================================================
-- Creates a temporary table to store invalid records

-- First, create a table to store invalid phone numbers
CREATE TABLE IF NOT EXISTS invalid_phones_log (
    log_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone_number VARCHAR(20),
    error_message TEXT,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE PROCEDURE insert_multiple_users(
    p_users_data TEXT  -- Format: 'FirstName1,LastName1,Email1,Phone1;FirstName2,LastName2,Email2,Phone2;...'
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_user_record TEXT;
    v_user_parts TEXT[];
    v_first_name VARCHAR(50);
    v_last_name VARCHAR(50);
    v_email VARCHAR(100);
    v_phone_number VARCHAR(20);
    v_user_id INTEGER;
    v_is_valid BOOLEAN;
    v_error_message TEXT;
    v_success_count INTEGER := 0;
    v_error_count INTEGER := 0;
BEGIN
    -- Clear previous invalid logs
    DELETE FROM invalid_phones_log WHERE logged_at < NOW() - INTERVAL '1 hour';
    
    -- Loop through each user record (separated by semicolon)
    FOREACH v_user_record IN ARRAY string_to_array(p_users_data, ';')
    LOOP
        -- Skip empty records
        IF trim(v_user_record) = '' THEN
            CONTINUE;
        END IF;
        
        -- Split user data by comma
        v_user_parts := string_to_array(v_user_record, ',');
        
        -- Validate we have at least 4 parts
        IF array_length(v_user_parts, 1) < 4 THEN
            INSERT INTO invalid_phones_log (first_name, last_name, phone_number, error_message)
            VALUES ('UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'Invalid data format: ' || v_user_record);
            v_error_count := v_error_count + 1;
            CONTINUE;
        END IF;
        
        -- Extract data
        v_first_name := trim(v_user_parts[1]);
        v_last_name := trim(v_user_parts[2]);
        v_email := NULLIF(trim(v_user_parts[3]), '');
        v_phone_number := trim(v_user_parts[4]);
        
        -- Validate phone number
        v_is_valid := TRUE;
        v_error_message := '';
        
        -- Check phone format (should start with + and contain only digits after that)
        IF v_phone_number !~ '^\+?[0-9]{10,15}$' THEN
            v_is_valid := FALSE;
            v_error_message := 'Invalid phone format (should be +XXXXXXXXXXX)';
        END IF;
        
        -- Check minimum length
        IF LENGTH(v_phone_number) < 10 THEN
            v_is_valid := FALSE;
            v_error_message := 'Phone number too short (minimum 10 digits)';
        END IF;
        
        -- Check if phone already exists
        IF EXISTS (SELECT 1 FROM phones WHERE phone_number = v_phone_number) THEN
            v_is_valid := FALSE;
            v_error_message := 'Phone number already exists';
        END IF;
        
        -- Insert or log error
        IF v_is_valid THEN
            -- Insert user
            INSERT INTO users (first_name, last_name, email)
            VALUES (v_first_name, v_last_name, v_email)
            RETURNING user_id INTO v_user_id;
            
            -- Insert phone
            INSERT INTO phones (user_id, phone_number, phone_type, is_primary)
            VALUES (v_user_id, v_phone_number, 'mobile', TRUE);
            
            v_success_count := v_success_count + 1;
            RAISE NOTICE 'Successfully inserted: % % (Phone: %)', v_first_name, v_last_name, v_phone_number;
        ELSE
            -- Log invalid record
            INSERT INTO invalid_phones_log (first_name, last_name, phone_number, error_message)
            VALUES (v_first_name, v_last_name, v_phone_number, v_error_message);
            
            v_error_count := v_error_count + 1;
            RAISE WARNING 'Invalid record: % % (Phone: %) - %', v_first_name, v_last_name, v_phone_number, v_error_message;
        END IF;
    END LOOP;
    
    -- Summary
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Insertion complete!';
    RAISE NOTICE 'Successfully inserted: % users', v_success_count;
    RAISE NOTICE 'Failed (invalid): % records', v_error_count;
    RAISE NOTICE 'Check invalid_phones_log table for details';
    RAISE NOTICE '========================================';
    
    COMMIT;
END;
$$;

-- Usage example:
-- CALL insert_multiple_users('Alice,Smith,alice@mail.com,+77771111111;Bob,Jones,bob@mail.com,+77772222222;Invalid,User,test@mail.com,123');
-- SELECT * FROM invalid_phones_log ORDER BY logged_at DESC;


-- ============================================================================
-- 4. FUNCTION: Query with pagination
-- ============================================================================
-- Returns paginated results from users and phones tables

CREATE OR REPLACE FUNCTION get_contacts_paginated(
    p_limit INTEGER DEFAULT 10,
    p_offset INTEGER DEFAULT 0,
    p_order_by VARCHAR DEFAULT 'last_name'  -- Options: 'last_name', 'first_name', 'created_at'
)
RETURNS TABLE (
    user_id INTEGER,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone_number VARCHAR(20),
    phone_type VARCHAR(20),
    created_at TIMESTAMP,
    total_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    WITH total AS (
        SELECT COUNT(DISTINCT u.user_id) as cnt
        FROM users u
    )
    SELECT 
        u.user_id,
        u.first_name,
        u.last_name,
        u.email,
        p.phone_number,
        p.phone_type,
        u.created_at,
        t.cnt as total_count
    FROM users u
    LEFT JOIN phones p ON u.user_id = p.user_id
    CROSS JOIN total t
    ORDER BY 
        CASE 
            WHEN p_order_by = 'last_name' THEN u.last_name
            WHEN p_order_by = 'first_name' THEN u.first_name
            ELSE u.last_name
        END,
        u.first_name
    LIMIT p_limit
    OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;

-- Usage examples:
-- SELECT * FROM get_contacts_paginated(5, 0);  -- First 5 records
-- SELECT * FROM get_contacts_paginated(5, 5);  -- Next 5 records (page 2)
-- SELECT * FROM get_contacts_paginated(10, 0, 'first_name');  -- Order by first name


-- ============================================================================
-- 5. PROCEDURE: Delete by username or phone
-- ============================================================================
-- Deletes user by matching first name + last name OR phone number

CREATE OR REPLACE PROCEDURE delete_contact(
    p_first_name VARCHAR(50) DEFAULT NULL,
    p_last_name VARCHAR(50) DEFAULT NULL,
    p_phone_number VARCHAR(20) DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_user_id INTEGER;
    v_deleted_count INTEGER := 0;
BEGIN
    -- Option 1: Delete by phone number
    IF p_phone_number IS NOT NULL THEN
        -- Find user_id by phone number
        SELECT user_id INTO v_user_id
        FROM phones
        WHERE phone_number = p_phone_number
        LIMIT 1;
        
        IF v_user_id IS NOT NULL THEN
            -- Delete user (CASCADE will delete phones automatically)
            DELETE FROM users WHERE user_id = v_user_id;
            GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
            
            IF v_deleted_count > 0 THEN
                RAISE NOTICE 'User deleted by phone number: %', p_phone_number;
            END IF;
        ELSE
            RAISE NOTICE 'No user found with phone number: %', p_phone_number;
        END IF;
    
    -- Option 2: Delete by name
    ELSIF p_first_name IS NOT NULL AND p_last_name IS NOT NULL THEN
        DELETE FROM users
        WHERE first_name = p_first_name AND last_name = p_last_name;
        GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
        
        IF v_deleted_count > 0 THEN
            RAISE NOTICE 'Deleted % user(s) with name: % %', v_deleted_count, p_first_name, p_last_name;
        ELSE
            RAISE NOTICE 'No user found with name: % %', p_first_name, p_last_name;
        END IF;
    
    ELSE
        RAISE EXCEPTION 'Must provide either phone_number OR both first_name and last_name';
    END IF;
    
    COMMIT;
END;
$$;

-- Usage examples:
-- CALL delete_contact(p_phone_number => '+77771234567');
-- CALL delete_contact(p_first_name => 'John', p_last_name => 'Doe');


-- ============================================================================
-- HELPER FUNCTION: Get total contacts count
-- ============================================================================

CREATE OR REPLACE FUNCTION get_total_contacts_count()
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count FROM users;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- Usage: SELECT get_total_contacts_count();


-- ============================================================================
-- HELPER FUNCTION: Validate phone number format
-- ============================================================================

CREATE OR REPLACE FUNCTION is_valid_phone(p_phone VARCHAR)
RETURNS BOOLEAN AS $$
BEGIN
    -- Check if phone matches pattern: +XXXXXXXXXXX (10-15 digits)
    RETURN p_phone ~ '^\+?[0-9]{10,15}$';
END;
$$ LANGUAGE plpgsql;

-- Usage: SELECT is_valid_phone('+77771234567');


-- ============================================================================
-- TEST QUERIES
-- ============================================================================

-- Test 1: Search by pattern
-- SELECT * FROM search_contacts_by_pattern('john');

-- Test 2: Upsert user
-- CALL upsert_user_phone('Test', 'User', 'test@example.com', '+77779999999', 'mobile');

-- Test 3: Insert multiple users
-- CALL insert_multiple_users('Alice,Smith,alice@mail.com,+77771111111;Bob,Jones,bob@mail.com,+77772222222;Charlie,Brown,charlie@mail.com,+77773333333');

-- Test 4: Pagination
-- SELECT * FROM get_contacts_paginated(5, 0);

-- Test 5: Delete contact
-- CALL delete_contact(p_first_name => 'Test', p_last_name => 'User');

-- View invalid phones log
-- SELECT * FROM invalid_phones_log ORDER BY logged_at DESC;

-- ============================================================================
-- END OF SCRIPT
-- ============================================================================