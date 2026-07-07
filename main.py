import re
import requests
import traceback
from bs4 import BeautifulSoup
from flask import Flask, redirect

app = Flask(__name__)

URL_FUENTE = "https://tvlibre-online.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://tvlibre-online.com"
}

def raspar_token():
    # Iniciamos sesión simulada para mantener cookies activas
    sesion = requests.Session()
    
    # 1. Petición base para cookies
    try:
        sesion.get("https://tvlibre-online.com", headers=HEADERS, timeout=5)
    except:
        pass

    # 2. Petición a la página de DSports
    respuesta = sesion.get(URL_FUENTE, headers=HEADERS, timeout=10)
    texto_acumulado = respuesta.text
    
    # 3. Buscar enlaces internos (iframes) del reproductor
    soup = BeautifulSoup(respuesta.text, 'html.parser')
    for iframe in soup.find_all('iframe'):
        src = iframe.get('src', '')
        if src:
            if src.startswith('//'):
                src = 'https:' + src
            try:
                resp_iframe = sesion.get(src, headers=HEADERS, timeout=5)
                texto_acumulado += " " + resp_iframe.text
            except:
                continue

    # 4. Expresión regular para extraer la cadena del token
    match = re.search(r'token=([a-zA-Z0-9\-\_\.]+)', texto_acumulado)
    if match:
        token_sucio = match.group(1)
        # Limpieza correcta: Corta el texto en el primer caracter extraño que encuentre
        token_limpio = re.split(r'["\'&\s;?]', token_sucio)[0]
        return token_limpio
        
    return None

@app.route('/')
def inicio():
    return "Servidor IPTV activo y corregido.", 200

@app.route('/dsports.m3u8')
def enlace_dinamico():
    try:
        token_fresco = raspar_token()
        if token_fresco:
            print(f"¡Éxito! Token obtenido: {token_fresco}")
            # Redirige usando el string limpio de manera segura
            return redirect(f"https://fubo18.com{token_fresco}")
        
        return "La pagina fuente cambio su diseno o no entrego un token en este intento.", 200
    except Exception as e:
        # Si algo se rompe, te lo muestra en pantalla en vez de dar Internal Server Error
        return f"Error interno en el script: {str(e)}<br><pre>{traceback.format_exc()}</pre>", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
