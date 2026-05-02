-- procedures.sql
-- Run once:  psql -d phonebook -f procedures.sql

-- ── 1. add_phone ──────────────────────────────────────────
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_id INTEGER;
BEGIN
    SELECT id INTO v_id
    FROM contacts
    WHERE first_name ILIKE p_contact_name
       OR (first_name || ' ' || last_name) ILIKE p_contact_name
    LIMIT 1;

    IF v_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_id, p_phone, p_type);
END;
$$;

-- ── 2. move_to_group ─────────────────────────────────────
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id   INTEGER;
BEGIN
    -- Find or create group
    INSERT INTO groups (name)
    VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;

    -- Find contact
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE first_name ILIKE p_contact_name
       OR (first_name || ' ' || last_name) ILIKE p_contact_name
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;
END;
$$;

-- ── 3. search_contacts (function) ────────────────────────
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    id         INTEGER,
    first_name VARCHAR,
    last_name  VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    grp        VARCHAR,
    phones     TEXT
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.first_name,
        c.last_name,
        c.email,
        c.birthday,
        g.name                                        AS grp,
        STRING_AGG(p.phone || ' (' || p.type || ')', ', ') AS phones
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones p ON p.contact_id = c.id
    WHERE
        c.first_name ILIKE '%' || p_query || '%'
     OR c.last_name  ILIKE '%' || p_query || '%'
     OR c.email      ILIKE '%' || p_query || '%'
     OR p.phone      ILIKE '%' || p_query || '%'
    GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name;
END;
$$;

-- ── 4. paginated_contacts (from Practice 8, extended) ────
CREATE OR REPLACE FUNCTION paginated_contacts(
    p_limit  INTEGER,
    p_offset INTEGER,
    p_sort   VARCHAR DEFAULT 'name'
)
RETURNS TABLE (
    id         INTEGER,
    first_name VARCHAR,
    last_name  VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    grp        VARCHAR,
    phones     TEXT
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY EXECUTE
    FORMAT(
      'SELECT c.id, c.first_name, c.last_name, c.email, c.birthday,
              g.name,
              STRING_AGG(p.phone || '' ('' || p.type || '')'', '', '')
       FROM contacts c
       LEFT JOIN groups g ON g.id = c.group_id
       LEFT JOIN phones p ON p.contact_id = c.id
       GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
       ORDER BY %s
       LIMIT %s OFFSET %s',
      CASE p_sort
          WHEN 'birthday'   THEN 'c.birthday'
          WHEN 'date_added' THEN 'c.created_at'
          ELSE 'c.first_name'
      END,
      p_limit, p_offset
    );
END;
$$;