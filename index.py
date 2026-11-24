import os
import mimetypes

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def app(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    if path in ('', '/'):
        file_name = 'index.html'
    else:
        file_name = path.lstrip('/')

    target_file = os.path.join(ROOT_DIR, file_name)
    if not os.path.exists(target_file) or os.path.isdir(target_file):
        target_file = os.path.join(ROOT_DIR, 'index.html')

    mime_type, _ = mimetypes.guess_type(target_file)
    if not mime_type:
        if target_file.endswith('.json'):
            mime_type = 'application/json'
        elif target_file.endswith('.txt'):
            mime_type = 'text/plain'
        else:
            mime_type = 'text/html'

    try:
        with open(target_file, 'rb') as f:
            data = f.read()
        status = '200 OK'
    except Exception as e:
        status = '500 Internal Server Error'
        data = str(e).encode('utf-8')
        mime_type = 'text/plain'

    headers = [
        ('Content-Type', f'{mime_type}; charset=utf-8' if 'text' in mime_type or 'json' in mime_type else mime_type),
        ('Content-Length', str(len(data))),
        ('Access-Control-Allow-Origin', '*')
    ]
    start_response(status, headers)
    return [data]

# Vercel entrypoint aliases
handler = app
