"""
Task Controller - Lightweight Local HTTP Server & API Endpoints
Serves the web dashboard and handles REST API requests.
"""

import json
import os
import sys
import webbrowser
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

# Resolve paths
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WEB_DIR = os.path.join(BASE_DIR, "web")
sys.path.insert(0, os.path.join(BASE_DIR, "core"))
import task_manager

DEFAULT_PORT = 18500


class TaskControllerRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def log_message(self, format, *args):
        """Suppress noisy request logs."""
        pass

    def send_json(self, data: dict or list, status=HTTPStatus.OK):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/tasks":
            try:
                tasks = task_manager.get_user_scheduled_tasks()
                self.send_json({"success": True, "tasks": tasks})
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if path == "/api/processes":
            try:
                procs = task_manager.get_running_batch_processes()
                self.send_json({"success": True, "processes": procs})
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if path == "/" or path == "/index.html":
            self.path = "/index.html"
            return super().do_GET()

        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            body = json.loads(post_data.decode("utf-8"))
        except Exception:
            body = {}

        if path == "/api/task/toggle":
            task_name = body.get("taskName", "")
            enable = bool(body.get("enable", True))
            result = task_manager.toggle_scheduled_task(task_name, enable)
            self.send_json(result)
            return

        if path == "/api/task/run":
            task_name = body.get("taskName", "")
            result = task_manager.run_scheduled_task(task_name)
            self.send_json(result)
            return

        if path == "/api/task/stop":
            task_name = body.get("taskName", "")
            result = task_manager.stop_scheduled_task(task_name)
            self.send_json(result)
            return

        if path == "/api/process/kill":
            pid = int(body.get("pid", 0))
            result = task_manager.kill_batch_process(pid)
            self.send_json(result)
            return

        if path == "/api/task/open-folder":
            file_path = body.get("filePath", "")
            result = task_manager.open_file_folder(file_path)
            self.send_json(result)
            return

        if path == "/api/task/edit":
            file_path = body.get("filePath", "")
            result = task_manager.edit_file_in_notepad(file_path)
            self.send_json(result)
            return

        if path == "/api/task/delete":
            task_name = body.get("taskName", "")
            delete_file = bool(body.get("deleteFile", False))
            file_path = body.get("filePath", "")
            result = task_manager.delete_scheduled_task(task_name, delete_file, file_path)
            self.send_json(result)
            return

        self.send_json({"success": False, "message": "Endpoint not found"}, status=HTTPStatus.NOT_FOUND)


def find_available_port(start_port=DEFAULT_PORT):
    import socket
    port = start_port
    while port < start_port + 50:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
        port += 1
    return start_port


def run_server(open_browser=True):
    port = find_available_port()
    server_address = ("127.0.0.1", port)
    httpd = ThreadingHTTPServer(server_address, TaskControllerRequestHandler)
    url = f"http://127.0.0.1:{port}"
    print("==================================================")
    print("  Task Controller Server Started")
    print(f"  URL: {url}")
    print("  Press Ctrl+C to stop.")
    print("==================================================")

    if open_browser:
        webbrowser.open(url)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()


if __name__ == "__main__":
    open_b = "--no-browser" not in sys.argv
    run_server(open_browser=open_b)
