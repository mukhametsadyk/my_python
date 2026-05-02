"""
phonebook.py — TSIS 1: Extended PhoneBook Console App
Builds on Practice 7/8 base (CRUD, CSV import, search, pagination, stored procs).
New: groups, multiple phones, email, birthday, JSON export/import,
     filter by group, search by email, sort, paginated navigation,
     stored procedures: add_phone, move_to_group, search_contacts.
"""

import csv
import json
import os
from datetime import datetime, date

import psycopg2
from connect import get_conn
from config import PAGE_SIZE

# ══════════════════════════════════════════════════════════
#  Display helpers
# ══════════════════════════════════════════════════════════

SEP = "─" * 78

def header(title):
    print(f"\n{'═'*78}")
    print(f"  {title}")
    print(f"{'═'*78}")


def print_row(row):
    """Print one contact row from paginated/search queries."""
    cid, fname, lname, email, bday, grp, phones = row
    name = f"{fname} {lname or ''}".strip()
    print(f"  [{cid}] {name:<25} | {email or '-':<22} | {str(bday) if bday else '-':<12}"
          f" | {grp or '-':<8} | {phones or '-'}")


def print_table(rows):
    if not rows:
        print("  (no results)")
        return
    print(f"  {'ID':<5} {'Name':<25} | {'Email':<22} | {'Birthday':<12}"
          f" | {'Group':<8} | Phones")
    print(f"  {SEP}")
    for r in rows:
        print_row(r)


def input_or_none(prompt):
    v = input(prompt).strip()
    return v if v else None


# ══════════════════════════════════════════════════════════
#  DB helpers
# ══════════════════════════════════════════════════════════

def ensure_group(cur, name):
    if not name:
        return None
    cur.execute("INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (name,))
    cur.execute("SELECT id FROM groups WHERE name = %s", (name,))
    row = cur.fetchone()
    return row[0] if row else None


def list_groups(cur):
    cur.execute("SELECT id, name FROM groups ORDER BY name")
    return cur.fetchall()


# ══════════════════════════════════════════════════════════
#  1. Add contact
# ══════════════════════════════════════════════════════════

def add_contact():
    header("Add New Contact")
    fname  = input("First name: ").strip()
    if not fname:
        print("First name is required."); return
    lname  = input_or_none("Last name : ")
    email  = input_or_none("Email     : ")
    bday   = input_or_none("Birthday (YYYY-MM-DD): ")
    print("Group options: Family, Work, Friend, Other (or new name)")
    grp    = input_or_none("Group     : ")
    phone  = input_or_none("Phone     : ")
    ptype  = input("Phone type (home/work/mobile) [mobile]: ").strip() or "mobile"

    with get_conn() as conn:
        with conn.cursor() as cur:
            gid = ensure_group(cur, grp)
            cur.execute(
                "INSERT INTO contacts (first_name, last_name, email, birthday, group_id) "
                "VALUES (%s,%s,%s,%s,%s) RETURNING id",
                (fname, lname, email, bday or None, gid)
            )
            cid = cur.fetchone()[0]
            if phone:
                cur.execute(
                    "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                    (cid, phone, ptype)
                )
        conn.commit()
    print(f"✔ Contact '{fname}' added (id={cid}).")


# ══════════════════════════════════════════════════════════
#  2. View all — paginated
# ══════════════════════════════════════════════════════════

def view_contacts():
    header("All Contacts (paginated)")
    print("Sort by: 1=Name  2=Birthday  3=Date added")
    sort_choice = input("Choice [1]: ").strip() or "1"
    sort_map    = {"1": "name", "2": "birthday", "3": "date_added"}
    sort        = sort_map.get(sort_choice, "name")

    offset = 0
    while True:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM paginated_contacts(%s, %s, %s)",
                    (PAGE_SIZE, offset, sort)
                )
                rows = cur.fetchall()

        print_table(rows)
        if len(rows) < PAGE_SIZE:
            print("  (end of list)")
            break

        nav = input("\n[n]ext  [p]rev  [q]uit: ").strip().lower()
        if nav == "n":
            offset += PAGE_SIZE
        elif nav == "p":
            offset = max(0, offset - PAGE_SIZE)
        else:
            break


# ══════════════════════════════════════════════════════════
#  3. Search contacts (DB function)
# ══════════════════════════════════════════════════════════

def search_contacts():
    header("Search Contacts")
    query = input("Search (name / email / phone): ").strip()
    if not query:
        return
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s)", (query,))
            rows = cur.fetchall()
    print_table(rows)


# ══════════════════════════════════════════════════════════
#  4. Filter by group
# ══════════════════════════════════════════════════════════

def filter_by_group():
    header("Filter by Group")
    with get_conn() as conn:
        with conn.cursor() as cur:
            groups = list_groups(cur)
    if not groups:
        print("No groups found."); return

    for gid, gname in groups:
        print(f"  {gid}. {gname}")
    choice = input("Enter group id or name: ").strip()

    with get_conn() as conn:
        with conn.cursor() as cur:
            if choice.isdigit():
                cur.execute(
                    "SELECT c.id, c.first_name, c.last_name, c.email, c.birthday, "
                    "g.name, STRING_AGG(p.phone || ' (' || p.type || ')', ', ') "
                    "FROM contacts c "
                    "LEFT JOIN groups g ON g.id = c.group_id "
                    "LEFT JOIN phones p ON p.contact_id = c.id "
                    "WHERE c.group_id = %s "
                    "GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name",
                    (int(choice),)
                )
            else:
                cur.execute(
                    "SELECT c.id, c.first_name, c.last_name, c.email, c.birthday, "
                    "g.name, STRING_AGG(p.phone || ' (' || p.type || ')', ', ') "
                    "FROM contacts c "
                    "LEFT JOIN groups g ON g.id = c.group_id "
                    "LEFT JOIN phones p ON p.contact_id = c.id "
                    "WHERE g.name ILIKE %s "
                    "GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name",
                    (choice,)
                )
            rows = cur.fetchall()
    print_table(rows)


# ══════════════════════════════════════════════════════════
#  5. Update contact
# ══════════════════════════════════════════════════════════

def update_contact():
    header("Update Contact")
    cid = input("Contact ID to update: ").strip()
    if not cid.isdigit():
        print("Invalid ID."); return

    print("Leave blank to keep current value.")
    fname = input_or_none("New first name : ")
    lname = input_or_none("New last name  : ")
    email = input_or_none("New email      : ")
    bday  = input_or_none("New birthday (YYYY-MM-DD): ")
    grp   = input_or_none("New group      : ")

    with get_conn() as conn:
        with conn.cursor() as cur:
            if fname: cur.execute("UPDATE contacts SET first_name=%s WHERE id=%s", (fname, cid))
            if lname: cur.execute("UPDATE contacts SET last_name=%s  WHERE id=%s", (lname, cid))
            if email: cur.execute("UPDATE contacts SET email=%s      WHERE id=%s", (email, cid))
            if bday:  cur.execute("UPDATE contacts SET birthday=%s   WHERE id=%s", (bday,  cid))
            if grp:
                gid = ensure_group(cur, grp)
                cur.execute("UPDATE contacts SET group_id=%s WHERE id=%s", (gid, cid))
        conn.commit()
    print("✔ Contact updated.")


# ══════════════════════════════════════════════════════════
#  6. Delete contact
# ══════════════════════════════════════════════════════════

def delete_contact():
    header("Delete Contact")
    cid = input("Contact ID to delete: ").strip()
    if not cid.isdigit():
        print("Invalid ID."); return
    confirm = input(f"Delete contact {cid}? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled."); return
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM contacts WHERE id = %s", (cid,))
        conn.commit()
    print("✔ Contact deleted.")


# ══════════════════════════════════════════════════════════
#  7. Add phone  (stored procedure)
# ══════════════════════════════════════════════════════════

def add_phone_menu():
    header("Add Phone Number")
    name  = input("Contact name: ").strip()
    phone = input("Phone number: ").strip()
    ptype = input("Type (home/work/mobile) [mobile]: ").strip() or "mobile"
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
            conn.commit()
        print("✔ Phone added.")
    except Exception as e:
        print(f"Error: {e}")


# ══════════════════════════════════════════════════════════
#  8. Move to group  (stored procedure)
# ══════════════════════════════════════════════════════════

def move_to_group_menu():
    header("Move Contact to Group")
    name  = input("Contact name : ").strip()
    group = input("Target group : ").strip()
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("CALL move_to_group(%s, %s)", (name, group))
            conn.commit()
        print("✔ Contact moved.")
    except Exception as e:
        print(f"Error: {e}")


# ══════════════════════════════════════════════════════════
#  9. CSV import (extended)
# ══════════════════════════════════════════════════════════

def import_csv():
    header("Import from CSV")
    path = input("CSV file path [contacts.csv]: ").strip() or "contacts.csv"
    if not os.path.exists(path):
        print("File not found."); return

    added = skipped = 0
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        with get_conn() as conn:
            with conn.cursor() as cur:
                for row in reader:
                    fname = row.get("first_name", "").strip()
                    if not fname:
                        skipped += 1; continue
                    lname  = row.get("last_name",  "").strip() or None
                    email  = row.get("email",      "").strip() or None
                    bday   = row.get("birthday",   "").strip() or None
                    grp    = row.get("group",      "").strip() or None
                    phone  = row.get("phone",      "").strip() or None
                    ptype  = row.get("phone_type", "mobile").strip() or "mobile"

                    gid = ensure_group(cur, grp)
                    cur.execute(
                        "INSERT INTO contacts (first_name, last_name, email, birthday, group_id) "
                        "VALUES (%s,%s,%s,%s,%s) RETURNING id",
                        (fname, lname, email, bday or None, gid)
                    )
                    cid = cur.fetchone()[0]
                    if phone:
                        cur.execute(
                            "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                            (cid, phone, ptype)
                        )
                    added += 1
            conn.commit()
    print(f"✔ Imported: {added} added, {skipped} skipped.")


# ══════════════════════════════════════════════════════════
#  10. Export to JSON
# ══════════════════════════════════════════════════════════

def export_json():
    header("Export to JSON")
    path = input("Output file [contacts.json]: ").strip() or "contacts.json"

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.first_name, c.last_name, c.email,
                       c.birthday::text, g.name AS grp,
                       COALESCE(
                           JSON_AGG(
                               JSON_BUILD_OBJECT('phone', p.phone, 'type', p.type)
                           ) FILTER (WHERE p.id IS NOT NULL),
                           '[]'
                       ) AS phones
                FROM contacts c
                LEFT JOIN groups g ON g.id = c.group_id
                LEFT JOIN phones p ON p.contact_id = c.id
                GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
                ORDER BY c.first_name
            """)
            rows = cur.fetchall()

    contacts = []
    for r in rows:
        contacts.append({
            "id":         r[0],
            "first_name": r[1],
            "last_name":  r[2],
            "email":      r[3],
            "birthday":   r[4],
            "group":      r[5],
            "phones":     r[6],
        })

    with open(path, "w", encoding="utf-8") as f:
        json.dump(contacts, f, ensure_ascii=False, indent=2)
    print(f"✔ Exported {len(contacts)} contacts to '{path}'.")


# ══════════════════════════════════════════════════════════
#  11. Import from JSON
# ══════════════════════════════════════════════════════════

def import_json():
    header("Import from JSON")
    path = input("JSON file path [contacts.json]: ").strip() or "contacts.json"
    if not os.path.exists(path):
        print("File not found."); return

    with open(path, encoding="utf-8") as f:
        contacts = json.load(f)

    added = skipped = overwritten = 0

    with get_conn() as conn:
        with conn.cursor() as cur:
            for c in contacts:
                fname = (c.get("first_name") or "").strip()
                lname = (c.get("last_name")  or "").strip() or None
                if not fname:
                    skipped += 1; continue

                # Check duplicate
                cur.execute(
                    "SELECT id FROM contacts WHERE first_name ILIKE %s "
                    "AND (last_name ILIKE %s OR last_name IS NULL)",
                    (fname, lname or "")
                )
                existing = cur.fetchone()

                if existing:
                    choice = input(
                        f"  Duplicate: '{fname} {lname or ''}'. "
                        f"[s]kip / [o]verwrite? "
                    ).strip().lower()
                    if choice != "o":
                        skipped += 1; continue
                    cur.execute("DELETE FROM contacts WHERE id = %s", (existing[0],))
                    overwritten += 1

                email = c.get("email")   or None
                bday  = c.get("birthday")or None
                grp   = c.get("group")   or None
                gid   = ensure_group(cur, grp)

                cur.execute(
                    "INSERT INTO contacts (first_name, last_name, email, birthday, group_id) "
                    "VALUES (%s,%s,%s,%s,%s) RETURNING id",
                    (fname, lname, email, bday or None, gid)
                )
                cid = cur.fetchone()[0]

                for ph in (c.get("phones") or []):
                    cur.execute(
                        "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                        (cid, ph.get("phone"), ph.get("type", "mobile"))
                    )
                added += 1

        conn.commit()
    print(f"✔ JSON import done: {added} added, {overwritten} overwritten, {skipped} skipped.")


# ══════════════════════════════════════════════════════════
#  Main menu
# ══════════════════════════════════════════════════════════

MENU = """
╔══════════════════════════════════════╗
║        TSIS 1 — PhoneBook           ║
╠══════════════════════════════════════╣
║  1. Add contact                     ║
║  2. View all (paginated)            ║
║  3. Search contacts                 ║
║  4. Filter by group                 ║
║  5. Update contact                  ║
║  6. Delete contact                  ║
║  7. Add phone number (procedure)    ║
║  8. Move to group  (procedure)      ║
║  9. Import from CSV                 ║
║ 10. Export to JSON                  ║
║ 11. Import from JSON                ║
║  0. Exit                            ║
╚══════════════════════════════════════╝
"""

ACTIONS = {
    "1":  add_contact,
    "2":  view_contacts,
    "3":  search_contacts,
    "4":  filter_by_group,
    "5":  update_contact,
    "6":  delete_contact,
    "7":  add_phone_menu,
    "8":  move_to_group_menu,
    "9":  import_csv,
    "10": export_json,
    "11": import_json,
}


def main():
    print("\nConnecting to database …")
    try:
        with get_conn() as conn:
            print("✔ Connected.")
    except Exception as e:
        print(f"✘ Cannot connect: {e}\n"
              "Check config.py settings and make sure the DB is running.")
        return

    while True:
        print(MENU)
        choice = input("Select option: ").strip()
        if choice == "0":
            print("Goodbye!"); break
        action = ACTIONS.get(choice)
        if action:
            try:
                action()
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()