from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import redis
import json
import os
import socket

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'postgres')}@{os.getenv('DB_HOST', 'db')}:{os.getenv('DB_PORT', 5432)}/{os.getenv('DB_NAME', 'cbo_db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

redis_client = redis.StrictRedis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

class Cbo(db.Model):
    __tablename__ = 'cbo'

    code = db.Column(db.String, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)

@app.route('/cbo/<code>', methods=['GET'])
def get_cbo(code):
    cached_data = redis_client.get(code)
    if cached_data:
        return jsonify(json.loads(cached_data))

    cbo = Cbo.query.filter_by(code=code).first()
    if cbo:
        result = {
            "code": cbo.code,
            "title": cbo.title,
            "description": cbo.description,
            "processed_by": socket.gethostname()
        }
        redis_client.setex(code, 3600, json.dumps(result))
        return jsonify(result)
    
    return jsonify({"error": "CBO not found", "processed_by": socket.gethostname()}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
