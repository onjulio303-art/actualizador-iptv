import requests
from flask import Flask, jsonify
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# Configuración del nuevo servidor objetivo
IP_SERVIDOR = "http://45.232.210.1:18000"
RUTAS_A_PROBAR = []

# 1. Agregamos las variaciones alfanuméricas detectadas en esta red (a01s, a07s, a04k, etc.)
letras_finales = ['s', 'k', 'b', 'f', 'c']
for i in range(1, 31):
    for letra in letras_finales:
        RUTAS_A_PROBAR.append(f"play/a{i:02d}{letra}/index.m3u8")
        RUTAS_A_PROBAR.append(f"play/a{i}{letra}/index.m3u8")

# 2. Agregamos también los rangos numéricos limpios por si el puerto 18000 los simplifica
for i in range(1, 61):
    RUTAS_A_PROBAR.append(f"play/a{i:02d}/index.m3u8")
    RUTAS_A_PROBAR.append(f"play/ch{i:02d}/index.m3u8")
    RUTAS_A_PROBAR.append(f"play/{i}")

def verificar_url(ruta):
    url_prueba = f"{IP_SERVIDOR}/{ruta}"
    try:
        # Petición ultra ligera de 0.8 segundos para procesar todo sin colapsar Render
        respuesta = requests.head(url_prueba, timeout=0.8)
        if respuesta.status_code == 200:
            return {"codigo_detectado": ruta, "url_iptv": url_prueba}
    except:
        pass
    return None

@app.route('/')
def inicio():
    return "Rastreador Avanzado para Puerto 18000 Activo. Visita /escanear", 200

@app.route('/escanear')
def escanear_servidor():
    canales_encontrados = []
    
    # 40 hilos en simultáneo para barrer más de 350 combinaciones en 3 segundos
    with ThreadPoolExecutor(max_workers=40) as executor:
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
