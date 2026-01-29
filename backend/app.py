from flask import Flask, jsonify
import psycopg2
import redis
import os
from datetime import datetime

app = Flask(__name__)

# Подключение к PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'db'),
        database=os.getenv('DB_NAME', 'myapp'),
        user=os.getenv('DB_USER', 'admin'),
        password=os.getenv('DB_PASSWORD', 'secret123')
    )
    return conn

# Подключение к Redis
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=6379,
    decode_responses=True
)

@app.route('/')
def home():
    return jsonify({
        'message': 'Flask + PostgreSQL + Redis + Nginx',
        'status': 'running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    try:
        # Проверка PostgreSQL
        conn = get_db_connection()
        conn.close()
        db_status = 'OK'
    except Exception as e:
        db_status = f'Error: {str(e)}'
    
    try:
        # Проверка Redis
        redis_client.ping()
        redis_status = 'OK'
    except Exception as e:
        redis_status = f'Error: {str(e)}'
    
    return jsonify({
        'database': db_status,
        'redis': redis_status
    })

@app.route('/counter')
def counter():
    # Увеличиваем счетчик в Redis
    count = redis_client.incr('visit_count')
    return jsonify({
        'visits': count,
        'message': f'This page has been visited {count} times'
    })

@app.route('/users')
def users():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Создать таблицу если не существует
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Добавить тестового пользователя
    cur.execute("INSERT INTO users (name) VALUES ('Test User') RETURNING id, name, created_at")
    user = cur.fetchone()
    
    conn.commit()
    
    # Получить всех пользователей
    cur.execute("SELECT * FROM users ORDER BY id DESC LIMIT 10")
    users = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return jsonify({
        'total_users': len(users),
        'latest_user': {
            'id': user[0],
            'name': user[1],
            'created_at': user[2].isoformat()
        },
        'recent_users': [
            {'id': u[0], 'name': u[1], 'created_at': u[2].isoformat()} 
            for u in users
        ]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
