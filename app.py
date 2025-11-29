from flask import Flask, request, jsonify, render_template_string
import datetime

app = Flask(__name__)

# --- REGISTRO DE PACIENTES ---
# Asegúrate que la MAC coincida con lo que imprime el monitor serial de Arduino
directorio_pacientes = {
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
        body { font-family: 'Segoe UI', sans-serif; background: #eaeff1; padding: 20px; }
        h1 { text-align: center; color: #2c3e50; }
        .grid { display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; }
        
        .card { 
            background: white; width: 300px; padding: 20px; border-radius: 15px; 
            box-shadow: 0 4px 10px rgba(0,0,0,0.1); 
            transition: transform 0.2s;
        }
        
        /* ESTADOS VISUALES */
        .standby { border-top: 10px solid #95a5a6; } /* GRIS */
        .normal  { border-top: 10px solid #2ecc71; } /* VERDE */
        .peligro { border-top: 10px solid #e74c3c; background-color: #fadbd8; } /* ROJO */

        .header { font-size: 1.2em; font-weight: bold; border-bottom: 2px solid #ddd; padding-bottom: 10px; margin-bottom: 10px;}
        .row { display: flex; justify-content: space-between; margin: 8px 0; font-size: 1.1em; }
        
        .badge { padding: 5px 10px; border-radius: 5px; color: white; font-weight: bold; text-align: center; margin-top: 15px;}
        .bg-gray { background-color: #95a5a6; }
        .bg-green { background-color: #2ecc71; }
        .bg-red { background-color: #e74c3c; }
    </style>
</head>
<body>
    <h1>🏥 Monitor de Signos Vitales</h1>
    <div class="grid">
        {% for mac, p in datos.items() %}
        
        <div class="card {{ p.clase_css }}">
            <div class="header">
                {{ p.nombre }}<br>
                <span style="font-size:0.7em; color:#555;">ID: {{ mac }}</span>
            </div>
            
            <div class="row"><span>🌡️ Temp:</span> <strong>{{ p.temp }} °C</strong></div>
            <div class="row"><span>❤️ Ritmo:</span> <strong>{{ p.ritmo }} BPM</strong></div>
            <div class="row"><span>💧 SpO2:</span> <strong>{{ p.oxigeno }} %</strong></div>

            <div class="badge {{ p.badge_css }}">
                {{ p.texto_estado }}
            </div>
            <div style="text-align:center; font-size:0.8em; color:#777; margin-top:5px;">
                Última act: {{ p.hora }}
            </div>
        </div>

        {% else %}
            <p style="text-align:center; margin-top:50px; font-size:1.5em; color:#7f8c8d;">
                📡 Esperando conexión de pulseras...
            </p>
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
    # Recibimos los datos (que ya vienen limpios desde Arduino, si son 0 es que no hay lectura)
    ritmo = int(data.get('ritmo', 0))
    spo2 = int(data.get('oxigeno', 0))
    temp = float(data.get('temperatura', 0.0))
    
    nombre = directorio_pacientes.get(mac, "Paciente Desconocido")
    
    # --- LOGICA DE ALERTA MEJORADA ---
    alerta = False
    estado_texto = "SIN DATOS"
    clase_css = "standby"
    badge_css = "bg-gray"

    # Caso 1: Lecturas válidas detectadas (No son cero)
    if ritmo > 0 or spo2 > 0:
        # Asumimos estado normal primero
        estado_texto = "ESTABLE"
        clase_css = "normal"
        badge_css = "bg-green"
        
        # Chequeo de Anomalías (Solo si tenemos datos reales)
        motivo_alerta = []
        
        # Fiebre o Hipotermia (Validamos que temp no sea 0 para no alertar por desconexión)
        if temp > 37.5: motivo_alerta.append("FIEBRE")
        if temp < 35.0 and temp > 10.0: motivo_alerta.append("BAJA TEMP")
        
        # Taquicardia o Bradicardia
        if ritmo > 120: motivo_alerta.append("TAQUICARDIA")
        if ritmo < 50: motivo_alerta.append("BRADICARDIA")
        
        # Hipoxia
        if spo2 < 90: motivo_alerta.append("BAJO OXIGENO")

        # Si hubo algún motivo, activamos la alerta roja
        if len(motivo_alerta) > 0:
            alerta = True
            estado_texto = "⚠️ ALERTA: " + ", ".join(motivo_alerta)
            clase_css = "peligro"
            badge_css = "bg-red"

    else:
        # Caso 2: Todo es cero
        estado_texto = "ESPERANDO PACIENTE..."
        clase_css = "standby"
        badge_css = "bg-gray"

    # Guardamos en la memoria del servidor
    estado_actual[mac] = {
        "nombre": nombre,
        "ritmo": ritmo,
        "oxigeno": spo2,
        "temp": round(temp, 1),
        "alerta": alerta,
        "texto_estado": estado_texto,
        "clase_css": clase_css,
        "badge_css": badge_css,
        "hora": datetime.datetime.now().strftime("%H:%M:%S")
    }
    
    print(f"📥 {nombre} -> {estado_texto} | T:{temp} HR:{ritmo}")
    
    # Devolvemos la orden al ESP32 (si alerta=True, la pulsera pita/prende rojo)
    return jsonify({"status": "ok", "alerta_activa": alerta})

if __name__ == '__main__':
    # host='0.0.0.0' permite que otras PCs en la red vean la página
    app.run(host='0.0.0.0', port=5000, debug=True)