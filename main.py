import requests
from flask import Flask, redirect, jsonify

app = Flask(__name__)

# Servidor Astra objetivo
IP_SERVIDOR = "http://138.121.15.230:9002"

# Rutas maestras por defecto que Astra usa para exportar todos sus canales juntos
RUTAS_MAESTRAS = [
    "playlist.m3u8",
    "playlist.m3u",
    "api/playlist.m3u8",
    "play/playlist.m3u8"
]

@app.route('/')
def inicio():
    return "Extractor de listas Astra Activo. Visita /escanear", 200

@app.route('/escanear')
def descargar_lista_maestra():
    # El script intenta descargar la lista completa de canales en un solo paso
    for ruta in RUTAS_MAESTRAS:
        url_archivo = f"{IP_SERVIDOR}/{ruta}"
        try:
            # Hacemos una petición rápida para ver si el archivo existe
            respuesta = requests.get(url_archivo, timeout=5)
            if respuesta.status_code == 200 and ("#EXTM3U" in respuesta.text or "EXTINF" in respuesta.text):
                print(f"¡Éxito! Lista maestra encontrada en: {url_archivo}")
                # Redirige de inmediato a tu reproductor con todos los canales cargados
                return redirect(url_archivo)
        except:
            continue
            
    # Si el administrador tiene protegida la lista general con contraseña
    return jsonify({
        "estado": "Error",
        "mensaje": "El servidor Astra tiene bloqueada la exportacion publica de la lista general. Requiere login administrativo.",
        "servidor": IP_SERVIDOR
    }), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
