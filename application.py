from flask import Flask, request, Response
import requests

application = app = Flask(__name__)

@app.route('/api', methods=['POST', 'GET'])
def api():
    return 'hmmm'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
