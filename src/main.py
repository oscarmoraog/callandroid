import os
import re
import time
import logging
import threading
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

from adb import find_adb, get_available_device, dial, hangup, is_call_active
from phone import normalize_phone, validate_phone


APP_NAME = "CallAndroid"
PORT = 39527

log_path = os.path.join(os.path.expanduser("~"), "callandroid.log")
logging.basicConfig(filename=log_path, level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")

adb_path = ""
in_call = False
current_phone = ""
current_name = ""
current_contact = ""
call_lock = threading.Lock()
call_start_time = 0
dial_done = False

PAGE_IDLE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>CallAndroid</title>
<style>
  body { font-family: sans-serif; text-align: center; padding: 60px 20px; background: #f5f5f5; }
  .card { background: white; border-radius: 12px; padding: 40px; display: inline-block; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
  h2 { color: #333; margin-bottom: 10px; }
  p { color: #666; }
</style></head><body>
<div class="card">
  <h2>CallAndroid</h2>
  <p>Pronto para ligar.</p>
</div></body></html>"""

PAGE_CALLING = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>CallAndroid</title>
<style>
  body { font-family: sans-serif; text-align: center; padding: 60px 20px; background: #f5f5f5; }
  .card { background: white; border-radius: 12px; padding: 40px; display: inline-block; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
  h2 { color: #333; margin-bottom: 5px; }
  .phone { font-size: 24px; font-weight: bold; color: #1a73e8; margin: 15px 0; }
  .contact { color: #666; font-size: 14px; margin-bottom: 10px; }
  .status { color: #888; font-size: 14px; margin-bottom: 20px; }
  a.btn { display: inline-block; background: #d32f2f; color: white; text-decoration: none;
    padding: 12px 30px; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; }
  a.btn:hover { background: #b71c1c; }
</style></head><body>
<div class="card">
  <h2>Chamada em andamento</h2>
  <h2>{name}</h2>
  {contact}
  <div class="phone">{phone}</div>
  <div class="status" id="timer">Timer: {timer}</div>
  <a class="btn" onclick="hangup()">Desligar</a>
</div>
<script>
var startTime = Date.now();
function updateTimer() {{
  var s = Math.floor((Date.now() - startTime) / 1000);
  var m = Math.floor(s / 60);
  s = s % 60;
  document.getElementById('timer').textContent = 'Timer: ' + m + ':' + (s < 10 ? '0' : '') + s;
}}
setInterval(updateTimer, 1000);
function hangup() {{
  fetch('/hangup').then(function() {{ window.close(); }});
}}
function checkStatus() {{
  fetch('/status').then(function(r) {{ return r.text(); }}).then(function(s) {{
    if (s === 'idle') window.close();
  }});
}}
setInterval(checkStatus, 1000);
</script>
</body></html>"""

PAGE_ENDED = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>CallAndroid</title>
<style>
  body { font-family: sans-serif; text-align: center; padding: 60px 20px; background: #f5f5f5; }
  .card { background: white; border-radius: 12px; padding: 40px; display: inline-block; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
  h2 { color: #333; }
  p { color: #888; }
</style></head><body>
<div class="card">
  <h2>Chamada encerrada</h2>
</div></body></html>"""

PAGE_ERROR = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>CallAndroid</title>
<style>
  body { font-family: sans-serif; text-align: center; padding: 60px 20px; background: #f5f5f5; }
  .card { background: white; border-radius: 12px; padding: 40px; display: inline-block; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
  h2 { color: #d32f2f; }
  p { color: #666; }
</style></head><body>
<div class="card">
  <h2>Erro</h2>
  <p>{error}</p>
</div></body></html>"""


class CallHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        logging.debug(format, *args)

    def send_html(self, html, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def do_GET(self):
        global in_call, call_start_time, current_phone, current_name

        if self.path == "/":
            with call_lock:
                if in_call:
                    elapsed = int(time.time() - call_start_time)
                    mins, secs = divmod(elapsed, 60)
                    contact_html = f'<p class="contact">{current_contact}</p>' if current_contact else ""
                    self.send_html(
                        PAGE_CALLING
                        .replace("{name}", current_name)
                        .replace("{contact}", contact_html)
                        .replace("{phone}", current_phone)
                        .replace("{timer}", f"{mins}:{secs:02d}")
                    )
                else:
                    self.send_html(PAGE_IDLE)
            return

        if self.path == "/hangup":
            logging.info("hangup requested via browser")
            try:
                hangup(adb_path)
            except Exception as e:
                logging.error("hangup error: %s", e)
            with call_lock:
                in_call = False
                dial_done = False
            self.send_html(PAGE_ENDED)
            return

        if self.path == "/status":
            with call_lock:
                status = "calling" if in_call else "idle"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(status.encode())
            return

        match = re.match(r"^/call/(.+?)/?$", self.path)
        if not match:
            self.send_html(PAGE_ERROR.replace("{error}", "Pagina nao encontrada"), 404)
            return

        with call_lock:
            if in_call:
                self.send_html(PAGE_ERROR.replace("{error}", "Chamada ja em andamento. Aguarde ou desligue primeiro."))
                return

        raw = urllib.parse.unquote(match.group(1)).strip()
        params = {}
        for m in re.finditer(r"[&?](\w+)=(.+?)(?=[&?]|$)", raw):
            params[m.group(1).lower()] = m.group(2).strip()
        raw = re.sub(r"[&?]\w+=.+?(?=[&?]|$)", "", raw).strip().rstrip("/")
        phone = normalize_phone(raw)
        nome = params.get("nome", "")
        contato = params.get("contato", "")

        if not validate_phone(phone):
            self.send_html(PAGE_ERROR.replace("{error}", f"Telefone invalido: {phone}"), 400)
            return

        logging.info("call requested: %s nome=%s contato=%s", phone, nome, contato)

        with call_lock:
            current_phone = phone
            current_name = nome
            current_contact = contato
            in_call = True
            call_start_time = time.time()
            dial_done = False

        threading.Thread(target=_do_dial, args=(phone,), daemon=True).start()

        contact_html = f'<p class="contact">{contato}</p>' if contato else ""
        self.send_html(
            PAGE_CALLING
            .replace("{name}", nome)
            .replace("{contact}", contact_html)
            .replace("{phone}", phone)
            .replace("{timer}", "0:00")
        )


def _do_dial(phone):
    global in_call, dial_done
    dial_done = False
    try:
        result = dial(adb_path, phone)
        if result.returncode != 0:
            logging.error("dial failed: %s", result.stderr)
            with call_lock:
                in_call = False
        else:
            time.sleep(5)
            with call_lock:
                dial_done = True
    except Exception as e:
        logging.error("dial error: %s", e)
        with call_lock:
            in_call = False


def monitor_call():
    global in_call, dial_done
    while True:
        time.sleep(2)
        with call_lock:
            if in_call and dial_done:
                try:
                    if not is_call_active(adb_path):
                        logging.info("call ended from phone")
                        in_call = False
                        dial_done = False
                except Exception:
                    pass


def main():
    global adb_path
    logging.info("starting %s", APP_NAME)

    try:
        adb_path = find_adb()
    except FileNotFoundError as e:
        print(f"ERRO: {e}")
        return

    try:
        get_available_device(adb_path)
    except (ConnectionError, PermissionError) as e:
        print(f"ERRO: {e}")
        return

    monitor_thread = threading.Thread(target=monitor_call, daemon=True)
    monitor_thread.start()

    server = HTTPServer(("127.0.0.1", PORT), CallHandler)
    logging.info("server started on port %d", PORT)
    print(f"{APP_NAME} rodando em http://localhost:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
