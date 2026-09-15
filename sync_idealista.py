import json, re, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

SOURCE = 'https://www.idealista.com/pro/projecthouseagents/'
OUT = Path('data/inmuebles.json')
UA = 'Mozilla/5.0 (compatible; ProjectHousePropertySync/1.0)'


def clean(s):
    return re.sub(r'\s+', ' ', s or '').strip()


def first_match(pattern, text, default=''):
    m = re.search(pattern, text, re.I)
    return clean(m.group(1)) if m else default


def find_card(a):
    # Find the smallest ancestor that looks like a property result.
    node = a
    for _ in range(7):
        node = node.parent
        if not node:
            break
        txt = clean(node.get_text(' ', strip=True))
        if 20 < len(txt) < 1800 and ('€' in txt or '€' in txt.replace('.', '')) and 'm²' in txt:
            return node
    return a.parent


def extract():
    r = requests.get(SOURCE, headers={'User-Agent': UA, 'Accept-Language': 'es-ES,es;q=0.9'}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')

    items = []
    seen = set()
    for a in soup.select('a[href*="/inmueble/"]'):
        href = a.get('href')
        if not href:
            continue
        href = urljoin(SOURCE, href)
        m = re.search(r'/inmueble/(\d+)/', href)
        if not m:
            continue
        pid = m.group(1)
        if pid in seen:
            continue
        seen.add(pid)

        card = find_card(a)
        text = clean(card.get_text(' ', strip=True))
        title = clean(a.get_text(' ', strip=True))
        if not title:
            title = clean(a.get('title', ''))

        # Stats are normally in the result card.
        price = first_match(r'(\d[\d\.]*\s*€)', text)
        area = first_match(r'(\d[\d\.]*\s*m²)', text)
        rooms = first_match(r'(\d+\s*hab\.)', text)

        img = card.find('img') if card else None
        image = ''
        if img:
            image = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or ''
            image = urljoin(SOURCE, image)

        # Prefer the heading/title-looking anchor text; use surrounding text as location fallback.
        location = ''
        for node in card.find_all(['div','span','p','h2','h3']) if card else []:
            t = clean(node.get_text(' ', strip=True))
            if t and t != title and ('€' not in t) and ('m²' not in t) and ('hab.' not in t) and len(t) < 120:
                if any(x in t.lower() for x in ['barcelona','vallès','brunyola','lliçà','mollet','girona']):
                    location = t
                    break
        if not location:
            location = title

        # The public profile gives us enough data for a safe card. Never publish a partial sync.
        if not title or not price or not area:
            continue

        items.append({
            'id': pid,
            'url': href,
            'image': image,
            'location': location,
            'title': title,
            'type': 'Inmueble',
            'price': price,
            'rooms': rooms,
            'area': area
        })

    if not items:
        raise RuntimeError('No se han detectado inmuebles; se conserva el JSON anterior por seguridad.')
    return items


def main():
    try:
        items = extract()
    except Exception as e:
        print(f'[sync] ERROR: {e}', file=sys.stderr)
        sys.exit(1)

    payload = {
        'source': SOURCE,
        'updatedAt': datetime.now(timezone.utc).isoformat(),
        'properties': items,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'[sync] OK: {len(items)} inmuebles sincronizados.')

if __name__ == '__main__':
    main()
