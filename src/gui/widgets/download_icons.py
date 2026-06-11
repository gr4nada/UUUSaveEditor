import os
import re
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote

# ====================== FIX PARA IMPORT ======================
# Adiciona o diretório raiz do projeto ao PYTHONPATH
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

from src.core.enums import EObjectType

# Cabeçalhos para evitar bloqueio 406
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}


def normalize_name(text: str) -> str:
    """Normaliza nome para matching mais flexível"""
    return re.sub(r'[^a-z0-9]', '', text.lower())


def download_icons(output_dir="icons"):
    os.makedirs(output_dir, exist_ok=True)
    
    pages = [
        "https://wiki.ultimacodex.com/index.php?title=Category:Ultima_Underworld_Icons&fileuntil=UW1Sling.png#mw-category-media",
        "https://wiki.ultimacodex.com/index.php?title=Category:Ultima_Underworld_Icons&filefrom=UW1Sling.png#mw-category-media"
    ]
    
    downloaded = 0
    not_mapped = 0
    
    print("🔄 Iniciando download dos ícones...\n")
    
    for page_url in pages:
        print(f"📄 Processando: {page_url.split('&')[0]}...")
        
        try:
            response = requests.get(page_url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                if not (href.startswith('/wiki/File:') and 
                       any(href.lower().endswith(ext) for ext in ('.png', '.gif', '.jpg'))):
                    continue
                
                file_page_url = urljoin("https://wiki.ultimacodex.com", href)
                
                try:
                    file_resp = requests.get(file_page_url, headers=HEADERS, timeout=12)
                    file_soup = BeautifulSoup(file_resp.text, 'html.parser')
                    
                    img_tag = file_soup.find('img', src=re.compile(r'/images/.*\.(png|gif|jpg)'))
                    if not img_tag:
                        continue
                        
                    img_url = urljoin("https://wiki.ultimacodex.com", img_tag['src'])
                    original_filename = unquote(img_tag['src'].split('/')[-1])
                    name_base = original_filename.rsplit('.', 1)[0]
                    
                    # Matching com EObjectType
                    found_id = None
                    norm_name = normalize_name(name_base)
                    
                    for member in EObjectType:
                        if normalize_name(member.name) in norm_name or norm_name in normalize_name(member.name):
                            found_id = member.value
                            break
                    
                    if found_id is not None:
                        new_filename = f"{found_id:03d}.png"
                        print(f"✅ {name_base:<28} → {new_filename} (ID {found_id})")
                    else:
                        new_filename = f"unknown_{original_filename}"
                        print(f"⚠️  Não mapeado: {name_base}")
                        not_mapped += 1
                    
                    # Download
                    img_data = requests.get(img_url, headers=HEADERS, timeout=10).content
                    save_path = os.path.join(output_dir, new_filename)
                    
                    with open(save_path, 'wb') as f:
                        f.write(img_data)
                    downloaded += 1
                    
                except Exception as e:
                    print(f"   ❌ Erro ao baixar {name_base}: {e}")
                    
        except Exception as e:
            print(f"❌ Erro ao acessar página: {e}")
    
    print("\n" + "="*70)
    print("🎉 DOWNLOAD FINALIZADO!")
    print(f"   Total baixado     : {downloaded} ícones")
    print(f"   Não mapeados      : {not_mapped}")
    print(f"   Salvo em          : {os.path.abspath(output_dir)}")
    print("="*70)


if __name__ == "__main__":
    download_icons("icons")