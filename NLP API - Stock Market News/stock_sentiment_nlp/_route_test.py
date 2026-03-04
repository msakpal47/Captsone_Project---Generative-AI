from .app import app

def main():
    with app.test_client() as c:
        r = c.get('/api/test')
        print('status', r.status_code)
        try:
            print('json', r.get_json())
        except Exception:
            print('data', r.data[:200])

if __name__ == '__main__':
    main()
