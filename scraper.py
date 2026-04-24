import requests
from bs4 import BeautifulSoup
import json
import time

PAGES = [
    "obaidul.quader",
    "sheikh.hasina",
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

def get_posts_from_page(page_name):
    url = f"https://mbasic.facebook.com/{page_name}"
    
    try:
        session = requests.Session()
        res = session.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
        
        print(f"Status: {res.status_code}")
        print(f"Final URL: {res.url}")
        
        # Login page এ redirect হয়েছে কিনা চেক করুন
        if 'login' in res.url or 'checkpoint' in res.url:
            print(f"⚠️ {page_name}: Facebook login page এ redirect হয়েছে!")
            return []
        
        soup = BeautifulSoup(res.content, 'html.parser')
        
        # পেজের টাইটেল দেখুন
        title = soup.find('title')
        print(f"Page title: {title.get_text() if title else 'No title'}")
        
        posts = []
        
        # মেথড ১: data-ft দিয়ে
        articles = soup.find_all('div', attrs={'data-ft': True})
        print(f"data-ft divs found: {len(articles)}")
        
        # মেথড ২: article ট্যাগ
        if not articles:
            articles = soup.find_all('article')
            print(f"article tags found: {len(articles)}")
        
        # মেথড ৩: সরাসরি টেক্সট ব্লক খোঁজা
        if not articles:
            # mbasic এর স্ট্রাকচার আলাদা হতে পারে
            articles = soup.find_all('div', id=lambda x: x and 'story' in str(x).lower())
            print(f"story divs found: {len(articles)}")

        for i, article in enumerate(articles[:10]):  # প্রথম ১০টা
            try:
                text = article.get_text(separator=' ', strip=True)
                if len(text) > 50:  # অর্থবহ টেক্সট
                    img = article.find('img')
                    link = ""
                    for a in article.find_all('a', href=True):
                        if 'story' in a['href'] or 'permalink' in a['href']:
                            link = "https://mbasic.facebook.com" + a['href']
                            break
                    
                    posts.append({
                        'id': f"{page_name}_{i}_{int(time.time())}",
                        'author': page_name,
                        'content': text[:500],
                        'imageUrl': img['src'] if img and 'src' in img.attrs else "",
                        'shareUrl': link,
                        'time': str(int(time.time()))
                    })
            except:
                continue
        
        print(f"✅ {page_name}: {len(posts)} posts পাওয়া গেছে")
        return posts
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def generate_data_json():
    all_posts = []
    
    for page in PAGES:
        print(f"\n⏳ Fetching: {page}")
        posts = get_posts_from_page(page)
        all_posts.extend(posts)
        time.sleep(5)
    
    output = {
        'lastUpdated': int(time.time()),
        'totalPosts': len(all_posts),
        'posts': all_posts
    }
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 সম্পন্ন! মোট {len(all_posts)} পোস্ট।")

if __name__ == "__main__":
    generate_data_json()