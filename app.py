from flask import Flask
import ssl
app = Flask(__name__)
@app.route('/')
def hello():
    return 'TrustBit Dev Server'
if __name__ == '__main__':
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('/home/trustbitdev/certs/selfsigned.crt', '/home/trustbitdev/certs/selfsigned.key')
    app.run(host='0.0.0.0', port=8000, ssl_context=context)
