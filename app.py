from flask import Flask, request
from google.cloud import secretmanager
import time
from prometheus_client import Counter, Gauge, generate_latest
from functools import wraps

app = Flask(__name__)
requests_count = Counter('trustbit_requests_total', 'Total requests')
uptime_gauge = Gauge('trustbit_uptime_seconds', 'Server uptime')
start_time = time.time()

client = secretmanager.SecretManagerServiceClient()
project_id = 'trustbit-463123' # REMINDER: Replace with your Google Cloud project ID

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == 'admin' and auth.password == 'trustbit123':
            return f(*args, **kwargs)
        return {'error': 'Unauthorized'}, 401
    return decorated

@app.route('/')
def hello():
    requests_count.inc()
    uptime_gauge.set(int(time.time() - start_time))
    return 'TrustBit Dev Server'

@app.route('/health')
def health():
    requests_count.inc()
    uptime_gauge.set(int(time.time() - start_time))
    return {'status': 'healthy'}

@app.route('/metrics')
def metrics():
    requests_count.inc()
    uptime_gauge.set(int(time.time() - start_time))
    return generate_latest(), 200, {'Content-Type': 'text/plain'}

@app.route('/search', methods=['POST'])
def search():
    requests_count.inc()
    uptime_gauge.set(int(time.time() - start_time))
    data = request.get_json()
    query = data.get('query', '')
    return {'results': [f'result1 for {query}', f'result2 for {query}']}

@app.route('/vault')
@require_auth
def vault():
    requests_count.inc()
    uptime_gauge.set(int(time.time() - start_time))
    return {'data': 'secure data'}

@app.route('/truth')
def truth():
    requests_count.inc()
    uptime_gauge.set(int(time.time() - start_time))
    xai_key = client.access_secret_version(name=f'projects/{project_id}/secrets/trustbit-xai-key/versions/latest').payload.data.decode('UTF-8')
    return {'truth': f'verified with XAI key: {xai_key[:4]}...'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
