import requests
from flask import Flask, jsonify
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# Nueva dirección IP del servidor Astra a analizar
IP_SERVIDOR = "http://38.226.210.46:8000"

# Estructuramos las rutas de canales más comunes en servidores Astra latinoamericanos
RUTAS_A_PROBAR = []

# 1. Rangos numéricos clásicos de Astra con prefijos comunes (ej: play/c01, play/ch01, play/1)
for i in range(1, 61):
    RUTAS_A_PROBAR.append(f"play/c{i:02d}")
    RUTAS_A_PROBAR.append(f"play/ch{i:02d}")
    RUTAS_A_PROBAR.append(f"play/a{i:02d}")
    RUTAS_A_PROBAR.append(f"play/{i}")
    RUTAS_A_PROBAR.append(f"play/{i:02d}")

# 2. Formatos con nombres de canales conocidos en minúsculas y mayúsculas
CANALES_TEXTO = ["caracol", "rcn", "win", "winsports", "dsports", "espn", "espn2", "foxsports", "tyc"]
for canal in CANALES_TEXTO:
    RUTAS_A_PROBAR.append(f"play/{canal}")
    RUTAS_A_PROBAR.append(f"play/{canal.upper()}")

def verificar_url(ruta):
    url_prueba = f"{IP_SERVIDOR}/{ruta}"
    try:
        # Petición ultra ligera de 1 segundo para agilizar el barrido en paralelo
        respuesta = requests.head(url_prueba, timeout=1.0)
        if respuesta.status_code == 200:
            return {"ruta_descubierta": ruta, "url_iptv": url_prueba}
    except:
        pass
    return None

@app.route('/')
def inicio():
    return "Rastreador Astra Activo para la nueva IP. Visita /escanear", 200

@app.route('/escanear')
def escanear_servidor():
    canales_encontrados = []
    
    # Ejecutamos 35 hilos en simultáneo para barrer más de 300 rutas en solo 3 segundos
    with ThreadPoolExecutor(max_workers=35) as executor:
        resultados = executor.map(verificar_url, RUTAS_A_PROBAR)
        for res in resultados:
            if res is not None:
                canales_encontrados.append(res)
                
    return jsonify({
        "servidor_analizado": IP_SERVIDOR,
        "total_descubiertos": len(canales_encontrados),
        "canales_activos": canales_encontrados
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
