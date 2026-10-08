"""Sonde une page wiki : liste les <img> dans l'ordre + contexte du titre.

Usage : python -m scripts.probe_icon <url>
"""
from __future__ import annotations

import re
import ssl
import sys
import urllib.request

CTX = ssl._create_unverified_context()


def main():
    url = sys.argv[1]
    req = urllib.request.Request(url, headers={"User-Agent": "probe/1.0"})
    html = urllib.request.urlopen(req, timeout=20, context=CTX).read().decode("utf-8", "replace")

    imgs = re.findall(r'<img[^>]+>', html, re.I)
    print(f"{len(imgs)} balises <img>. Les 12 premières :")
    for t in imgs[:12]:
        src = re.search(r'(?:data-src|src)=["\']([^"\']+)', t)
        print("  ", src.group(1) if src else "?", "  ::", t[:90])

    # Contexte autour de la 1re occurrence d'un lien de type item (data-tippy / item card)
    for key in ['item_11_', 'class="item', 'og:image', 'itemprop="image"']:
        i = html.find(key)
        if i >= 0:
            print(f"\n[{key}] ...{html[max(0, i - 140):i + 80]}...".replace(chr(10), ' '))


if __name__ == "__main__":
    main()
