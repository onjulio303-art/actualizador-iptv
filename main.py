import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, redirect

app = Flask(__name__)

URL_FUENTE = "https://tvlibre-online.com/en-vivo/dsports/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://tvlibre-online.com/"
}

def raspar_token():
    try:
        # Entra a la web a buscar el token vigente
        sesion = requests.Session()
        respuesta = sesion.get(URL_FUENTE, headers=HEADERS, timeout=10)
        
        # Busca el patrón del token (letras y números largos después de 'token=')
        match = re.search(r'token=([a-f0-9\-]+)', respuesta.text)
        if match:
            return match.group(1)
        return None
    except:
        return None

@app.route('/dsports.m3u8')
def enlace_dinamico():
    token_fresco = raspar_token()
    if token_fresco:
        # Une el token actual al enlace base que me diste
        return redirect(f"https://am91cm5leq.fubo18.com/dsports/mono.m3u8?token={token_fresco}")
    return "Error: No se pudo renovar el token automáticamente", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
