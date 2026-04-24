import requests
from bs4 import BeautifulSoup
import json
import time

# আপনার টার্গেট পলিটিশিয়ানদের পেজ লিস্ট
PAGES = [
    "obaidul.quader",
    "sheikh.hasina",
    # যত পেজ চান যোগ করুন
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Accept-Language': 'bn-BD,bn;q=0.9,en;q=0.8',
}

def get_posts_from_page(page_name):
    url = f"https://mbasic.facebook.com/{page_name}"
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.content, 'html.parser')
        
        posts = []
        
        # পোস্ট আর্টিকেলগুলো খুঁজুন
        for article in soup.find_all('div', attrs={'data-ft': True}):
            try:
                # টেক্সট কন্টেন্ট
                text_div = article.find('div', class_=lambda x: x and 'story_body' in str(x))
                content = text_div.get_text(separator='\n').strip() if text_div else ""
                
                # ছবি
                img_tag = article.find('img')
                image_url = img_tag['src'] if img_tag else ""
                
                # পোস্ট লিংক (Share URL)
                share_link = ""
                for a in article.find_all('a', href=True):
                    if '/story.php' in a['href'] or 'story_fbid' in a['href']:
                        share_link = "https://facebook.com" + a['href']
                        break
                
                # পোস্ট টাইম
                abbr = article.find('abbr')
                post_time = abbr.get_text() if abbr else ""
                
                if content:  # শুধু টেক্সট আছে এমন পোস্ট নেব
                    posts.append({
                        'id': f"{page_name}_{len(posts)}",
                        'author': page_name,
                        'content': content,
                        'imageUrl': image_url,
                        'shareUrl': share_link,
                        'time': post_time
                    })
                    
            except Exception as e:
                print(f"Post parse error: {e}")
                continue
        
        return posts
    
    except Exception as e:
        print(f"Page fetch error for {page_name}: {e}")
        return []

def generate_data_json():
    all_posts = []
    
    for page in PAGES:
        print(f"Fetching: {page}")
        posts = get_posts_from_page(page)
        all_posts.extend(posts)
        time.sleep(3)  # ব্লক এড়াতে ৩ সেকেন্ড অপেক্ষা
    
    # সর্বশেষ আপডেট টাইম যোগ করুন
    output = {
        'lastUpdated': int(time.time()),
        'posts': all_posts
    }
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"Done! {len(all_posts)} posts saved.")

if __name__ == "__main__":
    generate_data_json()