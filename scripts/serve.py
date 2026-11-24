"""
Lightweight local HTTP preview server for index.html.
Starts server at http://localhost:8000 and opens default browser.
"""

import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8000
DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def main():
    print(f"\n🚀 Starting Composio Case Study Server at: http://localhost:{PORT}")
    print(f"📁 Serving directory: {DIRECTORY}")
    print("Press Ctrl+C to stop the server.\n")

    # Try opening browser
    try:
        webbrowser.open(f"http://localhost:{PORT}/index.html")
    except Exception:
        pass

    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == "__main__":
    main()
