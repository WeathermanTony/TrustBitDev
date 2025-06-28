from flask import Flask, request
from google.cloud import secretmanager
import time
import requests
from prometheus_client import Counter, Gauge, generate_latest
from functools import wraps

app = Flask(__name__)

requests_count = Counter('trustbit_requests_total', 'Total requests')
uptime_gauge = Gauge('trustbit_uptime_seconds', 'Server uptime')
start_time = time.time()

client = secretmanager.SecretManagerServiceClient()
project_id = 'trustbit-463123'

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == 'admin' and auth.password == 'trustbit123':
            return f(*args, **kwargs)
        return {'error': 'Unauthorized'}, 401
    return decorated

def get_secret(secret_id):
    try:
        response = client.access_secret_version(name=f'projects/{project_id}/secrets/{secret_id}/versions/latest')
        return response.payload.data.decode('UTF-8')
    except Exception as e:
        return f'Error accessing {secret_id}: {str(e)}'

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
    secrets = {
        'xai': get_secret('trustbit-xai-key'),
        'google_ai': get_secret('trustbit-google-ai-key'),
        'openai': get_secret('trustbit-openai-key'),
        'anthropic': get_secret('trustbit-anthropic-key'),
        'mistral': get_secret('trustbit-mistral-key'),
        'newsapi': get_secret('trustbit-newsapi-key'),
        'deepl': get_secret('trustbit-deepl-key'),
        'serpapi': get_secret('trustbit-serpapi-key'),
        'google_factcheck': get_secret('trustbit-google-factcheck-key'),
        'google_gemini': get_secret('trustbit-google-gemini-key'),
        'google_customsearch': get_secret('trustbit-google-customsearch-key'),
        'cohere': get_secret('trustbit-cohere-key'),
        'nytimes': get_secret('trustbit-nytimes-key'),
        'google_cloud': get_secret('trustbit-google-cloud-key'),
        'wikipedia_clientid': get_secret('trustbit-wikipedia-clientid'),
        'wikipedia_secret': get_secret('trustbit-wikipedia-secret'),
        'wikipedia_token': get_secret('trustbit-wikipedia-token')
    }
    return {'truth': {k: v[:4] + '...' if not v.startswith('Error') else v for k, v in secrets.items()}}

@app.route('/query', methods=['POST'])
def query():
    requests_count.inc()
    uptime_gauge.set(int(time.time() - start_time))
    data = request.get_json()
    query = data.get('query', '')

    newsapi_key = get_secret('trustbit-newsapi-key')
    serpapi_key = get_secret('trustbit-serpapi-key')

    news_results = []
    serp_results = []

    try:
        news_response = requests.get(f'https://newsapi.org/v2/everything?q={query}&apiKey={newsapi_key}')
        news_results = [article['title'] for article in news_response.json().get('articles', [])[:2]]
    except Exception as e:
        news_results = [f'NewsAPI error: {str(e)}']

    try:
        serp_response = requests.get(f'https://serpapi.com/search?query={query}&api_key={serpapi_key}')
        serp_results = [result['title'] for result in serp_response.json().get('organic_results', [])[:2]]
    except Exception as e:
        serp_results = [f'SerpApi error: {str(e)}']

    return {'news': news_results, 'serp': serp_results}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)