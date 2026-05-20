from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({
        "status": "success",
        "data": "Hello from server service"
    }), 200

def start_server(port=8080):
    app.run(host='localhost', port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    start_server()