import requests
from flask import Flask, jsonify

app = Flask(__name__)

# Nueva IP del servidor Astra proporcionada por el usuario
IP_SERVIDOR = "http://8.243.126.131:8000"

# 1. Lista de nombres de canales comunes en diferentes formatos
NOMBRES_CANALES = [
    "CITY-TV", "CITYTV", "CARACOL", "RCN", "WIN", "WIN-SPORTS", "WIN-PREMIUM",
    "DSPORTS", "DSPORTS-2", "DSPORTS-PLUS", "ESPN", "ESPN-2", "ESPN-3", "ESPN-4",
    "FOX-SPORTS", "TNT-SPORTS", "TYC-SPORTS", "HBO", "TNT", "SPACE"
]

# 2. Generamos combinaciones numéricas típicas de Astra (a001-a030, ch1-ch30)
RUTAS_A_PROBAR = []

# Añadir formatos con prefijos comunes
for i in range(1, 31):
    num_con_ceros = f"{i:03d}"  # Transforma 1 en 001, 2 en 002...
    RUTAS_A_PROBAR.append(f"play/a{num_con_ceros}")
    RUTAS_A_PROBAR.append(f"play/ch{num_con_ceros}")
    RUTAS_A_PROBAR.append(f"play/{i}")
    RUTAS_A_PROBAR.append(f"channel/{i}")

# Añadir las rutas de nombres de canales en minúsculas y mayúsculas
for nombre in NOMBRES_CANALES:
    RUTAS_A_PROBAR.append(nombre)
    RUTAS_A_PROBAR.append(nombre.lower())
    RUTAS_A_PROBAR.append(f"play/{nombre.lower()}")

@app.route('/')
def inicio():
    return "Rastreador Astra Activo. Visita /escanear para iniciar el barrido.", 200

@app.route('/escanear')
def escanear_servidor():
    canales_encontrados = []
    
    # Probamos cada ruta en la estructura del servidor Astra
    for ruta in RUTAS_A_PROBAR:
        url_prueba = f"{IP_SERVIDOR}/{ruta}"
        try:
            # Petición ligera HEAD para comprobar existencia del flujo de video
            respuesta = requests.head(url_prueba, timeout=1.5)
            
            # Astra suele responder con 200 OK si el canal está emitiendo de forma abierta
            if respuesta.status_code == 200:
                canales_encontrados.append({
                    "ruta_descubierta": ruta,
                    "url_directa": url_prueba,
                    "estado": "Emitiendo 🟢"
                })
        except:
            continue
            
    return jsonify({
        "servidor_analizado": IP_SERVIDOR,
        "total_encontrados": len(canales_encontrados),
        "enlaces_activos": canales_encontrados
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
