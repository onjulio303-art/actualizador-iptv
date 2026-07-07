import requests
from flask import Flask, jsonify
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

IP_SERVIDOR = "http://8.243.126.131:8000"

# Lista simplificada y directa con los formatos de Astra más probables
NOMBRES_CANALES = ["CITY-TV", "CITYTV", "CARACOL", "RCN", "WIN", "DSPORTS", "ESPN", "HBO"]
RUTAS_A_PROBAR = []

# Generamos solo las rutas numéricas más utilizadas en Astra para ahorrar memoria
for i in range(1, 31):
    RUTAS_A_PROBAR.append(f"play/a{i:03d}")
    RUTAS_A_PROBAR.append(f"play/ch{i:03d}")
    RUTAS_A_PROBAR.append(f"play/{i}")

for nombre in NOMBRES_CANALES:
    RUTAS_A_PROBAR.append(nombre)
    RUTAS_A_PROBAR.append(nombre.lower())

def verificar_url(ruta):
    url_prueba = f"{IP_SERVIDOR}/{ruta}"
    try:
        # Petición ultra rápida con un tiempo límite estricto de 1 segundo
        respuesta = requests.head(url_prueba, timeout=1.0)
        if respuesta.status_code == 200:
            return {"ruta_descubierta": ruta, "url_directa": url_prueba, "estado": "Emitiendo 🟢"}
    except:
        pass
    return None

@app.route('/')
def inicio():
    return "Rastreador Astra de Alta Velocidad Activo. Visita /escanear", 200

@app.route('/escanear')
def escanear_servidor():
    canales_encontrados = []
    
    # Usamos un ejecutor con 20 hilos en paralelo para revisar todo al mismo tiempo
    with ThreadPoolExecutor(max_workers=20) as executor:
        resultados = executor.map(verificar_url, RUTAS_A_PROBAR)
        
        for res in resultados:
            if res is not None:
                canales_encontrados.append(res)
                
    return jsonify({
        "servidor_analizado": IP_SERVIDOR,
        "total_encontrados": len(canales_encontrados),
        "enlaces_activos": canales_encontrados
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
