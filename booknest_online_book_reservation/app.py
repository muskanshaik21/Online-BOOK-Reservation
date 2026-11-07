from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
import sqlite3, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "booknest.db")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "booknest-development-secret-change-me")

COLLEGE_DEPARTMENTS = [
    ("CSE", "Computer Science and Engineering"),
    ("ECE", "Electronics and Communication Engineering"),
    ("EEE", "Electrical and Electronics Engineering"),
    ("EIE", "Electronics and Instrumentation Engineering"),
    ("Mechanical", "Mechanical Engineering"),
    ("Civil", "Civil Engineering"),
    ("AI & DS", "Artificial Intelligence and Data Science"),
    ("IT", "Information Technology"),
]

DEPARTMENT_BOOKS = {
    "CSE": [
        ("Programming in Python", "Reema Thareja"),
        ("Data Structures Using C", "E. Balagurusamy"),
        ("Introduction to Algorithms", "Thomas H. Cormen"),
        ("Operating System Concepts", "Abraham Silberschatz"),
        ("Database System Concepts", "Henry F. Korth"),
        ("Computer Networks", "Andrew S. Tanenbaum"),
        ("Software Engineering", "Ian Sommerville"),
        ("Computer Organization and Architecture", "William Stallings"),
        ("Compiler Design", "Alfred V. Aho"),
        ("Theory of Computation", "Michael Sipser"),
        ("Cryptography and Network Security", "William Stallings"),
        ("Web Technologies", "Uttam K. Roy"),
        ("Cloud Computing", "Rajkumar Buyya"),
    ],
    "ECE": [
        ("Electronic Devices and Circuit Theory", "Robert L. Boylestad"),
        ("Microelectronic Circuits", "Adel S. Sedra"),
        ("Digital Signal Processing", "John G. Proakis"),
        ("Communication Systems", "Simon Haykin"),
        ("Signals and Systems", "Alan V. Oppenheim"),
        ("Microwave Engineering", "David M. Pozar"),
        ("Antenna Theory", "Constantine A. Balanis"),
        ("VLSI Design", "Debaprasad Das"),
        ("CMOS Digital Integrated Circuits", "Sung-Mo Kang"),
        ("Optical Fiber Communications", "Gerd Keiser"),
        ("Wireless Communications", "Theodore S. Rappaport"),
        ("Embedded Systems", "Raj Kamal"),
        ("Satellite Communications", "Dennis Roddy"),
    ],
    "EEE": [
        ("Electrical Machinery", "P. S. Bimbhra"),
        ("Power System Engineering", "I. J. Nagrath"),
        ("Modern Power System Analysis", "D. P. Kothari"),
        ("Power Electronics", "Muhammad H. Rashid"),
        ("Electrical Measurements", "A. K. Sawhney"),
        ("Control Systems Engineering", "I. J. Nagrath"),
        ("Electric Circuits", "James W. Nilsson"),
        ("High Voltage Engineering", "M. S. Naidu"),
        ("Renewable Energy Sources", "G. D. Rai"),
        ("Electrical Drives", "G. K. Dubey"),
        ("Switchgear and Protection", "Sunil S. Rao"),
        ("Generation of Electrical Energy", "B. R. Gupta"),
        ("Smart Grid Technology", "Janaka Ekanayake"),
    ],
    "EIE": [
        ("Industrial Instrumentation", "K. Krishnaswamy"),
        ("Measurement Systems", "Ernest O. Doebelin"),
        ("Process Control Instrumentation", "Curtis D. Johnson"),
        ("Sensors and Transducers", "D. Patranabis"),
        ("Biomedical Instrumentation", "R. S. Khandpur"),
        ("Analytical Instrumentation", "R. S. Khandpur"),
        ("Digital Control Systems", "Benjamin C. Kuo"),
        ("Modern Control Engineering", "Katsuhiko Ogata"),
        ("Industrial Automation", "Terry L. M. Bartelt"),
        ("Programmable Logic Controllers", "Frank D. Petruzella"),
        ("Virtual Instrumentation Using LabVIEW", "Sanjay Gupta"),
        ("Robotics and Control", "R. K. Mittal"),
        ("Instrumentation Devices and Systems", "C. S. Rangan"),
    ],
    "Mechanical": [
        ("Engineering Thermodynamics", "P. K. Nag"),
        ("Fluid Mechanics", "R. K. Bansal"),
        ("Theory of Machines", "R. S. Khurmi"),
        ("Machine Design", "V. B. Bhandari"),
        ("Heat and Mass Transfer", "R. K. Rajput"),
        ("Manufacturing Technology", "P. N. Rao"),
        ("Strength of Materials", "R. K. Rajput"),
        ("Internal Combustion Engines", "V. Ganesan"),
        ("Refrigeration and Air Conditioning", "C. P. Arora"),
        ("Automobile Engineering", "Kirpal Singh"),
        ("CAD/CAM Principles and Applications", "P. N. Rao"),
        ("Mechatronics", "W. Bolton"),
        ("Engineering Metrology", "R. K. Jain"),
    ],
    "Civil": [
        ("Building Materials", "S. K. Duggal"),
        ("Surveying", "B. C. Punmia"),
        ("Soil Mechanics and Foundations", "B. C. Punmia"),
        ("Reinforced Concrete Structures", "B. C. Punmia"),
        ("Structural Analysis", "R. C. Hibbeler"),
        ("Environmental Engineering", "S. K. Garg"),
        ("Transportation Engineering", "C. Venkatramaiah"),
        ("Hydrology and Water Resources", "K. Subramanya"),
        ("Construction Planning and Management", "P. S. Gahlot"),
        ("Steel Structures", "S. K. Duggal"),
        ("Engineering Geology", "N. Chennakesavulu"),
        ("Estimation and Costing", "B. N. Dutta"),
        ("Concrete Technology", "M. S. Shetty"),
    ],
    "AI & DS": [
        ("Artificial Intelligence: A Modern Approach", "Stuart Russell"),
        ("Hands-On Machine Learning", "Aurélien Géron"),
        ("Deep Learning", "Ian Goodfellow"),
        ("Pattern Recognition and Machine Learning", "Christopher M. Bishop"),
        ("Data Science from Scratch", "Joel Grus"),
        ("Python for Data Analysis", "Wes McKinney"),
        ("The Elements of Statistical Learning", "Trevor Hastie"),
        ("Natural Language Processing with Python", "Steven Bird"),
        ("Computer Vision: Algorithms and Applications", "Richard Szeliski"),
        ("Reinforcement Learning", "Richard S. Sutton"),
        ("Mining of Massive Datasets", "Jure Leskovec"),
        ("Practical Statistics for Data Scientists", "Peter Bruce"),
        ("Data Mining Concepts and Techniques", "Jiawei Han"),
    ],
    "IT": [
        ("Information Technology Essentials", "Eric Frick"),
        ("Java: The Complete Reference", "Herbert Schildt"),
        ("Computer Fundamentals", "P. K. Sinha"),
        ("Linux Administration", "Wale Soyinka"),
        ("Information Security", "Mark Stamp"),
        ("Human Computer Interaction", "Alan Dix"),
        ("E-Commerce", "Kenneth C. Laudon"),
        ("Management Information Systems", "Kenneth C. Laudon"),
        ("Internet of Things", "Arshdeep Bahga"),
        ("Mobile Computing", "Jochen Schiller"),
        ("Distributed Systems", "George Coulouris"),
        ("Software Testing", "Ron Patton"),
        ("DevOps Handbook", "Gene Kim"),
    ],
}

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT DEFAULT '',
        is_department INTEGER NOT NULL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        isbn TEXT UNIQUE,
        description TEXT DEFAULT '',
        cover_url TEXT DEFAULT '',
        total_copies INTEGER NOT NULL DEFAULT 1,
        available_copies INTEGER NOT NULL DEFAULT 1,
        subject_id INTEGER,
        created_at TEXT NOT NULL,
        FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        reserved_at TEXT NOT NULL,
        pickup_deadline TEXT NOT NULL,
        borrowed_at TEXT,
        return_due_at TEXT,
        returned_at TEXT,
        status TEXT NOT NULL DEFAULT 'Reserved',
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE CASCADE
    );
    """)

    subject_columns = {row["name"] for row in conn.execute("PRAGMA table_info(subjects)").fetchall()}
    if "is_department" not in subject_columns:
        conn.execute("ALTER TABLE subjects ADD COLUMN is_department INTEGER NOT NULL DEFAULT 0")

    reservation_columns = {
        row["name"] for row in conn.execute("PRAGMA table_info(reservations)").fetchall()
    }
    for column_name in ("borrowed_at", "return_due_at", "returned_at"):
        if column_name not in reservation_columns:
            conn.execute(f"ALTER TABLE reservations ADD COLUMN {column_name} TEXT")

    for name, desc in COLLEGE_DEPARTMENTS:
        conn.execute(
            "INSERT OR IGNORE INTO subjects(name, description, is_department) VALUES (?, ?, 1)",
            (name, desc)
        )
        conn.execute("UPDATE subjects SET is_department=1 WHERE name=?", (name,))

    admin = conn.execute("SELECT id FROM users WHERE email=?", ("admin@booknest.com",)).fetchone()
    if not admin:
        conn.execute(
            "INSERT INTO users(name,email,password,role,created_at) VALUES(?,?,?,?,?)",
            ("BookNest Admin", "admin@booknest.com", generate_password_hash("admin123"), "admin",
             datetime.now().isoformat(timespec="seconds"))
        )

    for department_number, (department, books) in enumerate(DEPARTMENT_BOOKS.items(), start=1):
        department_id = conn.execute(
            "SELECT id FROM subjects WHERE name=?", (department,)
        ).fetchone()["id"]
        for book_number, (title, author) in enumerate(books, start=1):
            isbn = f"9788{department_number:02d}{book_number:07d}"
            copies = 3 + ((department_number + book_number) % 5)
            conn.execute("""INSERT OR IGNORE INTO books
                (title,author,isbn,description,cover_url,total_copies,available_copies,subject_id,created_at)
                VALUES(?,?,?,?,?,?,?,?,?)""",
                (title, author, isbn, f"A core {department} library reference for college students.",
                 "", copies, copies, department_id, datetime.now().isoformat(timespec="seconds")))

    conn.commit()
    conn.close()

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Administrator access required.", "danger")
            return redirect(url_for("index"))
        return fn(*args, **kwargs)
    return wrapper

@app.context_processor
def inject_globals():
    return {"year": datetime.now().year}

def reservation_view_rows(rows):
    """Add display-only status and due-date warning fields to reservation rows."""
    today = datetime.now().date()
    view_rows = []
    for row in rows:
        item = dict(row)
        due_at = None
        if item.get("return_due_at"):
            try:
                due_at = datetime.fromisoformat(item["return_due_at"])
            except ValueError:
                due_at = None

        loan_active = item["status"] in ("Borrowed", "Overdue")
        due_date = due_at.date() if due_at else None
        item["is_due_today"] = bool(loan_active and due_date == today)
        item["is_overdue"] = bool(
            loan_active and (item["status"] == "Overdue" or (due_date and due_date < today))
        )
        item["show_due_warning"] = item["is_due_today"] or item["is_overdue"]

        if item["is_overdue"]:
            overdue_days = max(1, (today - due_date).days) if due_date else 1
            item["display_status"] = "Overdue"
            item["status_class"] = "danger"
            item["warning_text"] = f"Return overdue by {overdue_days} day(s)"
        elif item["is_due_today"]:
            item["display_status"] = "Due today"
            item["status_class"] = "warning"
            item["warning_text"] = "This book must be returned today"
        elif item["status"] == "Borrowed":
            item["display_status"] = "Picked up"
            item["status_class"] = "primary"
            item["warning_text"] = ""
        else:
            item["display_status"] = item["status"]
            item["status_class"] = {
                "Reserved": "info", "Returned": "success", "Cancelled": "secondary"
            }.get(item["status"], "secondary")
            item["warning_text"] = ""

        item["deadline_at"] = item.get("return_due_at") or item.get("pickup_deadline")
        item["deadline_label"] = "Return due" if item.get("return_due_at") else "Pickup deadline"
        view_rows.append(item)
    return view_rows

@app.route("/")
def index():
    conn = get_db()
    q = request.args.get("q", "").strip()
    department_id = request.args.get("department", "").strip()
    sort = request.args.get("sort", "department").strip()
    departments = conn.execute(
        "SELECT * FROM subjects WHERE is_department=1 ORDER BY name COLLATE NOCASE"
    ).fetchall()
    department_names = [department["name"] for department in departments]
    sql = """SELECT b.*, s.name AS subject_name FROM books b
             LEFT JOIN subjects s ON s.id=b.subject_id WHERE 1=1"""
    params = []
    if q:
        sql += " AND (b.title LIKE ? OR b.author LIKE ? OR b.isbn LIKE ?)"
        like = f"%{q}%"
        params += [like, like, like]
    main_department_ids = {str(department["id"]) for department in departments}
    if department_id in main_department_ids:
        sql += " AND b.subject_id=?"
        params.append(int(department_id))
    if sort not in ("author_asc", "author_desc", "department", "title"):
        sort = "department"
    books = conn.execute(sql, params).fetchall()

    department_name_set = set(department_names)
    is_other = lambda book: (
        book["subject_name"] not in department_name_set
        or not (book["author"] or "").strip()
    )
    main_books = [book for book in books if not is_other(book)]
    other_books = [book for book in books if is_other(book)]

    if sort == "department":
        section_label = "Department"
        section_key = lambda book: book["subject_name"] or "General Library"
        main_books.sort(key=lambda book: (
            book["subject_name"].casefold(), book["author"].casefold(), book["title"].casefold()
        ))
    elif sort in ("author_asc", "author_desc"):
        section_label = "Author"
        section_key = lambda book: book["author"]
        main_books.sort(key=lambda book: book["title"].casefold())
        main_books.sort(key=lambda book: book["author"].casefold(), reverse=sort == "author_desc")
    else:
        section_label = "Title"
        section_key = lambda book: (book["title"][:1] or "#").upper()
        main_books.sort(key=lambda book: book["title"].casefold())

    other_books.sort(key=lambda book: book["title"].casefold())
    books = main_books + other_books

    book_sections = []
    for book in main_books:
        heading = section_key(book)
        if not book_sections or book_sections[-1]["heading"] != heading:
            book_sections.append({"heading": heading, "label": section_label, "books": []})
        book_sections[-1]["books"].append(book)
    if other_books:
        book_sections.append({"heading": "Others", "label": "Collection", "books": other_books})

    stats = {
        "books": conn.execute("SELECT COUNT(*) c FROM books").fetchone()["c"],
        "departments": len(departments),
        "available": conn.execute("SELECT COALESCE(SUM(available_copies),0) c FROM books").fetchone()["c"],
        "reservations": conn.execute(
            "SELECT COUNT(*) c FROM reservations WHERE status='Reserved'"
        ).fetchone()["c"]
    }
    conn.close()
    return render_template(
        "index.html", books=books, book_sections=book_sections,
        departments=departments, stats=stats, q=q,
        selected_department=department_id, selected_sort=sort
    )

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        if len(password) < 6:
            flash("Password must contain at least 6 characters.", "danger")
            return redirect(url_for("register"))
        conn = get_db()
        try:
            conn.execute("INSERT INTO users(name,email,password,created_at) VALUES(?,?,?,?)",
                         (name,email,generate_password_hash(password),datetime.now().isoformat(timespec="seconds")))
            conn.commit()
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("An account with that email already exists.", "danger")
        finally:
            conn.close()
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password"], password):
            session.update(user_id=user["id"], name=user["name"], role=user["role"])
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("admin_dashboard" if user["role"] == "admin" else "index"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

@app.route("/book/<int:book_id>")
def book_detail(book_id):
    conn = get_db()
    book = conn.execute("""SELECT b.*, s.name subject_name, s.description subject_description
                           FROM books b LEFT JOIN subjects s ON s.id=b.subject_id WHERE b.id=?""", (book_id,)).fetchone()
    conn.close()
    if not book:
        return "Book not found", 404
    return render_template("book_detail.html", book=book)

@app.route("/reserve/<int:book_id>", methods=["POST"])
@login_required
def reserve(book_id):
    conn = get_db()
    book = conn.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
    if not book:
        conn.close(); flash("Book not found.", "danger"); return redirect(url_for("index"))
    existing = conn.execute("""SELECT id FROM reservations
                               WHERE user_id=? AND book_id=?
                                 AND status IN ('Reserved','Borrowed','Overdue')""",
                            (session["user_id"], book_id)).fetchone()
    if existing:
        conn.close(); flash("You already have an active reservation for this book.", "warning")
        return redirect(url_for("book_detail", book_id=book_id))
    if book["available_copies"] < 1:
        conn.close(); flash("This book is currently unavailable.", "warning")
        return redirect(url_for("book_detail", book_id=book_id))
    now = datetime.now()
    deadline = now + timedelta(days=3)
    conn.execute("""INSERT INTO reservations(user_id,book_id,reserved_at,pickup_deadline,status)
                    VALUES(?,?,?,?,?)""",
                 (session["user_id"], book_id, now.isoformat(timespec="seconds"),
                  deadline.isoformat(timespec="seconds"), "Reserved"))
    conn.execute("UPDATE books SET available_copies=available_copies-1 WHERE id=?", (book_id,))
    conn.commit(); conn.close()
    flash("Book reserved successfully. Pickup deadline is 3 days.", "success")
    return redirect(url_for("my_reservations"))

@app.route("/reservations")
@login_required
def my_reservations():
    conn = get_db()
    rows = conn.execute("""SELECT r.*, b.title, b.author, b.cover_url
                           FROM reservations r JOIN books b ON b.id=r.book_id
                           WHERE r.user_id=? ORDER BY r.reserved_at DESC""",
                        (session["user_id"],)).fetchall()
    conn.close()
    return render_template("reservations.html", reservations=reservation_view_rows(rows))

@app.route("/cancel/<int:reservation_id>", methods=["POST"])
@login_required
def cancel_reservation(reservation_id):
    conn = get_db()
    r = conn.execute("SELECT * FROM reservations WHERE id=? AND user_id=?", (reservation_id, session["user_id"])).fetchone()
    if r and r["status"] == "Reserved":
        conn.execute("UPDATE reservations SET status='Cancelled' WHERE id=?", (reservation_id,))
        conn.execute("UPDATE books SET available_copies=available_copies+1 WHERE id=?", (r["book_id"],))
        conn.commit()
        flash("Reservation cancelled and the copy was released.", "success")
    conn.close()
    return redirect(url_for("my_reservations"))

@app.route("/admin")
@admin_required
def admin_dashboard():
    conn = get_db()
    departments = conn.execute(
        "SELECT * FROM subjects WHERE is_department=1 ORDER BY name COLLATE NOCASE"
    ).fetchall()
    department_ids = {str(department["id"]) for department in departments}
    inventory_q = request.args.get("inventory_q", "").strip()
    inventory_department = request.args.get("inventory_department", "").strip()
    inventory_sort = request.args.get("inventory_sort", "department").strip()

    stats = {
        "books": conn.execute("SELECT COUNT(*) c FROM books").fetchone()["c"],
        "users": conn.execute("SELECT COUNT(*) c FROM users WHERE role='user'").fetchone()["c"],
        "reservations": conn.execute("SELECT COUNT(*) c FROM reservations").fetchone()["c"],
        "active": conn.execute(
            "SELECT COUNT(*) c FROM reservations WHERE status IN ('Reserved','Borrowed','Overdue')"
        ).fetchone()["c"],
    }
    reservation_rows = conn.execute("""SELECT r.*, u.name user_name, u.email, b.title, b.author
                                       FROM reservations r JOIN users u ON u.id=r.user_id
                                       JOIN books b ON b.id=r.book_id
                                       WHERE r.status IN ('Reserved','Borrowed','Overdue')
                                       ORDER BY CASE
                                           WHEN r.status IN ('Borrowed','Overdue')
                                           THEN COALESCE(r.return_due_at,r.pickup_deadline)
                                           ELSE r.pickup_deadline END,
                                           r.reserved_at""").fetchall()
    reservations = reservation_view_rows(reservation_rows)

    inventory_sql = """SELECT b.*, s.name subject_name, COALESCE(s.is_department,0) is_department,
                       EXISTS(SELECT 1 FROM reservations due
                              WHERE due.book_id=b.id
                                AND due.status IN ('Borrowed','Overdue')
                                AND due.return_due_at IS NOT NULL
                                AND date(due.return_due_at) <= date('now','localtime')) has_due_warning
                       FROM books b LEFT JOIN subjects s ON s.id=b.subject_id WHERE 1=1"""
    inventory_params = []
    if inventory_q:
        like = f"%{inventory_q}%"
        inventory_sql += " AND (b.title LIKE ? OR b.author LIKE ? OR b.isbn LIKE ?)"
        inventory_params.extend([like, like, like])
    if inventory_department in department_ids:
        inventory_sql += " AND b.subject_id=?"
        inventory_params.append(int(inventory_department))
    elif inventory_department == "others":
        inventory_sql += " AND (COALESCE(s.is_department,0)=0 OR TRIM(COALESCE(b.author,''))='')"

    inventory_sort_options = {
        "department": "CASE WHEN COALESCE(s.is_department,0)=1 AND TRIM(COALESCE(b.author,''))<>'' THEN 0 ELSE 1 END, s.name COLLATE NOCASE, b.author COLLATE NOCASE, b.title COLLATE NOCASE",
        "title": "b.title COLLATE NOCASE",
        "author": "CASE WHEN TRIM(COALESCE(b.author,''))='' THEN 1 ELSE 0 END, b.author COLLATE NOCASE, b.title COLLATE NOCASE",
        "availability": "b.available_copies ASC, b.title COLLATE NOCASE",
        "newest": "b.id DESC",
    }
    if inventory_sort not in inventory_sort_options:
        inventory_sort = "department"
    inventory_sql += f" ORDER BY {inventory_sort_options[inventory_sort]}"
    books = conn.execute(inventory_sql, inventory_params).fetchall()
    total_inventory = conn.execute("SELECT COUNT(*) c FROM books").fetchone()["c"]
    conn.close()
    return render_template(
        "admin.html", stats=stats, reservations=reservations, books=books,
        subjects=departments, total_inventory=total_inventory,
        inventory_q=inventory_q, inventory_department=inventory_department,
        inventory_sort=inventory_sort
    )

@app.route("/admin/book/add", methods=["POST"])
@admin_required
def add_book():
    data = request.form
    conn = get_db()
    try:
        copies = max(1, int(data["copies"]))
        subject_id = int(data["subject_id"])
        valid_department = conn.execute(
            "SELECT id FROM subjects WHERE id=? AND is_department=1",
            (subject_id,)
        ).fetchone()
        if not valid_department:
            raise ValueError("Invalid main department")
        conn.execute("""INSERT INTO books(title,author,isbn,description,cover_url,total_copies,available_copies,subject_id,created_at)
                        VALUES(?,?,?,?,?,?,?,?,?)""",
                     (data["title"].strip(), data["author"].strip(), data.get("isbn","").strip() or None,
                      data.get("description","").strip(), data.get("cover_url","").strip(),
                      copies, copies, subject_id, datetime.now().isoformat(timespec="seconds")))
        conn.commit(); flash("Book added successfully.", "success")
    except (ValueError, sqlite3.IntegrityError):
        flash("Could not add book. Check the ISBN and form values.", "danger")
    finally: conn.close()
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/book/edit/<int:book_id>", methods=["GET", "POST"])
@admin_required
def edit_book(book_id):
    conn = get_db()
    if request.method == "POST":
        # Lock the inventory row against concurrent reservations while its
        # availability is recalculated from the new total.
        conn.execute("BEGIN IMMEDIATE")
    book = conn.execute(
        """SELECT b.*, s.name subject_name, COALESCE(s.is_department,0) is_department
           FROM books b LEFT JOIN subjects s ON s.id=b.subject_id
           WHERE b.id=?""",
        (book_id,)
    ).fetchone()
    if not book:
        conn.close()
        flash("Book not found.", "warning")
        return redirect(url_for("admin_dashboard"))

    departments = conn.execute(
        "SELECT * FROM subjects WHERE is_department=1 ORDER BY name COLLATE NOCASE"
    ).fetchall()
    active_reservations = conn.execute(
        """SELECT COUNT(*) c FROM reservations
           WHERE book_id=? AND status IN ('Reserved','Borrowed','Overdue')""",
        (book_id,)
    ).fetchone()["c"]
    unavailable_copies = max(
        0, book["total_copies"] - book["available_copies"], active_reservations
    )
    current_inactive_subject = book if book["subject_id"] and not book["is_department"] else None
    inventory_state = {
        "inventory_q": request.values.get("inventory_q", "").strip(),
        "inventory_department": request.values.get("inventory_department", "").strip(),
        "inventory_sort": request.values.get("inventory_sort", "department").strip(),
    }
    admin_return_url = url_for("admin_dashboard", **inventory_state)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        isbn = request.form.get("isbn", "").strip() or None
        description = request.form.get("description", "").strip()
        cover_url = request.form.get("cover_url", "").strip()
        subject_value = request.form.get("subject_id", "").strip()
        form_book = dict(book)
        form_book.update(
            title=title,
            author=author,
            isbn=isbn or "",
            description=description,
            cover_url=cover_url,
            subject_id=subject_value,
        )

        error = None
        try:
            total_copies = int(request.form.get("copies", ""))
            form_book["total_copies"] = total_copies
        except (TypeError, ValueError):
            total_copies = None
            form_book["total_copies"] = request.form.get("copies", "")
            error = "Copies must be a whole number."

        if not title:
            error = "Book title is required."
        elif total_copies is not None and total_copies < max(1, unavailable_copies):
            error = (
                f"Total copies cannot be below {max(1, unavailable_copies)} "
                f"while {unavailable_copies} copy/copies are unavailable."
            )

        subject_id = None
        if not error and subject_value:
            try:
                subject_id = int(subject_value)
            except ValueError:
                error = "Select a valid department."
            else:
                selected_subject = conn.execute(
                    "SELECT id, is_department FROM subjects WHERE id=?",
                    (subject_id,)
                ).fetchone()
                if not selected_subject or (
                    not selected_subject["is_department"] and subject_id != book["subject_id"]
                ):
                    error = "Select a valid department."

        if not error and isbn:
            duplicate = conn.execute(
                "SELECT id FROM books WHERE isbn=? AND id<>?",
                (isbn, book_id)
            ).fetchone()
            if duplicate:
                error = "Another book already uses that ISBN."

        if error:
            conn.close()
            flash(error, "danger")
            return render_template(
                "edit_book.html", book=form_book, departments=departments,
                unavailable_copies=unavailable_copies,
                current_inactive_subject=current_inactive_subject,
                admin_return_url=admin_return_url, inventory_state=inventory_state
            ), 400

        available_copies = total_copies - unavailable_copies
        try:
            conn.execute(
                """UPDATE books
                   SET title=?, author=?, isbn=?, description=?, cover_url=?,
                       total_copies=?, available_copies=?, subject_id=?
                   WHERE id=?""",
                (title, author, isbn, description, cover_url, total_copies,
                 available_copies, subject_id, book_id)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            flash("Could not update the book. Check the ISBN and form values.", "danger")
            return render_template(
                "edit_book.html", book=form_book, departments=departments,
                unavailable_copies=unavailable_copies,
                current_inactive_subject=current_inactive_subject,
                admin_return_url=admin_return_url, inventory_state=inventory_state
            ), 400

        conn.close()
        flash(f"{title} updated successfully.", "success")
        return redirect(admin_return_url)

    conn.close()
    return render_template(
        "edit_book.html", book=book, departments=departments,
        unavailable_copies=unavailable_copies,
        current_inactive_subject=current_inactive_subject,
        admin_return_url=admin_return_url, inventory_state=inventory_state
    )

@app.route("/admin/book/delete/<int:book_id>", methods=["POST"])
@admin_required
def delete_book(book_id):
    conn = get_db()
    active = conn.execute(
        """SELECT COUNT(*) c FROM reservations
           WHERE book_id=? AND status IN ('Reserved','Borrowed','Overdue')""",
        (book_id,)
    ).fetchone()["c"]
    if active:
        flash("Cannot delete a book with an active reservation.", "warning")
    else:
        conn.execute("DELETE FROM books WHERE id=?", (book_id,))
        conn.commit(); flash("Book deleted.", "success")
    conn.close()
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/subject/add", methods=["POST"])
@admin_required
def add_subject():
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    if not name:
        flash("Department name is required.", "danger")
        return redirect(url_for("admin_dashboard"))
    conn = get_db()
    existing = conn.execute("SELECT id, is_department FROM subjects WHERE name=?", (name,)).fetchone()
    if existing and existing["is_department"]:
        flash("That department already exists.", "warning")
    elif existing:
        conn.execute(
            "UPDATE subjects SET is_department=1, description=? WHERE id=?",
            (description, existing["id"])
        )
        conn.commit()
        flash("Existing category promoted to a department.", "success")
    else:
        conn.execute(
            "INSERT INTO subjects(name,description,is_department) VALUES(?,?,1)",
            (name, description)
        )
        conn.commit()
        flash("Department added successfully.", "success")
    conn.close()
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/subject/delete/<int:subject_id>", methods=["POST"])
@admin_required
def delete_subject(subject_id):
    conn = get_db()
    department = conn.execute(
        "SELECT id, name FROM subjects WHERE id=? AND is_department=1",
        (subject_id,)
    ).fetchone()
    if not department:
        flash("Department not found.", "warning")
    else:
        book_count = conn.execute(
            "SELECT COUNT(*) c FROM books WHERE subject_id=?", (subject_id,)
        ).fetchone()["c"]
        conn.execute("UPDATE subjects SET is_department=0 WHERE id=?", (subject_id,))
        conn.commit()
        if book_count:
            flash(
                f"{department['name']} removed from departments. "
                f"Its {book_count} book(s) now appear under Others.",
                "success"
            )
        else:
            flash(f"{department['name']} removed from departments.", "success")
    conn.close()
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/reservation/<int:reservation_id>/pickup", methods=["POST"])
@admin_required
def pickup_reservation(reservation_id):
    conn = get_db()
    conn.execute("BEGIN IMMEDIATE")
    reservation = conn.execute(
        "SELECT * FROM reservations WHERE id=?", (reservation_id,)
    ).fetchone()
    if not reservation:
        flash("Reservation not found.", "warning")
    elif reservation["status"] != "Reserved":
        flash("Only a reserved book can be marked as picked up.", "warning")
    else:
        picked_up_at = datetime.now()
        return_due_at = picked_up_at + timedelta(days=7)
        conn.execute(
            """UPDATE reservations
               SET status='Borrowed', borrowed_at=?, return_due_at=?
               WHERE id=? AND status='Reserved'""",
            (picked_up_at.isoformat(timespec="seconds"),
             return_due_at.isoformat(timespec="seconds"), reservation_id)
        )
        conn.commit()
        flash(
            f"Book marked as picked up. Return due {return_due_at.strftime('%d %b %Y at %I:%M %p')}.",
            "success"
        )
    conn.close()
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/reservation/<int:reservation_id>/complete", methods=["POST"])
@admin_required
def complete_reservation(reservation_id):
    conn = get_db()
    conn.execute("BEGIN IMMEDIATE")
    r = conn.execute("SELECT * FROM reservations WHERE id=?", (reservation_id,)).fetchone()
    if not r:
        flash("Reservation not found.", "warning")
    elif r["status"] in ("Borrowed", "Overdue"):
        conn.execute(
            "UPDATE reservations SET status='Returned', returned_at=? WHERE id=?",
            (datetime.now().isoformat(timespec="seconds"), reservation_id)
        )
        conn.execute(
            """UPDATE books
               SET available_copies=MIN(available_copies+1,total_copies)
               WHERE id=?""",
            (r["book_id"],)
        )
        conn.commit()
        flash("Book marked returned and copy restored to inventory.", "success")
    elif r["status"] == "Reserved":
        flash("Mark the book as picked up before marking it returned.", "warning")
    else:
        flash("This reservation is already closed.", "warning")
    conn.close()
    return redirect(url_for("admin_dashboard"))
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
