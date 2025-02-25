from flask import Flask, jsonify
import psycopg2
import redis
import json
import os
import socket  

app = Flask(__name__)
redis_client = redis.StrictRedis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME", "cbo_db"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "postgres"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", 5432))
)
cur = conn.cursor()

@app.route('/cbo/<code>', methods=['GET'])
def get_cbo(code):
    cached_data = redis_client.get(code)
    if cached_data:
        return jsonify(json.loads(cached_data))

    cur.execute("SELECT code, title, description FROM cbo WHERE code = %s", (code,))
    row = cur.fetchone()
    if row:
        result = {
            "code": row[0],
            "title": row[1],
            "description": row[2],
            "processed_by": socket.gethostname()  
        }
        redis_client.setex(code, 3600, json.dumps(result))
        return jsonify(result)
    
    return jsonify({"error": "CBO not found", "processed_by": socket.gethostname()}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
