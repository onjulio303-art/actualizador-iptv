import requests
from flask import Flask, jsonify
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

IP_SERVIDOR = "http://38.226.210.46:8000"
RUTAS_A_PROBAR = []

# GENERADOR INTELIGENTE: Creamos las combinaciones basadas en tus ejemplos (a07b, a0ab)
# Patrón: una letra inicial ('a' o 'b'), un número/letra, un número/letra, y una letra final ('b', 'f', 'k', 'c', etc.)
letras_iniciales = ['a', 'b']
caracteres_medio = ['0', '1', '2', '3', 'a', 'b', 'c', 'd', 'e']
letras_finales = ['b', 'c', 'f', 'k', 'd', 'a', 'x']

# Generamos mezclas rápidas basadas en el patrón real de Astra
for inicial in letras_iniciales:
    for medio1 in caracteres_medio:
        for medio2 in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b']:
            for final in letras_finales:
                codigo = f"{inicial}{medio1}{medio2}{final}"
                RUTAS_A_PROBAR.append(f"play/{codigo}")

def verificar_url(ruta):
    url_prueba = f"{IP_SERVIDOR}/{ruta}"
    try:
        # Petición ultra ligera HEAD de 0.8 segundos
        respuesta = requests.head(url_prueba, timeout=0.8)
        if respuesta.status_code == 200:
            return {"codigo_detectado": ruta.split('/')[-1], "url_iptv": url_prueba}
    except:
        pass
    return None

@app.route('/')
def inicio():
    return "Rastreador Astra Alfanumérico Activo. Visita /escanear", 200

@app.route('/escanear')
def escanear_servidor():
    canales_encontrados = []
    
    # Subimos a 40 hilos en paralelo para procesar las combinaciones en menos de 4 segundos
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
