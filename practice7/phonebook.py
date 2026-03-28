import csv
from connect import get_connection

# 1. CSV-ден мәліметтерді базаға жүктеу
def import_from_csv(file_name):
    try:
        conn = get_connection()
        cur = conn.cursor()
        with open(file_name, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                cur.execute(
                    "INSERT INTO teaching_contacts (first_name, last_name, phone_number) VALUES (%s, %s, %s)",
                    row
                )
        conn.commit()
        cur.close()
        conn.close()
        print("CSV-ден мәліметтер сәтті жүктелді!")
    except Exception as e:
        print(f"Қате (CSV): {e}")

# 2. Консоль арқылы жаңа адам қосу
def add_new_contact():
    fname = input("Аты: ")
    lname = input("Тегі: ")
    phone = input("Телефон нөмірі: ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO teaching_contacts (first_name, last_name, phone_number) VALUES (%s, %s, %s)", (fname, lname, phone))
    conn.commit()
    print("Контакт қосылды!")
    cur.close()
    conn.close()

# 3. Аты немесе нөмірі бойынша іздеу
def search_contacts():
    query = input("Іздеу (ат немесе нөмір басы): ")
    conn = get_connection()
    cur = conn.cursor()
    # ILIKE - регистрге қарамай іздеу, % - кез келген жалғасы
    cur.execute("SELECT * FROM teaching_contacts WHERE first_name ILIKE %s OR phone_number LIKE %s", (f'{query}%', f'{query}%'))
    rows = cur.fetchall()
    for row in rows:
        print(f"ID: {row[0]} | Аты: {row[1]} | Тегі: {row[2]} | Нөмірі: {row[3]}")
    cur.close()
    conn.close()

# 4. Нөмірді жаңарту
def update_contact():
    target_id = input("Өзгертетін контактінің ID-ін жаз: ")
    new_phone = input("Жаңа нөмір: ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE teaching_contacts SET phone_number = %s WHERE id = %s", (new_phone, target_id))
    conn.commit()
    print("Нөмір жаңартылды!")
    cur.close()
    conn.close()

# 5. Контактіні өшіру
def delete_contact():
    name = input("Өшіретін адамның атын жаз: ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM teaching_contacts WHERE first_name = %s", (name,))
    conn.commit()
    print(f"{name} базадан өшірілді.")
    cur.close()
    conn.close()

# Негізгі мәзір (Меню)
def main():
    while True:
        print("\n--- Телефон кітапшасы ---")
        print("1. CSV-ден жүктеу")
        print("2. Жаңа контакт қосу")
        print("3. Іздеу")
        print("4. Нөмірді жаңарту")
        print("5. Контактіні өшіру")
        print("0. Шығу")
        
        choice = input("Таңдауыңыз: ")
        
        if choice == '1': import_from_csv('contacts.csv')
        elif choice == '2': add_new_contact()
        elif choice == '3': search_contacts()
        elif choice == '4': update_contact()
        elif choice == '5': delete_contact()
        elif choice == '0': break
        else: print("Қате таңдау!")

if __name__ == "__main__":
    main()