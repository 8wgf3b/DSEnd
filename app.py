from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route('/api', methods=['GET'])
def api():
    return 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
