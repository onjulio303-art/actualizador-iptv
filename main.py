import requests
from flask import Flask, jsonify
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# Servidor objetivo actual
IP_SERVIDOR = "http://45.232.210.1:18000"
RUTAS_A_PROBAR = []

# LISTAS DE CARACTERES: Definimos las letras y números más usados en Astra
letras_frecuentes = ['a', 'b', 'c', 'd', 'e', 's', 'k', 'f', 'x']
numeros_frecuentes = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

# GENERADOR COMBINATORIO: Crea mezclas automáticas basadas en tus formatos
# Tipo 1: Letra + Número + Número + Letra (Ej: a07b, b12s, c04k)
for l1 in letras_frecuentes[:4]:  # a, b, c, d
    for n1 in numeros_frecuentes:
        for n2 in numeros_frecuentes:
            for l2 in letras_frecuentes:
                RUTAS_A_PROBAR.append(f"play/{l1}{n1}{n2}{l2}")
                RUTAS_A_PROBAR.append(f"play/{l1}{n1}{n2}{l2}/index.m3u8")

# Tipo 2: Letra + Letra + Número + Letra/Número (Ej: ab1s, ch01, ax2b)
for l1 in letras_frecuentes[:3]:
    for l2 in letras_frecuentes[:3]:
        for n1 in numeros_frecuentes:
            for ultimo in ['0', '1', '2', '3', 's', 'b', 'k', 'f']:
                RUTAS_A_PROBAR.append(f"play/{l1}{l2}{n1}{ultimo}")

# Eliminamos duplicados por seguridad para no sobrecargar el servidor
RUTAS_A_PROBAR = list(set(RUTAS_A_PROBAR))

def verificar_url(ruta):
    url_prueba = f"{IP_SERVIDOR}/{ruta}"
    try:
        # Petición ultra ligera HEAD de 0.7 segundos para barrer masivamente en Render
        respuesta = requests.head(url_prueba, timeout=0.7)
        if respuesta.status_code == 200:
            return {"codigo_detectado": ruta, "url_iptv": url_prueba}
    except:
        pass
    return None

@app.route('/')
def inicio():
    return "Rastreador Astra Alfanumérico (Letras y Números) Activo. Visita /escanear", 200

@app.route('/escanear')
def escanear_servidor():
    canales_encontrados = []
    
    # Subimos a 45 hilos en paralelo para procesar la ráfaga de combinaciones en segundos
    with ThreadPoolExecutor(max_workers=45) as executor:
        resultados = executor.map(verificar_url, RUTAS_A_PROBAR)
        for res in resultados:
            if res is not None:
                canales_encontrados.append(res)
                
    return jsonify({
        "servidor_analizado": IP_SERVIDOR,
        "total_combinaciones_probadas": len(RUTAS_A_PROBAR),
        "total_descubiertos": len(canales_encontrados),
        "canales_activos": canales_encontrados
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
