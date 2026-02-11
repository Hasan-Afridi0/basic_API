from flask import Flask, jsonify, request, send_file, render_template, Response
import pandas as pd
import os
import sqlite3

# 🔐 API Key
API_KEY = "12345"


from flask import render_template

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
COURSES_DB_PATH = os.path.join(DATA_DIR, 'courses.db')

def load_csv(path, *, name):
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Missing {name} data at {path}. Please ensure the CSV exists."
        )
    return pd.read_csv(path)

# Load CSV
students_path = os.path.join(DATA_DIR, 'students.csv')
students_df = load_csv(students_path, name="students")
students_df.columns = students_df.columns.str.strip().str.lower()

coffee_path = os.path.join(DATA_DIR, 'coffee.csv')
coffee_df = load_csv(coffee_path, name="coffee")
coffee_df.rename(columns={'coffee type': 'coffee_type'}, inplace=True)

def init_courses_database(db_path):
    seed_courses = [
        ("Physics", "Level 1", "Kinematics", "Motion described by displacement, velocity, and acceleration.", "v = u + at", "How does acceleration affect velocity over time?", "Velocity-Time Slope"),
        ("Physics", "Level 2", "Forces", "Net force determines acceleration based on Newton's second law.", "F = ma", "What happens to acceleration if force doubles and mass stays fixed?", "Force-Acceleration Map"),
        ("Physics", "Level 3", "Energy", "Energy is conserved while transforming between forms.", "W = ΔKE", "How can work done change an object's kinetic energy?", "Energy Transfer Cycle"),
        ("Math", "Level 1", "Linear Expressions", "Linear forms model constant-rate change.", "y = mx + b", "How does changing m affect the graph slope?", "Slope Intercept Diagram"),
        ("Math", "Level 2", "Quadratics", "Quadratic functions create parabolic relationships.", "x = (-b ± √(b² - 4ac)) / 2a", "How does the discriminant affect number of roots?", "Quadratic Roots Tree"),
        ("Math", "Level 3", "Trigonometry", "Trigonometric ratios link angles and side lengths.", "sin²θ + cos²θ = 1", "How does cosine change as angle increases from 0° to 90°?", "Unit Circle Progression")
    ]

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                level TEXT NOT NULL,
                topic TEXT NOT NULL,
                definition TEXT NOT NULL,
                equation TEXT NOT NULL,
                question TEXT NOT NULL,
                diagram_title TEXT NOT NULL
            )
            """
        )

        existing_rows = conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
        if existing_rows == 0:
            conn.executemany(
                """
                INSERT INTO courses (subject, level, topic, definition, equation, question, diagram_title)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                seed_courses,
            )

init_courses_database(COURSES_DB_PATH)

def init_resource_database(db_path):
    seed_resources = [
        ("Universal", "HyperPhysics (Georgia State University)", "Concept maps, formulas, and interconnected physics definitions.", "https://hyperphysics.phy-astr.gsu.edu/"),
        ("Universal", "The Physics Hypertextbook", "Free textbook-style explanations with equations and derivations.", "https://physics.info/"),
        ("Universal", "Wolfram Alpha (Physics)", "Computational lookups for constants, equations, and definitions.", "https://www.wolframalpha.com/"),
        ("Universal", "Physics Pro - Notes & Formulas", "Large formula and definition collection in app/web format.", "https://play.google.com/store/apps/details?id=de.eiswuxe.physicpro"),
        ("Universal", "Einstein-Online", "Modern physics and relativity concept dictionary.", "https://www.einstein-online.info/en/"),
        ("Equations", "Physics Formulae", "Easy-to-browse repository of formulas and constants.", "https://www.physicsformulae.com/"),
        ("Equations", "Cambridge Handbook of Physics Formulas (PDF)", "Comprehensive handbook of core formulas for quick revision.", "https://www.scribd.com/document/379748624/Cambridge-Handbook-of-Physics-Formulas"),
        ("Equations", "GeeksforGeeks Physics Formula List", "Topic-wise list of formulas from mechanics to modern physics.", "https://www.geeksforgeeks.org/physics-formulas/"),
        ("Definitions", "SlideShare - Physics Definitions", "Collections of curriculum-style term definitions.", "https://www.slideshare.net/search/slideshow?searchfrom=header&q=physics+definitions"),
        ("Definitions", "Scribd - Physics Formulae and Definitions", "User-uploaded formula and definition study guides.", "https://www.scribd.com/search?query=Physics%20Formulae%20and%20Definitions"),
        ("Definitions", "WJEC Physics Terms, Definitions & Units", "Glossary-focused definitions with units for exam prep.", "https://resource.download.wjec.co.uk.s3.amazonaws.com/vtc/2014-15/14-15_18/pdf/Terms,%20Definitions%20and%20Units.pdf")
    ]

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                url TEXT NOT NULL
            )
            """
        )

        existing_rows = conn.execute("SELECT COUNT(*) FROM resources").fetchone()[0]
        if existing_rows == 0:
            conn.executemany(
                """
                INSERT INTO resources (category, title, description, url)
                VALUES (?, ?, ?, ?)
                """,
                seed_resources,
            )

init_resource_database(COURSES_DB_PATH)

app = Flask(__name__)

# 🔐 API key check 
from functools import wraps

from flask import render_template

@app.route('/')
def index():
    return render_template('students.html')

@app.route('/students-view')
def students_view():
    return render_template('students.html')

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        key = request.args.get('api_key')
        if key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function


# ✅ Hello World route
@app.route('/api/hello', methods=['GET'])
@require_api_key
def hello():
    return jsonify({"message": "Hello, world!"})

# ✅ Greeting by name
@app.route('/api/greet', methods=['GET'])
@require_api_key
def greet():
    name = request.args.get('name', 'Guest')
    return jsonify({"message": f"Hello, {name}!"})

# ✅ Filter students
@app.route('/api/students', methods=['GET'])
@require_api_key
def get_students():
    result = students_df.copy()

    name = request.args.get('name')
    student_id = request.args.get('id')
    min_grade = request.args.get('min_grade', type=int)
    max_grade = request.args.get('max_grade', type=int)

    if name:
        result = result[result['name'].str.lower() == name.lower()]
    if student_id:
        result = result[result['id'] == int(student_id)]
    if min_grade is not None:
        result = result[result['grade'] >= min_grade]
    if max_grade is not None:
        result = result[result['grade'] <= max_grade]

    return jsonify(result.to_dict(orient='records'))

# ✅ Top N students
@app.route('/api/students/top', methods=['GET'])
@require_api_key
def get_top_students():
    count = request.args.get('count', default=5, type=int)
    top_students = students_df.sort_values(by='grade', ascending=False).head(count)
    return jsonify(top_students.to_dict(orient='records'))

# ✅ Average grade
@app.route('/api/students/average-grade', methods=['GET'])
@require_api_key
def get_average_grade():
    average = students_df['grade'].mean()
    return jsonify({"average_grade": round(average, 2)})

# ✅ Export filtered results as CSV
@app.route('/api/students/download', methods=['GET'])
@require_api_key
def download_filtered_students():
    result = students_df.copy()

    name = request.args.get('name')
    student_id = request.args.get('id')
    min_grade = request.args.get('min_grade', type=int)
    max_grade = request.args.get('max_grade', type=int)

    if name:
        result = result[result['name'].str.lower() == name.lower()]
    if student_id:
        result = result[result['id'] == int(student_id)]
    if min_grade is not None:
        result = result[result['grade'] >= min_grade]
    if max_grade is not None:
        result = result[result['grade'] <= max_grade]

    # Convert to CSV string
    csv_data = result.to_csv(index=False)

    # Return as downloadable file
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=filtered_students.csv"}
    )

@app.route('/api/coffee-data', methods=['GET'])
@require_api_key
def get_coffee_data():
    # Get query parameter from URL
    coffee_type = request.args.get('coffee_type')

    if coffee_type:
        # Filter data by coffee_type
        filtered_df = coffee_df[coffee_df['coffee_type'] == coffee_type]
        data = filtered_df.to_dict(orient='records')
    else:
        # No filter, return all data
        data = coffee_df.to_dict(orient='records')

    return jsonify(data)

@app.route('/api/courses', methods=['GET'])
@require_api_key
def get_courses_data():
    subject = request.args.get('subject')
    level = request.args.get('level')

    query = """
        SELECT id, subject, level, topic, definition, equation, question, diagram_title
        FROM courses
        WHERE 1=1
    """
    params = []

    if subject:
        query += " AND subject = ?"
        params.append(subject)
    if level:
        query += " AND level = ?"
        params.append(level)

    query += " ORDER BY subject, level, id"

    with sqlite3.connect(COURSES_DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(query, params).fetchall()

    return jsonify([dict(row) for row in rows])

@app.route('/api/resources', methods=['GET'])
@require_api_key
def get_resource_data():
    category = request.args.get('category')
    search = request.args.get('search')

    query = """
        SELECT id, category, title, description, url
        FROM resources
        WHERE 1=1
    """
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)

    if search:
        query += " AND (title LIKE ? OR description LIKE ?)"
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard])

    query += " ORDER BY category, title"

    with sqlite3.connect(COURSES_DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(query, params).fetchall()

    return jsonify([dict(row) for row in rows])

# Set max upload size (optional)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB max

# 🔽 Upload CSV and return JSON
@app.route('/api/upload-students', methods=['POST'])
@require_api_key
def upload_students():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Only CSV files are allowed'}), 400

    try:
        df = pd.read_csv(file)
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/students/paginated', methods=['GET'])
def get_paginated_students():
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=5, type=int)

    total_students = len(students_df)
    total_pages = (total_students + limit - 1) // limit  # ceiling division

    # Return 404 if page number too high
    if page < 1 or page > total_pages:
        return jsonify({
            "error": "Page number out of range",
            "total_pages": total_pages,
            "total_students": total_students
        }), 404

    start = (page - 1) * limit
    end = start + limit
    paginated_data = students_df.iloc[start:end]

    base_url = request.base_url  # like http://127.0.0.1:5000/api/students/paginated
    has_next = page < total_pages
    has_prev = page > 1

    next_page_count = 0
    if has_next:
        next_start = page * limit
        next_end = next_start + limit
        next_page_count = len(students_df.iloc[next_start:next_end])


    def make_url(p):
        return f"{base_url}?page={p}&limit={limit}"

    return jsonify({
        "page": page,
        "limit": limit,
        "total_students": total_students,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev,
        "next_url": make_url(page + 1) if has_next else None,
        "prev_url": make_url(page - 1) if has_prev else None,
        "data": paginated_data.to_dict(orient='records'),
        "next_page_count": next_page_count
    })
# and paginating student data.
if __name__ == '__main__':
    app.run(debug=True)
# This code is a Flask application that provides a RESTful API for managing student data.
# It includes endpoints for greeting users, filtering students, retrieving top students, calculating average grades,
