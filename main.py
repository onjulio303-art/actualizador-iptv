import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, redirect

app = Flask(__name__)

URL_FUENTE = "https://tvlibre-online.com/en-vivo/dsports/"

# Encabezados de un navegador real para despistar sistemas de seguridad
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Referer": "https://tvlibre-online.com/",
    "Origin": "https://tvlibre-online.com",
    "Connection": "keep-alive"
}

def raspar_token():
    try:
        # Iniciamos sesión para guardar cookies simuladas como si fuéramos un usuario real
        sesion = requests.Session()
        
        # 1. Petición a la home para obtener cookies básicas de validación
        sesion.get("https://tvlibre-online.com/", headers=HEADERS, timeout=8)
        
        # 2. Petición directa a la sección de DSports
        respuesta = sesion.get(URL_FUENTE, headers=HEADERS, timeout=10)
        texto_acumulado = respuesta.text
        
        # 3. Rastreo profundo dentro del código fuente buscando iframes ocultos
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src', '')
            if src:
                if src.startswith('//'):
                    src = 'https:' + src
                try:
                    # El robot entra de forma invisible a las entrañas del reproductor usando la misma sesión
                    resp_iframe = sesion.get(src, headers=HEADERS, timeout=5)
                    texto_acumulado += " " + resp_iframe.text
                except:
                    continue

        # 4. Buscador avanzado: Captura el token con el guion largo y números de timestamp de Fubo
        match = re.search(r'token=([a-f0-9]{32,45}-[a-zA-Z0-9\-]+-\d+-\d+)', texto_acumulado)
        if not match:
            # Buscador secundario flexible si modificaron el orden del string
            match = re.search(r'token=([a-zA-Z0-9\-\_\.]{40,120})', texto_acumulado)
            
        if match:
            token_extraido = match.group(1)
            # Limpiamos posibles comillas o caracteres extra de HTML
            token_limpio = re.split(r'["\'&\s;?]', token_extraido)[0]
            return token_limpio
            
        return None
    except Exception as e:
        print(f"Error en el proceso de rastreo: {e}")
        return None

@app.route('/')
def inicio():
    return "Servidor IPTV activo y camuflado.", 200

@app.route('/dsports.m3u8')
def enlace_dinamico():
    token_fresco = raspar_token()
    if token_fresco:
        print(f"¡Éxito total! Token capturado y saltado: {token_fresco}")
        return redirect(f"https://fubo18.com{token_fresco}")
    
    return "La pagina fuente bloqueo el acceso. Intentando de nuevo en el proximo arranque.", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
