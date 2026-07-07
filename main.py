import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, redirect

app = Flask(__name__)

URL_FUENTE = "https://tvlibre-online.com/en-vivo/dsports/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
    "Referer": "https://tvlibre-online.com/"
}

def raspar_token():
    try:
        sesion = requests.Session()
        # 1. Intentamos leer la página principal de TVLibre
        respuesta = sesion.get(URL_FUENTE, headers=HEADERS, timeout=10)
        texto_acumulado = respuesta.text
        
        # 2. Forzamos la búsqueda de cualquier iframe/reproductor escondido dentro de la web
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        iframes = soup.find_all('iframe')
        
        for iframe in iframes:
            src = iframe.get('src', '')
            if src:
                if src.startswith('//'):
                    src = 'https:' + src
                try:
                    # El script entra también de forma invisible al reproductor oculto
                    resp_iframe = sesion.get(src, headers=HEADERS, timeout=5)
                    texto_acumulado += " " + resp_iframe.text
                except:
                    continue

        # 3. Expresión regular ultra-flexible que atrapa cualquier formato de token de fubo
        # Busca patrones tipo token=hexadecimal, token=letras-numeros-guiones largos, etc.
        match = re.search(r'token=([a-f0-9]{32,45}-[a-zA-Z0-9\-]+)', texto_acumulado)
        if not match:
            match = re.search(r'token=([a-zA-Z0-9\-\_\.]+)', texto_acumulado)
            
        if match:
            token = match.group(1)
            # Limpieza básica por si arrastra caracteres de cierre del código HTML
            token = token.split('"')[0].split("'")[0].split('&')[0].split(';')[0]
            return token
        return None
    except Exception as e:
        print(f"Error interno: {e}")
        return None

@app.route('/')
def inicio():
    return "Servidor IPTV de Render en línea y funcionando.", 200

@app.route('/dsports.m3u8')
def enlace_dinamico():
    token_fresco = raspar_token()
    if token_fresco:
        # Imprime en la consola de Render para verificar que funcionó
        print(f"¡Éxito! Token capturado: {token_fresco}")
        return redirect(f"https://fubo18.com{token_fresco}")
    
    return "Error: No se pudo renovar el token automáticamente. La web fuente pudo haber cambiado su estructura.", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
