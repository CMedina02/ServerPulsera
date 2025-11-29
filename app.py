from flask import Flask, request, jsonify, render_template_string
import datetime

app = Flask(__name__)

# REGISTRO DE PACIENTES
directorio_pacientes = {
    "80:65:99:2B:25:94": "Paciente 1 - ROGER GONZALEZ",
}

estado_actual = {}

# HTML DASHBOARD
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="2"> 
    <title>Monitor Central - Signos Vitales</title>
    <style>
        /* --- RESET Y BASE --- */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #0f172a; /* Fondo Oscuro Original */
            color: #e2e8f0;
            padding: 20px;
            min-height: 100vh;
        }

        .container { max-width: 1200px; margin: 0 auto; }

        /* --- HEADER --- */
        header { margin-bottom: 40px; text-align: center; }
        
        header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 8px;
            background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        header p { color: #94a3b8; font-size: 1.1rem; }

        /* --- TABLA CONTAINER --- */
        .table-wrapper {
            background: #1e293b;
            border-radius: 12px;
            border: 1px solid #334155;
            overflow: hidden;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
        }

        table { width: 100%; border-collapse: collapse; }

        thead { background: #0f172a; border-bottom: 2px solid #334155; }

        th {
            padding: 20px;
            text-align: left;
            font-weight: 600;
            color: #94a3b8;
            text-transform: uppercase;
            font-size: 0.875rem;
            letter-spacing: 0.5px;
        }

        td {
            padding: 18px 20px;
            border-bottom: 1px solid #334155;
            color: #e2e8f0;
            vertical-align: middle;
        }

        tbody tr:last-child td { border-bottom: none; }

        /* --- ESTILOS DE CELDAS ESPECIFICOS --- */
        .patient-name {
            font-weight: 600;
            color: #60a5fa;
            font-size: 1rem;
        }
        
        .patient-mac {
            display: block;
            font-size: 0.75rem;
            color: #64748b;
            margin-top: 4px;
            font-family: monospace; /* Para que la MAC se vea técnica */
        }

        .metric {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 1.1rem;
            font-weight: 500;
        }

        .metric-value { min-width: 80px; }
        .metric-unit { color: #94a3b8; font-size: 0.875rem; margin-left: 4px; }

        /* Iconos */
        .heart-icon { color: #ef4444; font-size: 1.3rem; }
        .oxygen-icon { color: #3b82f6; font-size: 1.3rem; }
        .temp-icon { color: #f97316; font-size: 1.3rem; }

        /* --- BADGES DE ESTADO (Adaptados a tus clases de Python) --- */
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 500;
            text-transform: uppercase;
        }

        .status-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }

        /* Mapeo: Si Python manda 'bg-verde' -> Estilo Normal */
        .bg-verde {
            background: rgba(34, 197, 94, 0.2);
            color: #4ade80;
            border: 1px solid rgba(34, 197, 94, 0.3);
        }
        .bg-verde .status-dot {
            background: #4ade80;
            box-shadow: 0 0 8px rgba(74, 222, 128, 0.5);
        }

        /* Mapeo: Si Python manda 'bg-rojo' -> Estilo Crítico */
        .bg-rojo {
            background: rgba(239, 68, 68, 0.2);
            color: #ff6b6b;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }
        .bg-rojo .status-dot {
            background: #ff6b6b;
            box-shadow: 0 0 8px rgba(255, 107, 107, 0.5);
        }

        /* Mapeo: Si Python manda 'bg-gris' -> Estilo Desconocido/Offline */
        .bg-gris {
            background: rgba(148, 163, 184, 0.2);
            color: #cbd5e1;
            border: 1px solid rgba(148, 163, 184, 0.3);
        }
        .bg-gris .status-dot { background: #94a3b8; }

        .empty-state { text-align: center; padding: 40px; color: #94a3b8; }

        /* Responsive */
        @media (max-width: 768px) {
            header h1 { font-size: 1.8rem; }
            th, td { padding: 12px; font-size: 0.9rem; }
            .metric { flex-direction: column; align-items: flex-start; gap: 4px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Monitor de Signos Vitales</h1>
            <p>Panel de Control</p>
        </header>

        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>Paciente</th>
                        <th>Temperatura</th>
                        <th>Ritmo Cardíaco</th>
                        <th>SpO2</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
                    {% for mac, p in datos.items() %}
                    <tr>
                        <td class="patient-name">
                            {{ p.nombre }}
                            <span class="patient-mac">MAC: {{ mac }}</span>
                        </td>
                        <td>
                            <div class="metric">
                                <span class="temp-icon">●</span>
                                <span class="metric-value">{{ p.temp }}<span class="metric-unit">°C</span></span>
                            </div>
                        </td>
                        <td>
                            <div class="metric">
                                <span class="heart-icon">♥</span>
                                <span class="metric-value">{{ p.ritmo }}<span class="metric-unit">BPM</span></span>
                            </div>
                        </td>
                        <td>
                            <div class="metric">
                                <span class="oxygen-icon">●</span>
                                <span class="metric-value">{{ p.oxigeno }}<span class="metric-unit">%</span></span>
                            </div>
                        </td>
                        <td>
                            <span class="status-badge {{ p.bg }}">
                                <span class="status-dot"></span>
                                {{ p.msg }}
                            </span>
                        </td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="5" class="empty-state">
                            Esperando datos de sensores...
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
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
    msg = "EN ESPERA"
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
            msg = " " + ", ".join(fallos)
            clase = "rojo"
            bg = "bg-rojo"
        else:
            msg = "ESTABLE"
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