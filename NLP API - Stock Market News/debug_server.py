from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'ok'})

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({'message': 'API working'})

@app.route('/api/routes', methods=['GET'])
def routes():
    paths = sorted([str(r) for r in app.url_map.iter_rules()])
    return jsonify({'routes': paths})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)
