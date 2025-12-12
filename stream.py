#!/usr/bin/env python3                                                                                                                       
                                                                                                                                             
import sys                                                                                                                                   
import os                                                                                                                                    
import re                                                                                                                                    
import json                                                                                                                                  
import shutil                                                                                                                                
import subprocess                                                                                                                            
import requests                                                                                                                              
from urllib.parse import urljoin                                                                                                             
from bs4 import BeautifulSoup                                                                                                                
                                                                                                                                             
# --- Configuration Manager ---                                                                                                              
                                                                                                                                             
class Config:                                                                                                                                
    FILE_NAME = "stream_config.json"                                                                                                        
                                                                                                                                             
    DEFAULTS = {                                                                                                                             
        "base_url": "https://flixhq.to",                                                                                                     
        "api_url": "https://dec.eatmynerds.live",                                                                                            
        "provider": "Vidcloud", # Options: Vidcloud, UpCloud                                                                                 
        "quality": "Best",      # Options: Best, 1080, 720, 480, 360                                                                         
        "sub_language": "english",                                                                                                           
        "autoplay": False,                                                                                                                   
        "mpv_options": "--fs --force-window=immediate"                                                                                       
    }                                                                                                                                        
                                                                                                                                             
    def __init__(self):                                                                                                                      
        self.data = self.load()                                                                                                              
                                                                                                                                             
    def load(self):                                                                                                                          
        if not os.path.exists(self.FILE_NAME):                                                                                               
            self.save(self.DEFAULTS)                                                                                                         
            return self.DEFAULTS.copy()                                                                                                      
                                                                                                                                             
        try:                                                                                                                                 
            with open(self.FILE_NAME, 'r') as f:                                                                                             
                data = json.load(f)                                                                                                          
                # Merge with defaults                                                                                                        
                for key, val in self.DEFAULTS.items():                                                                                       
                    if key not in data:                                                                                                      
                        data[key] = val                                                                                                      
                return data                                                                                                                  
        except Exception:                                                                                                                    
            return self.DEFAULTS.copy()                                                                                                      
                                                                                                                                             
    def save(self, data=None):                                                                                                               
        if data: self.data = data                                                                                                            
        with open(self.FILE_NAME, 'w') as f:                                                                                                 
            json.dump(self.data, f, indent=4)                                                                                                
                                                                                                                                             
    def get(self, key):                                                                                                                      
        return self.data.get(key, self.DEFAULTS.get(key))                                                                                    
                                                                                                                                             
    def set(self, key, value):                                                                                                               
        self.data[key] = value                                                                                                               
        self.save()                                                                                                                          
                                                                                                                                             
# --- Visuals ---                                                                                                                            
                                                                                                                                             
class Colors:                                                                                                                                
    HEADER = '\033[95m'                                                                                                                      
    BLUE = '\033[94m'                                                                                                                        
    CYAN = '\033[96m'                                                                                                                        
    GREEN = '\033[92m'                                                                                                                       
    YELLOW = '\033[93m'                                                                                                                      
    FAIL = '\033[91m'                                                                                                                        
    ENDC = '\033[0m'                                                                                                                         
    BOLD = '\033[1m'                                                                                                                         
                                                                                                                                             
def check_dependencies():                                                                                                                    
    if not shutil.which("mpv"):                                                                                                              
        print(f"{Colors.FAIL}[!] Error: 'mpv' player is not installed.{Colors.ENDC}")                                                        
        sys.exit(1)                                                                                                                          
                                                                                                                                             
# --- Main Application ---                                                                                                                   
                                                                                                                                             
class StreamApp:                                                                                                                            
    def __init__(self):                                                                                                                      
        self.config = Config()                                                                                                               
        self.session = requests.Session()                                                                                                    
        self.update_headers()                                                                                                                
                                                                                                                                             
    def update_headers(self):                                                                                                                
        self.session.headers.update({                                                                                                        
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36', 
            'Referer': self.config.get("base_url")                                                                                           
        })                                                                                                                                   
                                                                                                                                             
    def notify(self, message, level="Info"):                                                                                                 
        if level == "Error":                                                                                                                 
            print(f"{Colors.FAIL}[!] {message}{Colors.ENDC}")                                                                                
        elif level == "Success":                                                                                                             
            print(f"{Colors.GREEN}[+] {message}{Colors.ENDC}")                                                                               
        elif level == "Info":                                                                                                                
            print(f"{Colors.CYAN}[*] {message}{Colors.ENDC}")                                                                                
        else:                                                                                                                                
            print(f"{message}")                                                                                                              
                                                                                                                                             
    def get_soup(self, path):                                                                                                                
        url = path if path.startswith("http") else f"{self.config.get('base_url')}{path}"                                                    
        try:                                                                                                                                 
            response = self.session.get(url, timeout=15)                                                                                     
            response.raise_for_status()                                                                                                      
            return BeautifulSoup(response.text, 'html.parser')                                                                               
        except requests.exceptions.RequestException as e:                                                                                    
            self.notify(f"Network error: {e}", "Error")                                                                                      
            return None                                                                                                                      
                                                                                                                                             
    # --- Settings Menu ---                                                                                                                  
                                                                                                                                             
    def settings_menu(self):                                                                                                                 
        while True:                                                                                                                          
            c = self.config.data                                                                                                             
            print(f"\n{Colors.HEADER}--- Settings ---{Colors.ENDC}")                                                                         
            print(f"1. Base URL:      {Colors.YELLOW}{c['base_url']}{Colors.ENDC}")                                                          
            print(f"2. Provider:      {Colors.YELLOW}{c['provider']}{Colors.ENDC}")                                                          
            print(f"3. Quality:       {Colors.YELLOW}{c['quality']}{Colors.ENDC}")                                                           
            print(f"4. Sub Language:  {Colors.YELLOW}{c['sub_language']}{Colors.ENDC}")                                                      
            print(f"5. Autoplay:      {Colors.YELLOW}{'ON' if c['autoplay'] else 'OFF'}{Colors.ENDC}")                                       
            print(f"6. MPV Options:   {Colors.YELLOW}{c['mpv_options']}{Colors.ENDC}")                                                       
            print(f"{Colors.FAIL}b. Back{Colors.ENDC}")                                                                                      
                                                                                                                                             
            choice = input(f"\n{Colors.CYAN}Edit setting # > {Colors.ENDC}").strip().lower()                                                 
                                                                                                                                             
            if choice == 'b': break                                                                                                          
                                                                                                                                             
            if choice == '1':                                                                                                                
                new_val = input("Enter new Base URL (e.g., https://flixhq.to): ").strip()                                                    
                if new_val: self.config.set('base_url', new_val)                                                                             
                self.update_headers()                                                                                                        
                                                                                                                                             
            elif choice == '2':                                                                                                              
                print("Common providers: Vidcloud, UpCloud")                                                                                 
                new_val = input("Enter Provider Name: ").strip()                                                                             
                if new_val: self.config.set('provider', new_val)                                                                             
                                                                                                                                             
            elif choice == '3':                                                                                                              
                print("Options: Best, 1080, 720, 480, 360")                                                                                  
                new_val = input("Enter Max Quality: ").strip()                                                                               
                if new_val in ['Best', '1080', '720', '480', '360']:                                                                         
                    self.config.set('quality', new_val)                                                                                      
                else:                                                                                                                        
                    self.notify("Invalid quality. Using Best.", "Error")                                                                     
                    self.config.set('quality', 'Best')                                                                                       
                                                                                                                                             
            elif choice == '4':                                                                                                              
                new_val = input("Enter Subtitle Language (e.g., 'eng'): ").strip()                                                           
                if new_val: self.config.set('sub_language', new_val)                                                                         
                                                                                                                                             
            elif choice == '5':                                                                                                              
                self.config.set('autoplay', not c['autoplay'])                                                                               
                                                                                                                                             
            elif choice == '6':                                                                                                              
                new_val = input("MPV Options (e.g., --fs): ").strip()                                                                        
                self.config.set('mpv_options', new_val)                                                                                      
                                                                                                                                             
    # --- HLS Quality Parser ---                                                                                                             
                                                                                                                                             
    def enforce_quality(self, master_url, target_quality):                                                                                   
        """                                                                                                                                  
        Parses the master playlist and selects the stream closest to target_quality                                                          
        without exceeding it.                                                                                                                
        """                                                                                                                                  
        if target_quality == "Best":                                                                                                         
            return master_url                                                                                                                
                                                                                                                                             
        try:                                                                                                                                 
            target_height = int(target_quality)                                                                                              
            response = self.session.get(master_url, timeout=10)                                                                              
            if response.status_code != 200: return master_url                                                                                
                                                                                                                                             
            lines = response.text.splitlines()                                                                                               
            best_url = None                                                                                                                  
            best_diff = float('inf')                                                                                                         
            highest_found = 0                                                                                                                
                                                                                                                                             
            # Simple M3U8 parser                                                                                                             
            for i, line in enumerate(lines):                                                                                                 
                if line.startswith("#EXT-X-STREAM-INF"):                                                                                     
                    # Extract resolution                                                                                                     
                    res_match = re.search(r'RESOLUTION=\d+x(\d+)', line)                                                                     
                    if res_match:                                                                                                            
                        height = int(res_match.group(1))                                                                                     
                        # Find the next non-comment line (the URL)                                                                           
                        url_line = None                                                                                                      
                        for k in range(i + 1, len(lines)):                                                                                   
                            if not lines[k].startswith("#") and lines[k].strip():                                                            
                                url_line = lines[k].strip()                                                                                  
                                break                                                                                                        
                                                                                                                                             
                        if url_line:                                                                                                         
                            # Logic: Find the highest quality that is <= target                                                              
                            if height <= target_height:                                                                                      
                                # We want the largest one that fits                                                                          
                                if height > highest_found:                                                                                   
                                    highest_found = height                                                                                   
                                    best_url = url_line                                                                                      
                                                                                                                                             
                            # Fallback: if we haven't found anything <= target, keep track of smallest available                             
                            # (Usually not needed if list is standard, but good safety)                                                      
                                                                                                                                             
            if best_url:                                                                                                                     
                # Handle relative URLs                                                                                                       
                return urljoin(master_url, best_url)                                                                                         
                                                                                                                                             
            return master_url # Fallback to master if parsing fails                                                                          
                                                                                                                                             
        except Exception as e:                                                                                                               
            self.notify(f"Quality parsing error: {e}. Using default.", "Info")                                                               
            return master_url                                                                                                                
                                                                                                                                             
    # --- Scraper Logic ---                                                                                                                  
                                                                                                                                             
    def search(self, query):                                                                                                                 
        self.notify(f"Searching: {Colors.BOLD}{query}{Colors.ENDC}")                                                                         
        search_query = query.replace(' ', '-')                                                                                               
        soup = self.get_soup(f"/search/{search_query}")                                                                                      
                                                                                                                                             
        if not soup: return []                                                                                                               
                                                                                                                                             
        results = []                                                                                                                         
        for item in soup.find_all('div', class_='flw-item'):                                                                                 
            try:                                                                                                                             
                link = item.find('a', href=True)                                                                                             
                title_elem = link.get('title') if link else None                                                                             
                if not link or not title_elem: continue                                                                                      
                                                                                                                                             
                href = link['href']                                                                                                          
                media_type = 'TV' if '/tv/' in href else 'Movie'                                                                             
                                                                                                                                             
                media_id = re.search(r'-(\d+)$', href)                                                                                       
                media_id = media_id.group(1) if media_id else None                                                                           
                                                                                                                                             
                year_elem = item.find('span', class_='fdi-item')                                                                             
                year = year_elem.text if year_elem else 'N/A'                                                                                
                                                                                                                                             
                if media_id:                                                                                                                 
                    results.append({'title': title_elem, 'id': media_id, 'type': media_type, 'year': year})                                  
            except Exception: continue                                                                                                       
        return results                                                                                                                       
                                                                                                                                             
    def select_from_list(self, items, prompt="Select"):                                                                                      
        if not items: return None                                                                                                            
        print(f"\n{Colors.HEADER}{prompt}:{Colors.ENDC}")                                                                                    
        for idx, item in enumerate(items, 1):                                                                                                
            if isinstance(item, dict):                                                                                                       
                display = f"{Colors.BOLD}{item.get('title')}{Colors.ENDC} ({item.get('type')}) [{item.get('year')}]"                         
            else:                                                                                                                            
                display = str(item)                                                                                                          
            print(f"  {Colors.GREEN}{idx}.{Colors.ENDC} {display}")                                                                          
        print(f"  {Colors.FAIL}b. Back{Colors.ENDC}")                                                                                        
                                                                                                                                             
        while True:                                                                                                                          
            try:                                                                                                                             
                choice = input(f"\n{Colors.CYAN}Number > {Colors.ENDC}").strip().lower()                                                     
                if choice == 'b': return None                                                                                                
                idx = int(choice) - 1                                                                                                        
                if 0 <= idx < len(items): return items[idx]                                                                                  
            except ValueError: pass                                                                                                          
                                                                                                                                             
    def get_seasons(self, media_id):                                                                                                         
        soup = self.get_soup(f"/ajax/v2/tv/seasons/{media_id}")                                                                              
        if not soup: return []                                                                                                               
        seasons = []                                                                                                                         
        for link in soup.find_all('a', href=True):                                                                                           
            sid = re.search(r'-(\d+)$', link['href'])                                                                                        
            if sid: seasons.append({'title': link.text.strip(), 'id': sid.group(1)})                                                         
        return seasons                                                                                                                       
                                                                                                                                             
    def get_episodes(self, season_id):                                                                                                       
        soup = self.get_soup(f"/ajax/v2/season/episodes/{season_id}")                                                                        
        if not soup: return []                                                                                                               
        episodes = []                                                                                                                        
        for item in soup.find_all(class_='nav-item'):                                                                                        
            episodes.append({'title': item.get('title', '').strip(), 'data_id': item.get('data-id')})                                        
        return episodes                                                                                                                      
                                                                                                                                             
    def get_source_id(self, episode_data_id):                                                                                                
        soup = self.get_soup(f"/ajax/v2/episode/servers/{episode_data_id}")                                                                  
        if not soup: return None                                                                                                             
        preferred = self.config.get("provider").lower()                                                                                      
        for item in soup.find_all(class_='nav-item'):                                                                                        
            if preferred in item.get('title', '').lower():                                                                                   
                return item.get('data-id')                                                                                                   
        first = soup.find(class_='nav-item')                                                                                                 
        if first: return first.get('data-id')                                                                                                
        return None                                                                                                                          
                                                                                                                                             
    def get_movie_id(self, media_id):                                                                                                        
        soup = self.get_soup(f"/ajax/movie/episodes/{media_id}")                                                                             
        if not soup: return None                                                                                                             
        preferred = self.config.get("provider").lower()                                                                                      
        link = soup.find('a', href=True, title=re.compile(preferred, re.I))                                                                  
        if not link: link = soup.find('a', href=True)                                                                                        
        if link:                                                                                                                             
            match = re.search(r'\.(\d+)$', link['href'])                                                                                     
            return match.group(1) if match else None                                                                                         
        return None                                                                                                                          
                                                                                                                                             
    def resolve_stream(self, source_id):                                                                                                     
        # 1. Get Embed URL                                                                                                                   
        try:                                                                                                                                 
            url = f"{self.config.get('base_url')}/ajax/episode/sources/{source_id}"                                                          
            resp = self.session.get(url, timeout=10).json()                                                                                  
            embed_link = resp.get('link', '')                                                                                                
        except Exception: return None, None                                                                                                  
                                                                                                                                             
        if not embed_link: return None, None                                                                                                 
                                                                                                                                             
        # 2. Decrypt                                                                                                                         
        try:                                                                                                                                 
            api_url = f"{self.config.get('api_url')}/?url={embed_link}"                                                                      
            data = self.session.get(api_url, timeout=15).json()                                                                              
        except Exception:                                                                                                                    
            self.notify("Decryption API failed/down.", "Error")                                                                              
            return None, None                                                                                                                
                                                                                                                                             
        # 3. Find m3u8                                                                                                                       
        video_link = next((s['file'] for s in data.get('sources', []) if '.m3u8' in s.get('file', '')), None)                                
                                                                                                                                             
        if video_link:                                                                                                                       
            # 4. Enforce Quality                                                                                                             
            quality_setting = self.config.get("quality")                                                                                     
            if quality_setting != "Best":                                                                                                    
                self.notify(f"Selecting stream for quality: {quality_setting}p...", "Info")                                                  
                video_link = self.enforce_quality(video_link, quality_setting)                                                               
                                                                                                                                             
        # 5. Find Subs                                                                                                                       
        target_lang = self.config.get('sub_language').lower()                                                                                
        subs = [t['file'] for t in data.get('tracks', [])                                                                                    
                if t.get('kind') == 'captions' and target_lang in t.get('label', '').lower()]                                                
                                                                                                                                             
        return video_link, subs                                                                                                              
                                                                                                                                             
    def play(self, url, subs, title):                                                                                                        
        self.notify(f"Playing: {title}", "Success")                                                                                          
        cmd = ["mpv", url, f"--force-media-title={title}"]                                                                                   
        opts = self.config.get("mpv_options").split()                                                                                        
        if opts: cmd.extend(opts)                                                                                                            
        if subs:                                                                                                                             
            for s in subs: cmd.append(f"--sub-file={s}")                                                                                     
        subprocess.run(cmd, stderr=subprocess.DEVNULL)                                                                                       
                                                                                                                                             
    # --- Handlers ---                                                                                                                       
                                                                                                                                             
    def handle_movie(self, media):                                                                                                           
        eid = self.get_movie_id(media['id'])                                                                                                 
        if not eid: return self.notify("Movie source not found", "Error")                                                                    
        link, subs = self.resolve_stream(eid)                                                                                                
        if link: self.play(link, subs, media['title'])                                                                                       
        else: self.notify("Stream resolution failed", "Error")                                                                               
                                                                                                                                             
    def handle_tv(self, media):                                                                                                              
        seasons = self.get_seasons(media['id'])                                                                                              
        season = self.select_from_list(seasons, "Select Season")                                                                             
        if not season: return                                                                                                                
                                                                                                                                             
        episodes = self.get_episodes(season['id'])                                                                                           
        if not episodes: return self.notify("No episodes found", "Error")                                                                    
                                                                                                                                             
        first_ep = self.select_from_list(episodes, "Select Start Episode")                                                                   
        if not first_ep: return                                                                                                              
                                                                                                                                             
        try:                                                                                                                                 
            start_index = next(i for i, v in enumerate(episodes) if v['data_id'] == first_ep['data_id'])                                     
        except StopIteration: return                                                                                                         
                                                                                                                                             
        for i in range(start_index, len(episodes)):                                                                                          
            ep = episodes[i]                                                                                                                 
            title = f"{media['title']} - {season['title']} - {ep['title']}"                                                                  
                                                                                                                                             
            self.notify(f"Loading: {title}...", "Info")                                                                                      
            sid = self.get_source_id(ep['data_id'])                                                                                          
            if not sid:                                                                                                                      
                self.notify("Server ID not found", "Error")                                                                                  
                break                                                                                                                        
                                                                                                                                             
            link, subs = self.resolve_stream(sid)                                                                                            
            if link:                                                                                                                         
                self.play(link, subs, title)                                                                                                 
            else:                                                                                                                            
                self.notify("Stream not found", "Error")                                                                                     
                                                                                                                                             
            if self.config.get("autoplay"):                                                                                                  
                if i + 1 < len(episodes):                                                                                                    
                    print(f"\n{Colors.GREEN}Autoplaying next in 3s... (Ctrl+C to cancel){Colors.ENDC}")                                      
                    try:                                                                                                                     
                        subprocess.run(["sleep", "3"])                                                                                       
                    except KeyboardInterrupt:                                                                                                
                        break                                                                                                                
                else:                                                                                                                        
                    self.notify("Season finished.", "Info")                                                                                  
                    break                                                                                                                    
            else:                                                                                                                            
                if i + 1 < len(episodes):                                                                                                    
                    choice = input(f"\n{Colors.CYAN}Play next? [Y/n]: {Colors.ENDC}").strip().lower()                                        
                    if choice == 'n': break                                                                                                  
                else: break                                                                                                                  
                                                                                                                                             
    def run(self):                                                                                                                           
        print(f"\n{Colors.HEADER} Stream Movie{Colors.ENDC}")                                                                                
        while True:                                                                                                                          
            try:                                                                                                                             
                q = input(f"\n{Colors.BLUE}Search/Command ('s' settings, 'q' quit): {Colors.ENDC}").strip()                                  
                if q.lower() in ['q', 'exit']: break                                                                                         
                if q.lower() in ['s', 'settings']:                                                                                           
                    self.settings_menu()                                                                                                     
                    continue                                                                                                                 
                if not q: continue                                                                                                           
                                                                                                                                             
                results = self.search(q)                                                                                                     
                if not results:                                                                                                              
                    self.notify("No results found", "Info")                                                                                  
                    continue                                                                                                                 
                                                                                                                                             
                media = self.select_from_list(results, "Select Media")                                                                       
                if not media: continue                                                                                                       
                                                                                                                                             
                if media['type'] == 'Movie': self.handle_movie(media)                                                                        
                else: self.handle_tv(media)                                                                                                  
            except KeyboardInterrupt:                                                                                                        
                print("\nStopped.")                                                                                                          
                break                                                                                                                        
            except Exception as e:                                                                                                           
                self.notify(f"Error: {e}", "Error")                                                                                          
                                                                                                                                             
if __name__ == "__main__":                                                                                                                   
    check_dependencies()                                                                                                                     
    StreamApp().run()                                                                                                                       
