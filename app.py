from flask import Flask, render_template, request
import mysql.connector
import redis
import os

app = Flask(__name__)

# Redis connection
cache = redis.Redis(
    host=os.environ.get("REDIS_HOST", "redis"),
    port=6379
)

# MySQL connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "mysql"),
        user="root",
        password="password",
        database="appdb"
    )

@app.route("/", methods=["GET", "POST"])
def index():
    message = None

    if request.method == "POST":
        message = request.form["message"]

        # save to mysql
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (text) VALUES (%s)", (message,))
        conn.commit()
        cursor.close()
        conn.close()

        # cache latest message
        cache.set("latest_message", message)

    # get cached message
    cached_message = cache.get("latest_message")

    return render_template(
        "index.html",
        message=cached_message.decode() if cached_message else None
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
