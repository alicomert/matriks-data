#!/usr/bin/env python3
"""
Matriks Data API Client — demonstrates full API access
Requires: pip install urllib3 (stdlib only, no external deps)
"""
import json
import urllib.request
import re
import time

class MatriksDataAPI:
    """Full API client for matriksdata.com"""
    
    BASE = "https://api.matriksdata.com"
    WEB = "https://www.matriksdata.com"
    
    def __init__(self):
        self.jwt = None
        self.disco = None
        
    def get_jwt(self):
        """Get JWT token from website HTML (refreshes on every page load)"""
        req = urllib.request.Request(f"{self.WEB}/website/", 
            headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="replace")
        match = re.findall(r"var\s+password\s*=\s*['\"]([^'\"]+)['\"]", html)
        if match:
            self.jwt = match[0]
            return self.jwt
        raise Exception("JWT token not found in HTML")
    
    def _headers(self):
        if not self.jwt:
            self.get_jwt()
        return {
            "Authorization": f"jwt {self.jwt}",
            "User-Agent": "Mozilla/5.0",
            "Origin": self.WEB,
            "Referer": f"{self.WEB}/",
        }
    
    def _get(self, url):
        req = urllib.request.Request(url, headers=self._headers())
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read())
    
    def get_disco(self):
        """Get API discovery document (277 endpoints)"""
        url = f"{self.BASE}/disco-v2.json?issuer=MATRIKSDATACOM"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        self.disco = json.loads(urllib.request.urlopen(req, timeout=30).read())
        return self.disco
    
    def get_all_symbols(self):
        """Get all 20,388 symbols with full metadata"""
        return self._get(f"{self.BASE}/dumrul/v3/meta/symbols?allSymbols=true")
    
    def get_symbol(self, symbol_code):
        """Get single symbol metadata"""
        return self._get(f"{self.BASE}/dumrul/v3/meta/symbols?symbolCode={symbol_code}")
    
    def get_bar_data(self, symbol, period="1day", start="2024-01-01", end="2024-12-31"):
        """Get OHLCV bar data
        Periods: 1min, 5min, 1hour, 1day
        """
        url = f"{self.BASE}/dumrul/v1/tick/bar?symbol={symbol}&period={period}&start={start}&end={end}"
        return self._get(url)
    
    def get_news(self, count=50):
        """Get latest news with AI sentiment analysis"""
        return self._get(f"{self.BASE}/dumrul/v2/news/lastN?count={count}")
    
    def search_news(self, query, language="tr", count=10):
        """Search news by keyword"""
        url = f"{self.BASE}/dumrul/v2/news/search?query={query}&language={language}&count={count}&withComment=false"
        return self._get(url)
    
    def get_market_symbol_list(self):
        """Get market symbol list"""
        return self._get(f"{self.BASE}/dumrul/v2/market-symbol-list?inline=false")
    
    def get_mqtt_config(self):
        """Get MQTT topic configuration for real-time streaming"""
        return self._get(f"{self.BASE}/dumrul/v2/topach")
    
    def query_codi(self, query, topK=10, app=1):
        """Query Codi AI assistant (RAG system)
        app=1: MatriksIQ, app=2: MatriksPrime
        """
        payload = json.dumps({"query": query, "topK": topK, "applicationFilter": app}).encode()
        req = urllib.request.Request(f"{self.WEB}/codi/Search/Search", data=payload, headers={
            "Content-Type": "application/json",
            "Origin": self.WEB,
            "Referer": f"{self.WEB}/codi/",
            "User-Agent": "Mozilla/5.0"
        })
        return json.loads(urllib.request.urlopen(req, timeout=60).read())
    
    def get_news_meta(self):
        """Get news sources and categories"""
        req = urllib.request.Request(f"{self.BASE}/news-meta.json",
            headers={"User-Agent": "Mozilla/5.0"})
        return json.loads(urllib.request.urlopen(req, timeout=15).read())


# === Usage Examples ===
if __name__ == "__main__":
    api = MatriksDataAPI()
    
    # Get JWT token
    print(f"JWT: {api.get_jwt()[:50]}...")
    
    # Get all symbols
    symbols = api.get_all_symbols()
    print(f"Total symbols: {len(symbols)}")
    
    # Get BIST stock bars
    garan = api.get_bar_data("GARAN", "1day", "2024-06-01", "2024-07-09")
    print(f"GARAN bars: {len(garan)}")
    if garan:
        last = garan[-1]
        print(f"  Last: date={last['date']} close={last['close']} volume={last['volume']}")
    
    # Get XU100 index
    xu100 = api.get_bar_data("XU100", "1day", "2024-06-01", "2024-07-09")
    if xu100:
        print(f"XU100 last close: {xu100[-1]['close']}")
    
    # Get latest news with AI sentiment
    news = api.get_news(10)
    for n in news[:3]:
        ai = n.get("aiAnalysis", {})
        print(f"  [{n['date'][:19]}] {n['headline'][:60]}")
        print(f"    AI: {ai.get('sentiment', '')} importance={ai.get('importance', '')}")
    
    # Query Codi AI
    resp = api.query_codi("MatriksIQ nedir?")
    print(f"Codi: {resp.get('llmResponse', '')[:100]}")
    
    # MQTT config
    mqtt = api.get_mqtt_config()
    print(f"MQTT topics: {list(mqtt.get('mqtt', {}).keys())}")
