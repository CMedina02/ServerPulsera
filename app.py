from flask import Flask, request, jsonify, render_template_string
import datetime

app = Flask(__name__)

# --- REGISTRO DE PACIENTES ---
directorio_pacientes = {
    # TU ID REAL:
    "80:65:99:2B:25:94": "Paciente 1 - [TU NOMBRE]",
}

estado_actual = {}

# --- DASHBOARD HTML ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>🏥 Monitor de Albergue</title>
    <meta http-equiv="refresh" content="2"> 
    <style>
        body { font-family: sans-serif; background: #eaeff1; padding: 20px; }
        h1 { text-align: center; color: #2c3e50; }
        .grid { display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; }
        .card { 
            background: white; width: 300px; padding: 20px; border-radius: 15px; 
            box-shadow: 0 4px 10px rgba(0,0,0,0.1); 
        }
        .header { font-size: 1.2em; font-weight: bold; border-bottom: 2px solid #f0f0f0; padding-bottom: 10px; }
        .row { display: flex; justify-content: space-between; margin: 8px 0; font-size: 1.1em; }
        .normal { border-top: 10px solid #2ecc71; }
        .peligro { border-top: 10px solid #e74c3c; background-color: #fdebd0; }
        .status-box { text-align: center; margin-top: 15px; padding: 8px; border-radius: 8px; font-weight: bold; color: white; }
        .ok { background-color: #2ecc71; }
        .error { background-color: #e74c3c; }
    </style>
</head>
<body>
    <h1>🏥 Monitor de Albergue</h1>
    <div class="grid">
        {% for mac, p in datos.items() %}
        <div class="card {% if p.alerta %}peligro{% else %}normal{% endif %}">
            <div class="header">
                {{ p.nombre }}<br><span style="font-size:0.7em; color:#777;">ID: {{ mac }}</span>
            </div>
            <div class="row"><span>🌡️ Temp:</span> <strong>{{ p.temp }} °C</strong></div>
            <div class="row"><span>❤️ Ritmo:</span> <strong>{{ p.ritmo }} BPM</strong></div>
            <div class="row"><span>💧 SpO2:</span> <strong>{{ p.oxigeno }} %</strong></div>
            <div class="status-box {% if p.alerta %}error{% else %}ok{% endif %}">
                {% if p.alerta %}⚠️ ALERTA {% else %}✅ ESTABLE {% endif %}
            </div>
        </div>
        {% else %}
            <p style="text-align:center; margin-top:50px;">📡 Esperando pulseras...</p>
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
    ritmo = data.get('ritmo', 0)
    spo2 = data.get('oxigeno', 0)
    temp = data.get('temperatura', 0.0)
    valido = data.get('valid', False)
    
    nombre = directorio_pacientes.get(mac, "Paciente Nuevo")
    
    alerta = False
    if temp > 38.0 or (temp < 35.0 and temp > 0): alerta = True
    if valido:
        if ritmo > 120 or (ritmo < 45 and ritmo > 0): alerta = True
        if spo2 < 90 and spo2 > 0: alerta = True
        
    estado_actual[mac] = {
        "nombre": nombre, "ritmo": ritmo, "oxigeno": spo2, "temp": temp, 
        "alerta": alerta, "hora": datetime.datetime.now().strftime("%H:%M:%S")
    }
    
    print(f"📥 {nombre} | T:{temp} | HR:{ritmo} | Alerta:{alerta}")
    return jsonify({"status": "ok", "alerta_activa": alerta})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)