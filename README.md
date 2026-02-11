# 📊 STEMora Student Dashboard API

A Flask + Pandas API with a built-in dashboard for exploring student progress in Physics and Math.

---

## 🚀 What this API does

This API lets you:
- authenticate requests with an API key
- view student data in JSON
- filter students by name/id/grade range
- paginate student records
- get top students and average grade
- download filtered records as CSV
- upload a student CSV file and get parsed JSON
- fetch coffee sample data (with optional type filter)
- open a web dashboard at `/` or `/students-view`

---

## 🔐 Authentication

Most endpoints require an `api_key` query parameter:

`api_key=12345`

> Example: `http://127.0.0.1:5000/api/students?api_key=12345`

Protected endpoints are guarded by `require_api_key` in `app.py`.

---

## 🧠 API functions (by endpoint)

### 1) Health / greeting functions

#### `GET /api/hello`
Returns a basic test response.

**Response example**
```json
{"message": "Hello, world!"}
```

#### `GET /api/greet?name=Sultan`
Returns a personalized greeting using `name` query param.

---

### 2) Student data functions

#### `GET /api/students`
Returns all students or filtered students.

**Supported query params**
- `name` (exact match, case-insensitive)
- `id`
- `min_grade`
- `max_grade`

#### `GET /api/students/top?count=5`
Returns top N students sorted by grade descending.

#### `GET /api/students/average-grade`
Returns class average grade.

#### `GET /api/students/paginated?page=1&limit=5`
Returns paginated student data with metadata:
- `page`, `limit`, `total_students`, `total_pages`
- `has_next`, `has_prev`
- `next_url`, `prev_url`
- `next_page_count`

> Note: this route is currently public (no API key required).

---

### 3) CSV export and upload functions

#### `GET /api/students/download`
Downloads filtered student results as a CSV file.

Uses the same filters as `/api/students`:
- `name`, `id`, `min_grade`, `max_grade`

#### `POST /api/upload-students`
Uploads a CSV file and returns parsed rows as JSON.

**Request type:** `multipart/form-data`
- form field: `file`
- only `.csv` files accepted

---

### 4) Course database functions

#### `GET /api/courses`
Returns course rows from a SQLite database that include:
- `subject`
- `level`
- `topic`
- `definition`
- `equation`
- `question`
- `diagram_title`

**Optional query params**
- `subject` (e.g. `Physics` or `Math`)
- `level` (e.g. `Level 1`, `Level 2`)

---

### 5) Coffee sample data function

#### `GET /api/coffee-data`
Returns all coffee records, or filtered by:
- `coffee_type`

---

### 6) Free physics resource database functions

#### `GET /api/resources`
Returns curated free resources with category/type grouping.

Fields:
- `category` (`Universal`, `Equations`, `Definitions`)
- `title`
- `description`
- `url`

Optional query params:
- `category`
- `search` (matches title/description)

---

## 🖥️ Dashboard routes

- `GET /` → renders `templates/students.html`
- `GET /students-view` → renders `templates/students.html`

The dashboard includes:
- filtering form
- export CSV button
- momentum badges
- interactive learning-loop diagram
- level studies roadmap
- course database viewer (definitions + equations)
- interactive question diagram cards
- free physics resource explorer (universal/equations/definitions)

---

## 📁 Project structure

```text
.
├── app.py
├── requirements.txt
├── data/
│   ├── students.csv
│   └── coffee.csv
└── templates/
    └── students.html
```

---

## ⚙️ Run locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start server:
```bash
python app.py
```

3. Open dashboard:
- `http://127.0.0.1:5000/`
- or `http://127.0.0.1:5000/students-view`

---

## 🧪 Quick curl examples

```bash
curl "http://127.0.0.1:5000/api/hello?api_key=12345"
curl "http://127.0.0.1:5000/api/students?api_key=12345&min_grade=80"
curl "http://127.0.0.1:5000/api/students/top?api_key=12345&count=3"
curl "http://127.0.0.1:5000/api/students/average-grade?api_key=12345"
```
