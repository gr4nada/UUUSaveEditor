import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote

# ====================== EWHOAMI DICTIONARY ======================
EWHOAMI = {
    0: "Generic",
    1: "Corby", 2: "Shak", 3: "Goldthirst", 4: "Shanklick", 5: "Eyesnack",
    6: "Marrowsuck", 7: "Ketchaval", 8: "Retichall", 9: "Vernix", 10: "Lanugo",
    11: "Thorlson", 12: "DornaIronfist", 13: "Morlock", 14: "DrOwl",
    15: "Sseetharee", 16: "Ishtass", 17: "SetharStrongarm", 18: "LakshiLongtooth",
    19: "Hagbard", 20: "Gulik", 21: "Steeltoe", 22: "Golem", 23: "Judy",
    24: "Prisoner", 25: "Door", 26: "Celaven", 27: "Garamon", 28: "Zak",
    64: "Jaacar", 65: "Eb", 66: "Drog", 67: "Bragit",
    88: "Brawnclan", 89: "Hewstone", 90: "Ironwit", 91: "Janus",
    110: "Gazer",
    112: "Bandit", 113: "HeadBandit", 114: "Issleek",
    136: "Oradinar", 137: "Linnet", 138: "Derek", 139: "Trisch", 140: "Ree",
    141: "Feznor", 142: "Rodrick", 143: "Biden", 144: "Rawstag",
    146: "Doris", 147: "Kyle", 148: "Cecil", 149: "Meredith",
    161: "Anjor", 162: "Kneenibble",
    184: "Delanrey", 185: "Nilpont", 186: "Folina", 187: "Illomo",
    188: "Gralwart", 189: "Shenilor", 190: "Bronus", 191: "Ranthru",
    192: "Fyrgen", 193: "Louvnon", 194: "Dominus",
    207: "Warren", 208: "Cardon",
    209: "Guard209", 210: "Naruto", 211: "Dantes", 212: "Kallistan",
    213: "Fintor", 214: "Bolinard", 215: "Smonden", 216: "Jailor",
    217: "Gurstang", 218: "Griffle", 219: "Guard219", 220: "Guard220",
    221: "Imp", 222: "Guard222",
    231: "Tyball", 232: "Carasso", 233: "Count",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def download_portraits(output_dir="portraits"):
    os.makedirs(output_dir, exist_ok=True)
    
    base_url = "https://wiki.ultimacodex.com/wiki/Category:Ultima_Underworld_Portraits"
    
    print("🔄 Baixando página da categoria...")
    response = requests.get(base_url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    downloaded = 0
    files_found = 0
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('/wiki/File:') and any(href.lower().endswith(ext) for ext in ('.png', '.gif', '.jpg')):
            files_found += 1
            file_page_url = urljoin("https://wiki.ultimacodex.com", href)
            
            try:
                file_resp = requests.get(file_page_url, headers=HEADERS, timeout=10)
                file_soup = BeautifulSoup(file_resp.text, 'html.parser')
                
                # Pega a imagem real
                img_tag = file_soup.find('img', src=re.compile(r'/images/.*\.(png|gif|jpg)'))
                if not img_tag:
                    continue
                    
                img_url = urljoin("https://wiki.ultimacodex.com", img_tag['src'])
                original_filename = img_tag['src'].split('/')[-1]
                
                # Nome limpo
                name_base = unquote(original_filename.rsplit('.', 1)[0]).replace('_', ' ').strip()
                
                # Mapeia para ID
                found_id = None
                name_clean = name_base.lower().replace(' ', '').replace("'", "")
                for who_id, who_name in EWHOAMI.items():
                    if who_name.lower().replace(' ', '').replace("'", "") == name_clean:
                        found_id = who_id
                        break
                
                if found_id is not None:
                    new_filename = f"{found_id:03d}.png"
                    print(f"✅ {name_base:<20} → {new_filename}")
                else:
                    new_filename = f"unknown_{original_filename}"
                    print(f"⚠️  Não mapeado: {name_base}")
                
                # Download
                img_data = requests.get(img_url, headers=HEADERS, timeout=10).content
                save_path = os.path.join(output_dir, new_filename)
                
                with open(save_path, 'wb') as f:
                    f.write(img_data)
                
                downloaded += 1
                
            except Exception as e:
                print(f"❌ Erro ao processar {name_base}: {e}")
    
    print(f"\n🎉 Concluído!")
    print(f"   Arquivos encontrados: {files_found}")
    print(f"   Imagens baixadas:    {downloaded}")
    print(f"   Pasta:               {os.path.abspath(output_dir)}")


def save_whoami_dict(filename="ewhoami.py"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write('''# EWhoAmI Enum mapping for Ultima Underworld
# Generated automatically

EWHOAMI = {
''')
        for k, v in sorted(EWHOAMI.items()):
            f.write(f'    {k}: "{v}",\n')
        f.write('}\n\n')
        f.write('def whoami_name(whoami_id: int) -> str:\n')
        f.write('    """Retorna o nome do NPC ou "NPC#ID" se não mapeado."""\n')
        f.write('    return EWHOAMI.get(whoami_id, f"NPC#{whoami_id}")\n')
    print(f"📄 Dicionário salvo em '{filename}'")


if __name__ == "__main__":
    save_whoami_dict()
    download_portraits("portraits")