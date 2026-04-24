import requests
from bs4 import BeautifulSoup
import json
import time
import os

# ─── Target Pages ─────────────────────────────────────────────────────────────
# Normal page: just the username string
# Profile by ID: use "profile.php?id=XXXXXXXXX"

PAGES = [
    "PinakiRightsActivist",
    "BJI.Official",
    "profile.php?id=100006640866646",
    "tariquerahman.bdbnp",
    "genzbds",
    "EliasHossainBangladesh",
]

# Page গুলোর বাংলা নাম (author হিসেবে দেখাবে app এ)
PAGE_NAMES = {
    "PinakiRightsActivist":       "পিনাকী ভট্টাচার্য",
    "BJI.Official":               "বাংলাদেশ জামায়াতে ইসলামী",
    "profile.php?id=100006640866646": "ইসলামী ব্যক্তিত্ব",
    "tariquerahman.bdbnp":        "তারেক রহমান",
    "genzbds":                    "Gen Z Bangladesh",
    "EliasHossainBangladesh":     "এলিয়াস হোসেন",
}

# ─── HTTP Config ──────────────────────────────────────────────────────────────

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

COOKIES = {
    'c_user': os.environ.get('FB_C_USER', ''),
    'xs':     os.environ.get('FB_XS', ''),
}

# ─── Scraper ──────────────────────────────────────────────────────────────────

def get_posts_from_page(page_identifier):
    url = f"https://mbasic.facebook.com/{page_identifier}"
    author_name = PAGE_NAMES.get(page_identifier, page_identifier)

    try:
        session = requests.Session()
        res = session.get(
            url,
            headers=HEADERS,
            cookies=COOKIES,
            timeout=20,
            allow_redirects=True,
        )

        print(f"  Status : {res.status_code}")
        print(f"  URL    : {res.url}")

        if 'login' in res.url or 'checkpoint' in res.url:
            print(f"  ⚠️  Login redirect — cookie সমস্যা!")
            return []

        soup = BeautifulSoup(res.content, 'html.parser')

        title = soup.find('title')
        print(f"  Title  : {title.get_text() if title else 'No title'}")

        # Article elements খোঁজা (fallback chain)
        articles = soup.find_all('div', attrs={'data-ft': True})
        if not articles:
            articles = soup.find_all('article')
        if not articles:
            articles = soup.find_all(
                'div', id=lambda x: x and 'story' in str(x).lower()
            )

        print(f"  Found  : {len(articles)} article blocks")

        posts = []
        for i, article in enumerate(articles[:10]):
            try:
                text = article.get_text(separator=' ', strip=True)
                if len(text) < 50:
                    continue

                img = article.find('img')

                link = ""
                for a in article.find_all('a', href=True):
                    if 'story' in a['href'] or 'permalink' in a['href']:
                        link = "https://mbasic.facebook.com" + a['href']
                        break

                posts.append({
                    'id':       f"{page_identifier}_{i}_{int(time.time())}",
                    'author':   author_name,
                    'content':  text[:500],
                    'imageUrl': img['src'] if img and 'src' in img.attrs else "",
                    'shareUrl': link,
                    'time':     str(int(time.time())),
                })
            except Exception:
                continue

        print(f"  ✅ {len(posts)} posts সংগ্রহ হয়েছে")
        return posts

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return []


# ─── Main ─────────────────────────────────────────────────────────────────────

def generate_data_json():
    all_posts = []

    for page in PAGES:
        print(f"\n⏳ Fetching: {PAGE_NAMES.get(page, page)}")
        posts = get_posts_from_page(page)
        all_posts.extend(posts)
        time.sleep(5)   # rate-limit এড়াতে

    output = {
        'lastUpdated': int(time.time()),
        'totalPosts':  len(all_posts),
        'posts':       all_posts,
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 সম্পন্ন! মোট {len(all_posts)} পোস্ট data.json এ সেভ হয়েছে।")


if __name__ == "__main__":
    generate_data_json()