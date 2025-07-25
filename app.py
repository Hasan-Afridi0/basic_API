from flask import Flask, jsonify, request, send_file, render_template, Response
import pandas as pd
import os

# 🔐 API Key
API_KEY = "12345"


from flask import render_template

# Load CSV
students_df = pd.read_csv('./practice/My_Work/students.csv')
students_df.columns = students_df.columns.str.strip().str.lower()
coffee_df = pd.read_csv('./complete-pandas-tutorial/warmup-data/coffee.csv')
coffee_df.rename(columns={'coffee type': 'coffee_type'}, inplace=True)

app = Flask(__name__)

# 🔐 API key check 
from functools import wraps

from flask import render_template

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