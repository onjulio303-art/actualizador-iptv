import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, redirect

app = Flask(__name__)

URL_FUENTE = "https://tvlibre-online.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://tvlibre-online.com"
}

def raspar_token():
    try:
        sesion = requests.Session()
        # 1. Obtener la página principal
        respuesta = sesion.get(URL_FUENTE, headers=HEADERS, timeout=10)
        texto_acumulado = respuesta.text
        
        # 2. Buscar iframes y sumar su contenido de forma segura
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

        # 3. Buscar el token con una expresión limpia y robusta
        match = re.search(r'token=([a-f0-9A-Za-z\-\_]+)', texto_acumulado)
        if match:
            token_sucio = match.group(1)
            # Limpieza segura para eliminar código HTML sobrante si existiera
            token_limpio = re.split(r'["\'&\s;]', token_sucio)[0]
            return token_limpio
            
        return None
    except Exception as e:
        print(f"Error al raspar token: {e}")
        return None

@app.route('/')
def inicio():
    return "Servidor IPTV activo.", 200

@app.route('/dsports.m3u8')
def enlace_dinamico():
    token_fresco = raspar_token()
    if token_fresco:
        print(f"Token obtenido de forma exitosa: {token_fresco}")
        return redirect(f"https://fubo18.com{token_fresco}")
    
    # Si la web no da el token, devolvemos un mensaje limpio en vez de romper el servidor
    return "La pagina fuente no entrego un token valido en este intento.", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
