from flask import Flask, request, jsonify, render_template_string
import datetime

app = Flask(__name__)

# --- CONFIGURACIÓN ---
# Aquí registras las MACs de tus pulseras
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
    <title>🏥 Central de Monitoreo</title>
    <meta http-equiv="refresh" content="2"> 
    <style>
        body { font-family: 'Arial', sans-serif; background: #f4f6f7; padding: 20px; }
        h1 { text-align: center; color: #34495e; }
        .container { display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; }
        
        .card { 
            background: white; width: 320px; border-radius: 12px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.1); overflow: hidden;
            font-size: 1.1em;
        }
        
        .card-header { padding: 15px; color: white; font-weight: bold; text-align: center; }
        .card-body { padding: 20px; }
        .dato { display: flex; justify-content: space-between; margin-bottom: 10px; border-bottom: 1px solid #eee; padding-bottom: 5px; }
        .estado-msg { text-align: center; margin-top: 15px; padding: 10px; border-radius: 8px; font-weight: bold; }

        /* COLORES DE ESTADO */
        .gris  { background-color: #95a5a6; } /* Standby */
        .verde { background-color: #27ae60; } /* Todo Bien */
        .rojo  { background-color: #c0392b; animation: parpadeo 1s infinite; } /* Alerta */

        @keyframes parpadeo { 0% {opacity: 1;} 50% {opacity: 0.8;} 100% {opacity: 1;} }
    </style>
</head>
<body>
    <h1>🏥 Central de Monitoreo IOT</h1>
    <div class="container">
        {% for mac, p in datos.items() %}
        <div class="card">
            <div class="card-header {{ p.color_css }}">
                {{ p.nombre }}
            </div>
            <div class="card-body">
                <div class="dato"><span>🌡️ Temperatura:</span> <strong>{{ p.temp }} °C</strong></div>
                <div class="dato"><span>❤️ Ritmo Card.:</span> <strong>{{ p.ritmo }} BPM</strong></div>
                <div class="dato"><span>💧 Oxígeno:</span> <strong>{{ p.oxigeno }} %</strong></div>
                
                <div class="estado-msg {{ p.color_css }}" style="color:white;">
                    {{ p.mensaje }}
                </div>
                <div style="text-align:center; font-size:0.8em; color:#888; margin-top:10px;">
                    MAC: {{ mac }} <br> Hora: {{ p.hora }}
                </div>
            </div>
        </div>
        {% else %}
            <h3>📡 Esperando conexión de dispositivos...</h3>
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
    
    nombre = directorio_pacientes.get(mac, "Paciente Desconocido")
    
    # --- LÓGICA DE DIAGNÓSTICO ---
    alerta = False
    mensaje = "SIN LECTURA"
    color_css = "gris"

    # 1. ¿Hay alguien conectado? (Si todo es 0, es Standby)
    if ritmo > 0 or spo2 > 0 or temp > 25.0:
        
        # 2. Análisis de Signos Vitales
        fallos = []
        
        # Temperatura (Aceptamos entre 33 y 37.8 como normal en muñeca)
        if temp > 37.8: fallos.append("FIEBRE")
        if temp < 33.0: fallos.append("HIPOTERMIA") 

        # Ritmo Cardiaco
        if ritmo > 120: fallos.append("TAQUICARDIA")
        if ritmo < 50: fallos.append("BRADICARDIA")

        # Oxigenación
        if spo2 < 90: fallos.append("HIPOXIA")

        # 3. Decisión Final
        if len(fallos) > 0:
            alerta = True
            mensaje = "⚠️ ALERTA: " + ", ".join(fallos)
            color_css = "rojo"
        else:
            alerta = False
            mensaje = "✅ ESTABLE"
            color_css = "verde"
            
    else:
        # Modo Standby (Sensores en 0)
        mensaje = "💤 ESPERANDO..."
        color_css = "gris"
        alerta = False

    # Guardar estado
    estado_actual[mac] = {
        "nombre": nombre, "ritmo": ritmo, "oxigeno": spo2, "temp": temp,
        "alerta": alerta, "mensaje": mensaje, "color_css": color_css,
        "hora": datetime.datetime.now().strftime("%H:%M:%S")
    }
    
    print(f"[{mac}] {mensaje} | T:{temp}")
    
    return jsonify({"status": "ok", "alerta_activa": alerta})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)