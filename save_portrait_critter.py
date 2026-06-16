import os
import re
import io
import requests
from bs4 import BeautifulSoup
from PIL import Image

BASE_URL = "https://wiki.ultimacodex.com"
CATEGORY_URL = "https://wiki.ultimacodex.com/wiki/Category:Ultima_Underworld_Animations"
OUTPUT_DIR = "ultima_underworld_critters"

# Cabeçalho para simular um navegador real e evitar bloqueios/timeouts do servidor
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_critter_images():
    print("🔍 Buscando critters na página da categoria (pode demorar um pouco)...")
    try:
        # Aumentamos o timeout para 30 segundos e adicionamos os headers
        response = requests.get(CATEGORY_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Erro ao acessar a página principal: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    downloaded = 0
    links = soup.find_all('a', href=True)
    
    for link in links:
        href = link['href']
        
        if not ('/wiki/File:' in href and 'critter' in href.lower() and '.gif' in href.lower()):
            continue
            
        file_page_url = f"{BASE_URL}{href}"
        
        match = re.search(r'critter[._]?(\d+)', href, re.IGNORECASE)
        if not match:
            continue
            
        num = match.group(1).lstrip('0') or '0'
        filename = f"{num}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        if os.path.exists(filepath):
            print(f"⏭️  Já existe: {filename}")
            continue
            
        try:
            # Acessa a página interna de cada arquivo usando os mesmos headers
            file_page_res = requests.get(file_page_url, headers=HEADERS, timeout=20)
            file_page_soup = BeautifulSoup(file_page_res.text, 'html.parser')
            
            media_div = file_page_soup.find('div', class_='fullMedia')
            if not media_div:
                continue
                
            img_relative_url = media_div.find('a')['href']
            img_url = f"{BASE_URL}{img_relative_url}"
            
            print(f"🔄 Baixando: {filename}...")
            img_data = requests.get(img_url, headers=HEADERS, timeout=20).content
            
            with Image.open(io.BytesIO(img_data)) as img:
                img = img.convert('RGBA')
                img.save(filepath, 'PNG')
                
            print(f"✅ Salvo: {filename}")
            downloaded += 1
            
        except Exception as e:
            print(f"❌ Erro ao processar {filename}: {e}")
    
    print(f"\n🎉 Concluído! {downloaded} imagens salvas na pasta '{OUTPUT_DIR}'")

if __name__ == "__main__":
    download_critter_images()