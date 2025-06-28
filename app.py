from flask import Flask
import time

app = Flask(__name__)
requests_count = 0
start_time = time.time()

@app.route('/')
def hello():
    return 'TrustBit Dev Server'

@app.route('/health')
def health():
    global requests_count
    requests_count += 1
    return {'status': 'healthy'}

@app.route('/metrics')
def metrics():
    global requests_count
    requests_count += 1
    return {'uptime': int(time.time() - start_time), 'requests': requests_count}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
