import psycopg2
from config import get_config

def get_connection():
    return psycopg2.connect(**get_config())

def main():
    while True:
        print("\n" + "="*50)
        print("📱 PHONEBOOK — Практика 8 (Functions & Procedures)")
        print("="*50)
        print("1. Поиск контактов по шаблону")
        print("2. Добавить / обновить контакт (upsert)")
        print("3. Массовое добавление контактов")
        print("4. Показать контакты с пагинацией")
        print("5. Удалить контакт")
        print("6. Показать все контакты")
        print("0. Выход")
        print("="*50)

        choice = input("\nВыберите действие: ").strip()

        if choice == "1":
            pattern = input("Введите текст для поиска: ")
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM get_contacts_by_pattern(%s)", (pattern,))
            rows = cur.fetchall()
            print(f"\nНайдено {len(rows)} контактов:")
            for name, phone in rows:
                print(f"• {name:<25} {phone}")
            cur.close()
            conn.close()

        elif choice == "2":
            name = input("Имя контакта: ").strip()
            phone = input("Телефон: ").strip()
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("CALL upsert_contact(%s, %s)", (name, phone))
            conn.commit()
            print(f"✅ Контакт '{name}' успешно добавлен/обновлён!")
            cur.close()
            conn.close()

        elif choice == "3":
            print("Введите данные через запятую (например: Алиса,Боб,Мария)")
            names_str = input("Имена: ")
            phones_str = input("Телефоны: ")
            
            names = [n.strip() for n in names_str.split(",") if n.strip()]
            phones = [p.strip() for p in phones_str.split(",") if p.strip()]
            
            if len(names) != len(phones):
                print("❌ Количество имён и телефонов не совпадает!")
                continue
                
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("CALL bulk_insert_contacts(%s, %s, '')", (names, phones))
            conn.commit()
            print("✅ Массовая вставка завершена!")
            cur.close()
            conn.close()

        elif choice == "4":
            try:
                limit = int(input("Сколько записей показать? (по умолчанию 10): ") or 10)
                offset = int(input("Смещение (0 для первой страницы): ") or 0)
            except:
                limit, offset = 10, 0
                
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))
            rows = cur.fetchall()
            print(f"\nСтраница (показано {len(rows)} записей):")
            for name, phone in rows:
                print(f"• {name:<25} {phone}")
            cur.close()
            conn.close()

        elif choice == "5":
            name = input("Имя для удаления (Enter — пропустить): ").strip() or None
            phone = input("Телефон для удаления (Enter — пропустить): ").strip() or None
            
            if not name and not phone:
                print("❌ Нужно указать хотя бы имя или телефон!")
                continue
                
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("CALL delete_contact(%s, %s)", (name, phone))
            conn.commit()
            print("✅ Контакт удалён!")
            cur.close()
            conn.close()

        elif choice == "6":
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT name, phone FROM contacts ORDER BY name")
            rows = cur.fetchall()
            print(f"\nВсе контакты ({len(rows)}):")
            for name, phone in rows:
                print(f"• {name:<25} {phone}")
            cur.close()
            conn.close()

        elif choice == "0":
            print("👋 До свидания!")
            break

        else:
            print("❌ Неверный выбор!")

if __name__ == "__main__":
    main()