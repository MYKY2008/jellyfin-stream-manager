# Jellyfin Stream Manager

Nástroj na automatickú synchronizáciu a prehrávanie webových streamov (napríklad zo stránok ako *mrkaj.si*) priamo v [Jellyfin](https://jellyfin.org/) mediálnom serveri pomocou `.strm` súborov. 

Skladá sa z dvoch hlavných častí:
1. **Proxy Server a Web UI (`proxy_server.py`)** - Beží na pozadí, poskytuje webové rozhranie na pridávanie obsahu a dynamicky získava aktuálne `.m3u8` streamovacie linky pomocou bezhlavého prehliadača.
2. **Synchronizačný skript (`jf_sync.py`)** - Vytvára štruktúru zložiek pre Jellyfin. Pri seriáloch dokáže automaticky prejsť sezóny a epizódy a overiť ich dostupnosť. Po stiahnutí súborov **nástroj automaticky cez API aktualizuje Jellyfin knižnicu**, takže sa nový obsah hneď zobrazí vo vašej ponuke.

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
   ```

3. **Konfigurácia:** Otvorte súbory `jf_sync.py` a `proxy_server.py` a upravte sekciu `=== KONFIGURÁCIA PRE UŽÍVATEĽA ===`:
   - `BASE_PATH`, `PROXY_IP`, `PROXY_PORT`: Nastavte správne cesty a IP adresu servera.
   - `JELLYFIN_URL`: URL adresa vášho Jellyfin servera (napr. `http://192.168.0.99:8096`).
   - `JELLYFIN_API_KEY`: Získate v Jellyfin rozhraní: **Dashboard (Ovládací panel)** -> **API Keys (Kľúče API)** -> vytvoriť nový kľúč.
   - `JELLYFIN_LIBRARY_NAME`: Presný názov knižnice v Jellyfine (napr. `Streams`), ktorú ste si vytvorili pre tieto `.strm` súbory.

4. Spustite Proxy server (ideálne ako službu na pozadí):
   ```bash
   python3 proxy_server.py
   ```

5. Otvorte prehliadač a zadajte `http://<VASA_IP>:5000`. Pridajte filmy/seriály a kliknite na **Pridať a Refreshnúť** alebo použite ikonu **🔄**.

6. **Hotovo!** O všetko ostatné sa postará skript. Vygeneruje súbory a automaticky dá Jellyfinu pokyn na preskenovanie knižnice, takže obsah môžete o pár sekúnd začať pozerať.

## 🛑 Upozornenie (Disclaimer)
Tento projekt bol vytvorený a je poskytovaný **výhradne na edukačné a študijné účely**. Slúži ako ukážka automatizácie a práce s webovým obsahom prostredníctvom jazyka Python. Autor tohto softvéru **nenenesie absolútne žiadnu zodpovednosť** za to, aký obsah používatelia pomocou tohto nástroja konzumujú, spracovávajú alebo šíria. Zodpovednosť za dodržiavanie autorských práv a legálnosť prehrávaného obsahu vo vašej krajine nesiete výhradne **vy**.

## 📄 Licencia
Tento projekt je vydaný pod **MIT licenciou**. 
Softvér je poskytovaný "tak, ako je", bez akýchkoľvek záruk, či už výslovných alebo implicitných. Môžete ho voľne používať, upravovať a šíriť, avšak autor nenesie zodpovednosť za žiadne škody alebo problémy spôsobené jeho používaním.
