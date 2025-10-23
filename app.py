from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from database import init_db
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = "supersecretclinickey"

# Initialize DB
init_db()

# ---------------- EMAIL CONFIG ---------------- #
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'nisha.reetha30@gmail.com'
app.config['MAIL_PASSWORD'] = 'fris hfvj tbok ixrl'
app.config['MAIL_DEFAULT_SENDER'] = ('Vetri Tech Clinic', 'nisha.reetha30@gmail.com')

mail = Mail(app)

# ---------------- ROUTES ---------------- #

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/book', methods=['POST'])
def book_appointment():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    doctor = request.form['doctor']
    date = request.form['date']
    time = request.form['time']

    # Basic validation
    if not name.replace(" ","").isalpha():
        flash("❌ Name should contain only letters.", "danger")
        return redirect(url_for('home'))
    if not phone.isdigit() or len(phone) != 10:
        flash("❌ Phone must be 10 digits.", "danger")
        return redirect(url_for('home'))

    conn = sqlite3.connect("clinic.db")
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO appointments (patient_name, patient_email, patient_phone, doctor, date, time) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, email, phone, doctor, date, time))
        conn.commit()

        # Email confirmation to patient
        msg = Message(
            subject="🩺 Appointment Booked - Vetri Clinic",
            recipients=[email],
            body=f"Dear {name},\n\nYour appointment with Dr. {doctor} is booked on {date} at {time}.\n\nRegards,\nVetri Clinic"
        )
        mail.send(msg)
        flash("✅ Appointment booked! Confirmation email sent.", "success")
    except Exception as e:
        flash(f"⚠️ Error: {e}", "danger")
    finally:
        conn.close()

    return redirect(url_for('home'))

# ---------------- Doctor Login ---------------- #
@app.route('/doctor', methods=['GET','POST'])
def doctor_login():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("clinic.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM doctor WHERE username=? AND password=?", (username, password))
        doctor = cur.fetchone()
        conn.close()

        if doctor:
            session['doctor'] = username
            return redirect(url_for('doctor_dashboard'))
        else:
            flash("❌ Invalid credentials!", "danger")
    return render_template("doctor_login.html")

@app.route('/dashboard')
def doctor_dashboard():
    if 'doctor' not in session:
        return redirect(url_for('doctor_login'))

    conn = sqlite3.connect("clinic.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM appointments ORDER BY date, time")
    appointments = cur.fetchall()
    conn.close()

    return render_template("doctor_dashboard.html", appointments=appointments)

@app.route('/update_status/<int:appointment_id>/<string:new_status>')
def update_status(appointment_id, new_status):
    if 'doctor' not in session:
        return redirect(url_for('doctor_login'))

    conn = sqlite3.connect("clinic.db")
    cur = conn.cursor()
    cur.execute("SELECT patient_name, patient_email FROM appointments WHERE id=?", (appointment_id,))
    patient = cur.fetchone()
    cur.execute("UPDATE appointments SET status=? WHERE id=?", (new_status, appointment_id))
    conn.commit()
    conn.close()

    # Email reminder/notification
    if patient:
        patient_name, patient_email = patient
        subject = "🩺 Appointment Update - Vetri Clinic"
        body = f"Dear {patient_name},\n\nYour appointment status is now: {new_status}.\n\nRegards,\nVetri Clinic"
        try:
            msg = Message(subject=subject, recipients=[patient_email], body=body)
            mail.send(msg)
        except Exception as e:
            print("Email error:", e)

    flash(f"Status updated to {new_status}", "success")
    return redirect(url_for('doctor_dashboard'))

@app.route('/logout')
def logout():
    session.pop('doctor', None)
    return redirect(url_for('doctor_login'))

if __name__ == "__main__":
    app.run(debug=True)
