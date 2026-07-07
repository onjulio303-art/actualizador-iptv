import requests
from flask import Flask, jsonify
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

IP_SERVIDOR = "http://8.243.126.131:8000"

# Combinamos el patrón real descubierto con las variaciones más probables
RUTAS_ASTRA = [
    "play/a04k/index.m3u8", "play/a04k",
    "play/a01k/index.m3u8", "play/a02k/index.m3u8", "play/a03k/index.m3u8",
    "play/a1/index.m3u8", "play/a2/index.m3u8", "play/a3/index.m3u8",
    "play/ch01/index.m3u8", "play/ch02/index.m3u8", "play/ch03/index.m3u8"
]

# Añadimos un barrido rápido del a01 al a50 agregándole el '/index.m3u8' que usa el admin
for i in range(1, 51):
    RUTAS_ASTRA.append(f"play/a{i:02d}/index.m3u8")
    RUTAS_ASTRA.append(f"play/a{i}/index.m3u8")
    RUTAS_ASTRA.append(f"play/ch{i}/index.m3u8")

def verificar_url(ruta):
    url_prueba = f"{IP_SERVIDOR}/{ruta}"
    try:
        # Petición ultra ligera de 1 segundo para evitar caídas en Render
        respuesta = requests.head(url_prueba, timeout=1.0)
        if respuesta.status_code == 200:
            return {"canal_encontrado": ruta, "url_iptv": url_prueba}
    except:
        pass
    return None

@app.route('/')
def inicio():
    return "Escáner Astra Descubierto Activo. Visita /escanear", 200

@app.route('/escanear')
def escanear_servidor():
    canales_encontrados = []
    
    # 35 hilos en paralelo para barrer las 150 rutas en 2 segundos
    with ThreadPoolExecutor(max_workers=35) as executor:
        resultados = executor.map(verificar_url, RUTAS_ASTRA)
        for res in resultados:
            if res is not None:
                canales_encontrados.append(res)
                
    return jsonify({
        "total_descubiertos": len(canales_encontrados),
        "canales_activos": canales_encontrados
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
