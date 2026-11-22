import json, os, re, time, urllib.error, urllib.parse, urllib.request
from io import BytesIO
from PIL import Image

UA = {"User-Agent": "hokkaido-2027-trip-app/1.0 (personal travel itinerary)"}


def get(url):
    for i in range(6):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or i == 5:
                raise
            time.sleep(10 * (i + 1))


spots = json.load(open("tools/spots.json", encoding="utf-8"))
os.makedirs("img/spots", exist_ok=True)
credits = json.load(open("img/spots/credits.json", encoding="utf-8")) if os.path.exists("img/spots/credits.json") else {}
for sid, title in spots.items():
    if os.path.exists(f"img/spots/{sid}.jpg") and sid in credits:
        continue
    try:
        wiki, t = ("en", title[3:]) if title.startswith("en:") else ("ja", title)
        q = urllib.parse.urlencode({"action": "query", "format": "json", "prop": "pageimages",
                                    "piprop": "name|thumbnail", "pithumbsize": "960",
                                    "redirects": "1", "titles": t})
        j = json.loads(get(f"https://{wiki}.wikipedia.org/w/api.php?" + q))
        page = next(iter(j["query"]["pages"].values()))
        name = page.get("pageimage")
        thumb = page.get("thumbnail", {}).get("source")
        if not (name and thumb):
            print(sid, title, "NO IMAGE")
            continue
        q2 = urllib.parse.urlencode({"action": "query", "format": "json", "prop": "imageinfo",
                                     "iiprop": "extmetadata", "titles": "File:" + name})
        m = json.loads(get("https://commons.wikimedia.org/w/api.php?" + q2))
        info = next(iter(m["query"]["pages"].values())).get("imageinfo", [{}])[0].get("extmetadata", {})
        artist = re.sub("<[^>]+>", "", info.get("Artist", {}).get("value", "")).strip()
        lic = info.get("LicenseShortName", {}).get("value", "")
        im = Image.open(BytesIO(get(thumb))).convert("RGB")
        im.thumbnail((900, 900))
        im.save(f"img/spots/{sid}.jpg", "JPEG", quality=76, optimize=True, progressive=True)
        credits[sid] = {"title": title, "file": name, "artist": artist[:80], "license": lic,
                        "url": "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(name)}
        print(sid, title, name, lic, im.size)
        time.sleep(4)
    except Exception as e:
        print(sid, title, "ERROR", e)
json.dump(credits, open("img/spots/credits.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
