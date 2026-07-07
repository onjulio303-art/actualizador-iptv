import requests
from flask import Flask, jsonify
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

IP_SERVIDOR = "http://8.243.126.131:8000"
RUTAS_A_PROBAR = []

# Astra organiza típicamente por rangos de tres dígitos (001 al 150)
for i in range(1, 151):
    RUTAS_A_PROBAR.append(f"play/a{i:03d}")
    RUTAS_A_PROBAR.append(f"play/ch{i:03d}")
    RUTAS_A_PROBAR.append(f"play/{i}")

def verificar_url(ruta):
    url_prueba = f"{IP_SERVIDOR}/{ruta}"
    try:
        # Petición ultraligera
        respuesta = requests.head(url_prueba, timeout=0.8)
        if respuesta.status_code == 200:
            return {"ruta_descubierta": ruta, "url_directa": url_prueba}
    except:
        pass
    return None

@app.route('/')
def inicio():
    return "Escáner Astra Ampliado Activo. Visita /escanear", 200

@app.route('/escanear')
def escanear_servidor():
    canales_encontrados = []
    # Elevamos a 35 hilos en paralelo para procesar los 450 intentos en segundos
    with ThreadPoolExecutor(max_workers=35) as executor:
        resultados = executor.map(verificar_url, RUTAS_A_PROBAR)
        for res in resultados:
            if res is not None:
                canales_encontrados.append(res)
                
    return jsonify({
        "total_descubiertos": len(canales_encontrados),
        "canales": canales_encontrados
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
