import sqlite3

def view_table(table_name):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        if rows:
            for row in rows:
                print(row)
        else:
            print(f"No data found in table '{table_name}'.")

    except sqlite3.OperationalError as e:
        print(f"Error: {e}")

    conn.close()

if __name__ == "__main__":
    print("View 'admins' table:")
    view_table('admins')

    print("\nView 'login_history' table:")
    view_table('login_history')
