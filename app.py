from flask import Flask, request, jsonify, render_template_string
import datetime

app = Flask(__name__)

# REGISTRO DE PACIENTES
directorio_pacientes = {
    "80:65:99:2B:25:94": "Paciente 1 - [TU NOMBRE]",
}

estado_actual = {}

# HTML DASHBOARD
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>🏥 Monitor Central</title>
    <meta http-equiv="refresh" content="2"> 
    <style>
        body { font-family: sans-serif; background: #eaeff1; padding: 20px; }
        .grid { display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; }
        .card { 
            background: white; width: 300px; padding: 20px; border-radius: 15px; 
            box-shadow: 0 4px 10px rgba(0,0,0,0.1); 
        }
        .header { font-size: 1.2em; font-weight: bold; padding-bottom: 10px; border-bottom: 2px solid #eee; }
        .row { display: flex; justify-content: space-between; margin: 10px 0; font-size: 1.1em; }
        .status { text-align: center; padding: 8px; border-radius: 5px; color: white; font-weight: bold; margin-top: 15px; }
        
        /* ESTADOS */
        .gris { border-top: 8px solid #95a5a6; }
        .verde { border-top: 8px solid #2ecc71; }
        .rojo { border-top: 8px solid #e74c3c; background-color: #fdebd0; }
        
        .bg-gris { background-color: #95a5a6; }
        .bg-verde { background-color: #2ecc71; }
        .bg-rojo { background-color: #e74c3c; }
    </style>
</head>
<body>
    <h1 style="text-align:center;">🏥 Monitor de Signos Vitales</h1>
    <div class="grid">
        {% for mac, p in datos.items() %}
        <div class="card {{ p.clase }}">
            <div class="header">{{ p.nombre }}</div>
            <div class="row"><span>🌡️ Temp:</span> <strong>{{ p.temp }} °C</strong></div>
            <div class="row"><span>❤️ Ritmo:</span> <strong>{{ p.ritmo }} BPM</strong></div>
            <div class="row"><span>💧 SpO2:</span> <strong>{{ p.oxigeno }} %</strong></div>
            <div class="status {{ p.bg }}"> {{ p.msg }} </div>
            <div style="text-align:center; font-size:0.8em; color:#888; margin-top:5px;">MAC: {{ mac }}</div>
        </div>
        {% else %}
            <h3>📡 Esperando datos...</h3>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(HTML_TEMPLATE, datos=estado_actual)

@app.route('/recibir_datos', methods=['POST'])
def recibir_datos():
    data = request.json
    mac = data.get('mac')
    ritmo = int(data.get('ritmo', 0))
    spo2 = int(data.get('oxigeno', 0))
    temp = float(data.get('temperatura', 0.0))
    
    nombre = directorio_pacientes.get(mac, "Desconocido")
    
    # --- LÓGICA DE ESTADOS ---
    alerta = False
    msg = "💤 STANDBY"
    clase = "gris"
    bg = "bg-gris"

    # ¿Hay lecturas válidas? (Al menos temperatura de piel o pulso)
    if ritmo > 0 or spo2 > 0 or temp > 25.0:
        
        fallos = []
        # Rangos tolerantes para muñeca
        if temp > 37.8: fallos.append("FIEBRE")
        if temp < 33.0: fallos.append("HIPOTERMIA") 
        if ritmo > 120: fallos.append("TAQUICARDIA")
        if ritmo < 50 and ritmo > 0: fallos.append("BRADICARDIA")
        if spo2 < 90 and spo2 > 0: fallos.append("BAJO O2")

        if len(fallos) > 0:
            alerta = True
            msg = "⚠️ " + ", ".join(fallos)
            clase = "rojo"
            bg = "bg-rojo"
        else:
            msg = "✅ ESTABLE"
            clase = "verde"
            bg = "bg-verde"
            
    estado_actual[mac] = {
        "nombre": nombre, "ritmo": ritmo, "oxigeno": spo2, "temp": temp,
        "msg": msg, "clase": clase, "bg": bg
    }
    
    print(f"[{mac}] {msg} | T:{temp}")
    return jsonify({"status": "ok", "alerta_activa": alerta})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)