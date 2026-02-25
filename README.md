# Jellyfin Stream Manager

Nástroj na automatickú synchronizáciu a prehrávanie webových streamov (napríklad zo stránok ako *mrkaj.si*) priamo v[Jellyfin](https://jellyfin.org/) mediálnom serveri pomocou `.strm` súborov. 

Skladá sa z dvoch hlavných častí:
1. **Proxy Server a Web UI (`proxy_server.py`)** - Beží na pozadí, poskytuje webové rozhranie na pridávanie obsahu a dynamicky získava aktuálne `.m3u8` streamovacie linky pomocou bezhlavého prehliadača.
2. **Synchronizačný skript (`jf_sync.py`)** - Vytvára štruktúru zložiek pre Jellyfin. Pri seriáloch dokáže automaticky prejsť sezóny a epizódy a overiť ich dostupnosť.

## ⚠️ Dôležité upozornenie pre Smart TV a Smartfóny
Vzhľadom na to, ako fungujú interné webové prehrávače, natívny prehrávač v aplikácii Jellyfin môže mať problém so spracovaním presmerovaného `.m3u8` streamu.
**Pre bezproblémové prehrávanie na Android TV, Google TV alebo v mobilných telefónoch je NUTNÉ v nastaveniach aplikácie Jellyfin prepnúť prehrávač na externý (napr. VLC alebo ExoPlayer).**

## 📋 Požiadavky
- Python 3.8 a novší
-[Jellyfin](https://jellyfin.org/) (prístup k rovnakej sieti)
- Knižnice: `Flask`, `requests`, `playwright`

## 🛠️ Inštalácia a spustenie

1. Stiahnite si tento repozitár do vášho servera/kontajnera.
2. Nainštalujte závislosti a prehliadač pre Playwright:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   
3. **Konfigurácia:** Otvorte súbory `jf_sync.py` a `proxy_server.py` a upravte sekciu `--- KONFIGURÁCIA ---` (nastavte správnu IP adresu, port a cestu k zložkám s filmami).

4. Spustite Proxy server (ideálne ako službu na pozadí):
   ```bash
   python3 proxy_server.py
   ```

5. Otvorte prehliadač a zadajte `http://<VASA_IP>:5000`. Pridajte filmy/seriály a kliknite na **Indexovať**.

6. Pridajte v Jellyfine zložku (nastavenú v `BASE_PATH`) ako novú knižnicu a dajte ju preskenovať.
