import requests

def probe(url):
    try:
        r = requests.get(url, timeout=5)
        print('URL:', url, 'STATUS:', r.status_code)
        print(r.text[:200])
    except Exception as e:
        print('URL:', url, 'ERROR:', str(e))

def main():
    base = 'http://127.0.0.1:5000'
    for path in ['/api/ping', '/api/test', '/api/routes', '/']:
        probe(base + path)

if __name__ == '__main__':
    main()
