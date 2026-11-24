from index import app, handler

if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    server = make_server("0.0.0.0", 8000, app)
    print("Serving on http://localhost:8000")
    server.serve_forever()
