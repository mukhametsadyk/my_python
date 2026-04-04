CREATE OR REPLACE FUNCTION search_contacts(p TEXT)
RETURNS TABLE(name VARCHAR, phone VARCHAR)
AS $func$
BEGIN
    RETURN QUERY
    SELECT c.name, c.phone
    FROM contacts c
    WHERE c.name ILIKE '%'  '%';
END;
$func$
LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_contacts(limit_val INT, offset_val INT)
RETURNS TABLE(id INT, name VARCHAR, phone VARCHAR)
AS $func$
BEGIN
    RETURN QUERY
    SELECT * FROM contacts
    LIMIT limit_val OFFSET offset_val;
END;
$func$
LANGUAGE plpgsql;
