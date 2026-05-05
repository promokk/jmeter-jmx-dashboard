#!/usr/bin/env python3

#Lightweight HTTP Service Discovery for targets

import json
import logging
import threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

# Настройка логирования (вывод в stderr)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Хранилище целей: {port: {"targets": [...], "labels": {...}}}
targets = {}
lock = threading.Lock()

class SDHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Получаем IP и hostname сервера, отправившего запрос
            client_ip = self.client_address[0]

            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            action = data.get('action')
            port = str(data.get('port', ''))

            with lock:
                # Уникальный ключ
                key = f"{client_ip}:{port}"
                if action == 'register' and port:
                    hostname = data.get('hostname', client_ip)
                    script = data.get('script', 'unknown')
                    process_name = data.get('process_name', 'unknown')
                    
                    targets[key] = {
                        "targets": [f"{client_ip}:{port}"],
                        "labels": {
                            "hostname": hostname,
                            "script_name": script,
                            "process_name": process_name
                        }
                    }
                    logger.info(f"REGISTER: key={key}, hostname={hostname}, script={script}, process={process_name}")
                elif action == 'unregister' and port:
                    targets.pop(key, None)
                    logger.info(f"UNREGISTER: key={key}")
            self._send(200, {"status": "ok"})
        except Exception as e:
            logger.error(f"POST error: {e}")
            self._send(400, {"error": str(e)})

    def do_GET(self):
        with lock:
            result = list(targets.values())
        logger.info(f"GET: returning {len(result)} active target(s)")
        self._send(200, result)

    def _send(self, code, body):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def log_message(self, format, *args):
        pass  # Тихий режим для production

if __name__ == "__main__":
    port = 8089
    server = ThreadingHTTPServer(('0.0.0.0', port), SDHandler)
    logger.info(f"SD Server started on port {port}")
    server.serve_forever()