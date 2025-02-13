from flask import Flask, jsonify
import psycopg2
import redis
import json
import os

app = Flask(__name__)

# Configuração do Redis
redis_client = redis.StrictRedis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

# Configuração do Postgres
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
    # Verifica se o dado está no cache
    cached_data = redis_client.get(code)
    if cached_data:
        return jsonify(json.loads(cached_data))

    # Busca no banco de dados caso não esteja no cache
    cur.execute("SELECT code, title, description FROM cbo WHERE code = %s", (code,))
    row = cur.fetchone()
    if row:
        result = {"code": row[0], "title": row[1], "description": row[2]}
        redis_client.setex(code, 3600, json.dumps(result))  # Cache válido por 1 hora
        return jsonify(result)
    
    return jsonify({"error": "CBO not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
