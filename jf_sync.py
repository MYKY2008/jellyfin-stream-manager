#### Súbor 2: `jf_sync.py`

```python
import os
import json
import re
import base64
import requests
import sys
import argparse

# ==========================================
# --- KONFIGURÁCIA --- (Uprav pred spustením)
# ==========================================
BASE_PATH = "/Data/Movies_Streams" # Cesta, kam sa budú ukladať .strm súbory
CONFIG_FILE = os.path.join(BASE_PATH, "config.json")

# IP tvojho Proxmoxu/Servera (tá, ktorú vidí Jellyfin)
PROXY_IP = "192.168.0.99" # ZMEŇ NA SVOJU IP ADRESU
PROXY_PORT = "5000"       # ZMEŇ, AK POUŽÍVAŠ INÝ PORT
# ==========================================

def get_proxy_link(target_url):
    b64_url = base64.b64encode(target_url.encode('utf-8')).decode('utf-8')
    return f"http://{PROXY_IP}:{PROXY_PORT}/play/{b64_url}/video.m3u8"

def check_episode_exists(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        if "S01E01" in response.url and "S01E01" not in url:
            return False, response.url
        return True, response.url
    except:
        return False, url

def process_item(item):
    name = item['name']
    url = item['web_url']
    is_serial = bool(re.search(r'S\d+E\d+', url))

    if is_serial:
        print(f"\n--- Synchronizácia seriálu: {name} ---")
        s = 1
        while s < 25:
            e = 1
            found_any = False
            while e < 60:
                current_url = re.sub(r'S\d+E\d+', f'S{s:02d}E{e:02d}', url)
                print(f"Overujem: {name} S{s:02d}E{e:02d}...", end=" ")
                exists, _ = check_episode_exists(current_url)
                
                if not exists:
                    print("Koniec série.")
                    break
                
                season_dir = os.path.join(BASE_PATH, name, f"Season {s:02d}")
                os.makedirs(season_dir, exist_ok=True)
                strm_path = os.path.join(season_dir, f"{name} S{s:02d}E{e:02d}.strm")
                
                with open(strm_path, 'w') as f:
                    f.write(get_proxy_link(current_url))
                
                print("✅")
                found_any = True
                e += 1
            if not found_any: break
            s += 1
    else:
        print(f"\n--- Synchronizácia filmu: {name} ---")
        movie_dir = os.path.join(BASE_PATH, name)
        os.makedirs(movie_dir, exist_ok=True)
        with open(os.path.join(movie_dir, f"{name}.strm"), 'w') as f:
            f.write(get_proxy_link(url))
        print("✅ Hotovo.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', help='Meno konkrétneho filmu na indexáciu')
    args = parser.parse_args()

    if not os.path.exists(CONFIG_FILE):
        print("Chyba: config.json neexistuje.")
        return

    with open(CONFIG_FILE, 'r') as f:
        try:
            items = json.load(f)
        except:
            print("Chyba: config.json je poškodený.")
            return

    if args.name:
        # Hľadáme konkrétny film podľa mena
        target = next((i for i in items if i['name'] == args.name), None)
        if target:
            process_item(target)
        else:
            print(f"Položka '{args.name}' sa v konfigu nenašla.")
    else:
        # Indexujeme všetko
        for item in items:
            process_item(item)

if __name__ == "__main__":
    main()
