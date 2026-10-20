from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-for-production")
DB_PATH = os.environ.get("DATABASE_PATH", "kazakhstan2050.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS survey_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                region TEXT NOT NULL,
                priority TEXT NOT NULL,
                idea TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

@app.route("/")
def index():
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM survey_responses").fetchone()[0]
        priorities = conn.execute("""
            SELECT priority, COUNT(*) AS count
            FROM survey_responses GROUP BY priority ORDER BY count DESC
        """).fetchall()
    return render_template("index.html", total=total, priorities=priorities)

@app.route("/vote", methods=["POST"])
def vote():
    region = request.form.get("region", "").strip()
    priority = request.form.get("priority", "").strip()
    idea = request.form.get("idea", "").strip()[:500]
    allowed_regions = {"Астана", "Алматы", "Шымкент", "Акмолинская область", "Алматинская область",
                       "Актюбинская область", "Атырауская область", "Восточно-Казахстанская область",
                       "Жамбылская область", "Жетысу", "Западно-Казахстанская область",
                       "Карагандинская область", "Костанайская область", "Кызылординская область",
                       "Мангистауская область", "Павлодарская область", "Северо-Казахстанская область",
                       "Туркестанская область", "Улытау", "Абай"}
    allowed_priorities = {"Экология и чистая энергия", "Технологии и искусственный интеллект",
                          "Образование", "Экономика и новые профессии", "Комфортные города"}
    if region not in allowed_regions or priority not in allowed_priorities:
        flash("Пожалуйста, выберите регион и направление из списка.", "error")
        return redirect(url_for("index") + "#survey")
    with get_db() as conn:
        conn.execute("INSERT INTO survey_responses (region, priority, idea) VALUES (?, ?, ?)",
                     (region, priority, idea))
    flash("Спасибо! Ваш голос добавлен в базу проекта.", "success")
    return redirect(url_for("index") + "#survey")

@app.route("/health")
def health():
    return {"status": "ok"}

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)