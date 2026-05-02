import psycopg2
import json

def get_db_connection():
    return psycopg2.connect(
        host="localhost", 
        database="postgres", 
        user="postgres", 
        password="enhypen301120"
    )

def export_to_json(file_name="contacts.json"):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.name, c.email, c.birthday, g.name, 
               json_agg(json_build_object('phone', p.phone, 'type', p.type))
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        GROUP BY c.id, g.name
    """)
    rows = cur.fetchall()
    data = []
    for r in rows:
        data.append({
            "name": r[0], 
            "email": r[1],
            "birthday": str(r[2]), 
            "group": r[3], 
            "phones": r[4]
        })
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)
    cur.close()
    conn.close()

def import_from_json(file_name):
    with open(file_name, "r") as f:
        data = json.load(f)
    conn = get_db_connection()
    cur = conn.cursor()
    for item in data:
        cur.execute("SELECT id FROM contacts WHERE name = %s", (item['name'],))
        exists = cur.fetchone()
        if exists:
            ans = input(f"{item['name']} exists. Overwrite? (y/n): ")
            if ans.lower() != 'y': continue
            cur.execute("DELETE FROM contacts WHERE id = %s", (exists[0],))
        
        cur.execute("INSERT INTO contacts (name, email, birthday) VALUES (%s, %s, %s) RETURNING id",
                    (item['name'], item.get('email'), item.get('birthday')))
        c_id = cur.fetchone()[0]
        for ph in item.get('phones', []):
            if ph.get('phone'):
                cur.execute("INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)", (c_id, ph['phone'], ph['type']))
    conn.commit()
    cur.close()
    conn.close()

def paginated_nav():
    conn = get_db_connection()
    cur = conn.cursor()
    limit = 5
    offset = 0
    while True:
        cur.execute("SELECT name FROM contacts ORDER BY name LIMIT %s OFFSET %s", (limit, offset))
        rows = cur.fetchall()
        if not rows and offset > 0:
            print("No more records.")
            offset -= limit
            continue
        for r in rows: 
            print(f"{r[0]}")
        cmd = input("n-next, p-prev, q-quit: ").lower()
        if cmd == 'n': offset += limit
        elif cmd == 'p': offset = max(0, offset - limit)
        elif cmd == 'q': break
    cur.close()
    conn.close()

if __name__ == "__main__":
    paginated_nav()
  
#INSERT INTO contacts (name, email, birthday) 
#VALUES ('Alina', 'alina@example.com', '2000-01-01');