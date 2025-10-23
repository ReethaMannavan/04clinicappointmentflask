import sqlite3

def init_db():
    conn = sqlite3.connect("clinic.db")
    cur = conn.cursor()

    # Patients table
    cur.execute('''CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT NOT NULL,
        patient_email TEXT NOT NULL,
        patient_phone TEXT NOT NULL,
        doctor TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        status TEXT DEFAULT 'Pending'
    )''')

    # Doctors table
    cur.execute('''CREATE TABLE IF NOT EXISTS doctor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')

    # Default doctor
    cur.execute("SELECT * FROM doctor WHERE username = ?", ("doctor",))
    if not cur.fetchone():
        cur.execute("INSERT INTO doctor (username, password) VALUES (?, ?)", ("doctor", "doctor123"))

    conn.commit()
    conn.close()
    print("✅ Clinic DB initialized successfully!")

if __name__ == "__main__":
    init_db()
