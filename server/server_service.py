# server.py
from flask import Flask, jsonify
import random

app = Flask(__name__)

error_mode = False
error_rate = 0.5

@app.route('/api/data', methods=['GET'])
def get_data():
    global error_mode
    if error_mode or random.random() < error_rate:
        return jsonify({"error": "Service unavailable"}), 500
    return jsonify({
        "status": "success",
        "data": "Hello from server service"
    }), 200

def set_error_mode(mode):
    global error_mode
    error_mode = mode

def set_error_rate(rate):
    global error_rate
    error_rate = rate

if __name__ == "__main__":
    app.run(host='localhost', port=8080, debug=False)