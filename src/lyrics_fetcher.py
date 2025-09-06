import requests
from bs4 import BeautifulSoup
import re
from typing import Optional
import time
from urllib.parse import quote


class LyricsFetcher:
    """Fetches song lyrics from online sources."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def fetch_lyrics(self, artist: str, song: str) -> Optional[str]:
        """Fetches song lyrics using multiple sources."""
        # Try different sources
        sources = [
            self._fetch_from_azlyrics,
            self._fetch_from_genius,
            self._fetch_from_letras
        ]
        
        for source in sources:
            try:
                lyrics = source(artist, song)
                if lyrics and len(lyrics.strip()) > 50:  # Check if lyrics have sufficient content
                    return self._clean_lyrics(lyrics)
                time.sleep(1)  # Respect rate limiting
            except Exception as e:
                print(f"Error fetching lyrics from {source.__name__}: {e}")
                continue
        
        return None
    
    def _fetch_from_azlyrics(self, artist: str, song: str) -> Optional[str]:
        """Fetches lyrics from AZLyrics."""
        # Clean and format names for URL
        artist_clean = re.sub(r'[^a-zA-Z0-9]', '', artist.lower())
        song_clean = re.sub(r'[^a-zA-Z0-9]', '', song.lower())
        
        url = f"https://www.azlyrics.com/lyrics/{artist_clean}/{song_clean}.html"
        
        response = self.session.get(url, timeout=10)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # AZLyrics uses divs without specific class for lyrics
        lyrics_divs = soup.find_all('div', class_=False, id=False)
        for div in lyrics_divs:
            if div.get_text().strip() and len(div.get_text().strip()) > 100:
                # Check if it looks like lyrics (has line breaks)
                text = div.get_text().strip()
                if '\n' in text or '<br>' in str(div):
                    return text
        
        return None
    
    def _fetch_from_genius(self, artist: str, song: str) -> Optional[str]:
        """Fetches lyrics from Genius (simplified method via web scraping)."""
        # Search first using Genius search API
        search_url = "https://genius.com/api/search/multi"
        params = {
            'per_page': 5,
            'q': f"{artist} {song}"
        }
        
        response = self.session.get(search_url, params=params, timeout=10)
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        # Search for the song in results
        for section in data.get('response', {}).get('sections', []):
            for hit in section.get('hits', []):
                if hit.get('type') == 'song':
                    song_url = hit.get('result', {}).get('url')
                    if song_url:
                        return self._fetch_genius_lyrics_from_url(song_url)
        
        return None
    
    def _fetch_genius_lyrics_from_url(self, url: str) -> Optional[str]:
        """Extracts lyrics from a specific Genius page."""
        response = self.session.get(url, timeout=10)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Genius uses different selectors for lyrics
        lyrics_containers = [
            soup.find('div', {'data-lyrics-container': 'true'}),
            soup.find('div', class_='lyrics'),
            soup.find('div', class_='Lyrics__Container-sc-1ynbvzw-6')
        ]
        
        for container in lyrics_containers:
            if container:
                # Remove unnecessary elements
                for elem in container.find_all(['script', 'style', 'a']):
                    elem.decompose()
                
                text = container.get_text(separator='\n').strip()
                if len(text) > 50:
                    return text
        
        return None
    
    def _fetch_from_letras(self, artist: str, song: str) -> Optional[str]:
        """Fetches lyrics from Letras.mus.br."""
        # Format for Letras.mus.br URL
        artist_url = quote(artist.lower().replace(' ', '-'))
        song_url = quote(song.lower().replace(' ', '-'))
        
        url = f"https://www.letras.mus.br/{artist_url}/{song_url}/"
        
        response = self.session.get(url, timeout=10)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Letras.mus.br uses div with specific class
        lyrics_div = soup.find('div', class_='cnt-letra')
        if not lyrics_div:
            lyrics_div = soup.find('div', class_='letra-cnt')
        
        if lyrics_div:
            # Remove unnecessary elements
            for elem in lyrics_div.find_all(['script', 'style']):
                elem.decompose()
            
            text = lyrics_div.get_text(separator='\n').strip()
            if len(text) > 50:
                return text
        
        return None
    
    def _clean_lyrics(self, lyrics: str) -> str:
        """Cleans and formats song lyrics."""
        if not lyrics:
            return ""
        
        # Remove special characters and clean text
        lyrics = re.sub(r'\[.*?\]', '', lyrics)  # Remove [Verse], [Chorus], etc.
        lyrics = re.sub(r'\(.*?\)', '', lyrics)  # Remove (repetitions), etc.
        lyrics = re.sub(r'\n\s*\n', '\n\n', lyrics)  # Normalize line breaks
        lyrics = re.sub(r'^\s+|\s+$', '', lyrics, flags=re.MULTILINE)  # Remove extra spaces
        
        # Remove very short lines (probably not lyrics)
        lines = lyrics.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if len(line) > 2 and not line.isdigit():  # Remove line numbers
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def close(self):
        """Closes the requests session."""
        self.session.close()