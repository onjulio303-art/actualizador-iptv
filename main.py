import requests
from flask import Flask, jsonify

app = Flask(__name__)

IP_SERVIDOR = "http://138.121.15.230:9002"

# Lista ampliada con los canales más buscados en Latinoamérica
CANALES_A_ESCANEAR = [
    "CITY-TV", "CITYTV", "CARACOL", "CARACOL-TV", "RCN", "RCN-TV", "CANAL-1",
    "WIN", "WIN-SPORTS", "WIN-SPORTS-PREMIUM", "WIN-PREMIUM",
    "DSPORTS", "DSPORTS-2", "DSPORTS-PLUS", "DIRECTV-SPORTS", "DIRECTV",
    "ESPN", "ESPN-1", "ESPN-2", "ESPN-3", "ESPN-4", "ESPN-PREMIUM", 
    "FOX-SPORTS", "FOX-SPORTS-1", "FOX-SPORTS-2", "FOX-SPORTS-3", 
    "TNT-SPORTS", "TYC-SPORTS", "GOL-CARACOL", "D-SPORTS",
    "TELEANTIOQUIA", "TELEPACIFICO", "TELECARIBE", "CINEMAX",
    "SPACE", "WARNER", "TNT", "HBO", "AXN", "DISNEY", "NICKELODEON"
]

@app.route('/')
def inicio():
    return "Rastreador Flussonic Activo. Visita /escanear para ver los canales descubiertos.", 200

@app.route('/escanear')
def escanear_servidor():
    canales_encontrados = []
    
    # Probamos cada canal con la estructura exacta: /CANAL/index.m3u8
    for canal in CANALES_A_ESCANEAR:
        url_prueba = f"{IP_SERVIDOR}/{canal}/index.m3u8"
        try:
            # Hacemos una petición ligera HEAD para no consumir ancho de banda
            respuesta = requests.head(url_prueba, timeout=2)
            if respuesta.status_code == 200:
                canales_encontrados.append({
                    "canal": canal,
                    "url": url_prueba,
                    "estado": "Online 🟢"
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
