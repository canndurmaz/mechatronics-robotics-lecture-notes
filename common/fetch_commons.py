#!/usr/bin/env python3
"""Search / download freely-licensed figures from Wikimedia Commons.

Usage:
  fetch_commons.py search "<query>" [n]           -> list File: titles with license + size
  fetch_commons.py get "File:Name.ext" outname    -> downloads a PNG/JPG rendition (max 1600px wide)
                                                    to ../figures/<outname>.<ext> and appends a line
                                                    to ../figures/CREDITS.tsv (title, author, license, url)
SVGs are fetched as PNG thumbnails so pdflatex can include them.
"""
import json, os, re, sys, urllib.parse, urllib.request, html

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "MechatronicsTrainingBuilder/1.0 (educational slides; contact: local)"}
FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures")


def api(params):
    params = dict(params, format="json")
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def strip(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def info(titles):
    d = api({"action": "query", "titles": "|".join(titles), "prop": "imageinfo",
             "iiprop": "url|extmetadata|size|mime", "iiurlwidth": 1600})
    out = []
    for p in d["query"]["pages"].values():
        if "imageinfo" not in p:
            continue
        ii = p["imageinfo"][0]
        m = ii.get("extmetadata", {})
        out.append(dict(title=p["title"], url=ii.get("thumburl") or ii["url"], page=ii.get("descriptionurl"),
                        mime=ii.get("mime"), w=ii.get("width"), h=ii.get("height"),
                        license=strip(m.get("LicenseShortName", {}).get("value")),
                        author=strip(m.get("Artist", {}).get("value"))[:80],
                        desc=strip(m.get("ImageDescription", {}).get("value"))[:120]))
    return out


def search(q, n=10):
    d = api({"action": "query", "list": "search", "srsearch": q, "srnamespace": 6, "srlimit": n})
    titles = [s["title"] for s in d["query"]["search"]]
    for i in info(titles) if titles else []:
        if not (i["mime"] or "").startswith("image/"):
            continue
        print(f"{i['title']}\n   {i['license']} | {i['author']} | {i['w']}x{i['h']} {i['mime']}\n   {i['desc']}")


def get(title, outname):
    i = info([title])
    if not i:
        sys.exit("not found: " + title)
    i = i[0]
    lic = i["license"].lower()
    if not any(k in lic for k in ("cc", "public domain", "pd", "gfdl", "cc0")):
        sys.exit("refusing: unclear license " + i["license"])
    url = i["url"]
    ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
    if ext not in (".png", ".jpg", ".jpeg"):
        ext = ".png"
    os.makedirs(FIG, exist_ok=True)
    dest = os.path.join(FIG, outname + ext)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
        f.write(r.read())
    with open(os.path.join(FIG, "CREDITS.tsv"), "a") as f:
        f.write("\t".join([outname + ext, i["title"], i["author"], i["license"], i["page"] or ""]) + "\n")
    print(f"saved {dest}\nCREDIT: {i['author']}, {i['license']}, via Wikimedia Commons ({i['title']})")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "search":
        search(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 10)
    elif len(sys.argv) == 4 and sys.argv[1] == "get":
        get(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
