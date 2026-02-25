import base64
import time
import json
import os
import subprocess
import requests
from flask import Flask, redirect, render_template_string, request, jsonify, Response
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# ==================== KONFIGURÁCIA PRE UŽÍVATEĽA ====================
BASE_PATH = "/Data/Movies_Streams"        # Cesta k vašim médiám
PROXY_IP = "example.com"                  # IP adresa tohto servera
PROXY_PORT = "5000"                        # Port tohto servera (default 5000)
JELLYFIN_URL = "http://example.com"  # URL vášho Jellyfinu
JELLYFIN_API_KEY = "API"      # Dashboard -> API Keys
JELLYFIN_LIBRARY_NAME = "Streams"          # Presný názov knižnice v JF
# =====================================================================

CONFIG_FILE = os.path.join(BASE_PATH, "config.json")
SYNC_SCRIPT = os.path.join(BASE_PATH, "jf_sync.py")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"

link_cache = {}

def refresh_jellyfin_library():
    """Zistí ID knižnice podľa názvu a spustí jej refresh"""
    headers = {"X-MediaBrowser-Token": JELLYFIN_API_KEY}
    try:
        # 1. Získame zoznam knižníc
        views = requests.get(f"{JELLYFIN_URL}/Library/VirtualFolders", headers=headers).json()
        library_id = next((v['ItemId'] for v in views if v['Name'] == JELLYFIN_LIBRARY_NAME), None)
        
        if library_id:
            # 2. Spustíme refresh iba tej konkrétnej knižnice
            requests.post(f"{JELLYFIN_URL}/Library/Series/Updated?api_key={JELLYFIN_API_KEY}") # Pre seriály
            requests.post(f"{JELLYFIN_URL}/Items/{library_id}/Refresh", headers=headers)
            print(f"🚀 Refresh knižnice '{JELLYFIN_LIBRARY_NAME}' (ID: {library_id}) úspešne odoslaný.")
        else:
            print(f"⚠️ Knižnica '{JELLYFIN_LIBRARY_NAME}' sa nenašla. Skúste celkový refresh.")
            requests.post(f"{JELLYFIN_URL}/Library/Refresh?api_key={JELLYFIN_API_KEY}")
    except Exception as e:
        print(f"❌ Chyba pri komunikácii s Jellyfinom: {e}")

def get_m3u8_cached(url):
    current_time = time.time()
    if url in link_cache:
        cached_url, timestamp = link_cache[url]
        if current_time - timestamp < 3600:
            print(f"♻️ Cache hit: {url}")
            return cached_url

    print(f"🔍 Grabujem link: {url}")
    found_links = []
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=USER_AGENT)
            page = context.new_page()
            page.on("request", lambda req: found_links.append(req.url) if ".m3u8" in req.url else None)
            page.goto(url, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(4000)
            page.mouse.click(400, 300)
            page.wait_for_timeout(2000)
            page.mouse.click(400, 300)
            
            for _ in range(10):
                if found_links:
                    master = [l for l in found_links if any(x in l for x in ["master", "index", "playlist"])]
                    final_link = master[-1] if master else found_links[-1]
                    link_cache[url] = (final_link, current_time)
                    browser.close()
                    return final_link
                page.wait_for_timeout(1000)
            browser.close()
        except Exception as e:
            print(f"⚠️ Playwright chyba: {e}")
    return None

@app.route('/play/<b64_url>/video.m3u8')
def play(b64_url):
    try:
        target_url = base64.b64decode(b64_url).decode('utf-8')
        fresh_link = get_m3u8_cached(target_url)
        if not fresh_link: return "Stream error", 404
        resp = redirect(fresh_link)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    except Exception as e:
        return str(e), 500

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Jellyfin Stream Manager</title>
    <style>
        body { font-family: sans-serif; background: #121212; color: #e0e0e0; padding: 20px; }
        .container { max-width: 900px; margin: auto; background: #1e1e1e; padding: 20px; border-radius: 8px; }
        input, button { padding: 12px; margin: 5px; border-radius: 4px; border: 1px solid #444; background: #2a2a2a; color: white; }
        table { width: 100%; border-collapse: collapse; margin-top: 25px; }
        th, td { border: 1px solid #333; padding: 12px; text-align: left; }
        .btn-add { background: #4caf50; cursor: pointer; border: none; }
        .btn-sync { background: #0085ff; cursor: pointer; border: none; }
    </style>
</head>
<body>
    <div class="container">
        <h2>➕ Pridať nový obsah</h2>
        <form action="/add" method="post">
            <input type="text" name="name" placeholder="Názov" required>
            <input type="text" name="url" placeholder="Mrkaj.si URL" required style="width: 350px;">
            <button type="submit" class="btn-add">Pridať a Refreshnúť</button>
        </form>
        <table>
            <tr><th>Názov</th><th>Akcia</th></tr>
            {% for item in items %}
            <tr>
                <td>{{ item.name }}</td>
                <td><button class="btn-sync" onclick="fetch('/sync?mode=one&name={{ item.name }}')">🔄</button></td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    items = []
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            try: items = json.load(f)
            except: items = []
    return render_template_string(HTML_TEMPLATE, items=items)

@app.route('/add', methods=['POST'])
def add_item():
    name, url = request.form.get('name'), request.form.get('url')
    if name and url:
        items = []
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                try: items = json.load(f)
                except: pass
        items.append({"name": name, "web_url": url})
        with open(CONFIG_FILE, 'w') as f:
            json.dump(items, f, indent=4)
        
        # Spustíme synchronizáciu a hneď refresh
        p = subprocess.Popen(['python3', SYNC_SCRIPT, '--name', name])
        p.wait()
        refresh_jellyfin_library()
        
    return redirect('/')

@app.route('/sync')
def sync():
    name = request.args.get('name')
    if name: 
        p = subprocess.Popen(['python3', SYNC_SCRIPT, '--name', name])
        p.wait()
        refresh_jellyfin_library()
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(PROXY_PORT), threaded=True)
