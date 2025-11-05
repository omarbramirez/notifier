from flask import Flask, request, jsonify
import pywhatkit as kit
import time
import datetime

# =========================================================
# CONFIGURACIÓN ESENCIAL
# =========================================================
# ⚠️ CAMBIA ESTO: Usa los 22 caracteres alfanuméricos del enlace de invitación del grupo.
ID_DEL_GRUPO = "JcxR4qlHtgB2bMa02SEfz3"
# Por ejemplo: https://chat.whatsapp.com/IDDeGrupoDeWhatsApp

app = Flask(__name__)

# =========================================================
# FUNCIÓN DE ENVÍO A WHATSAPP
# =========================================================
def enviar_a_grupo_whatsapp(mensaje):
    """
    Programa el envío del mensaje al minuto siguiente usando pywhatkit.
    Requiere que la sesión de WhatsApp Web esté abierta en el PC donde se ejecuta.
    """
    if ID_DEL_GRUPO == "TuIDDeGrupoDeWhatsApp":
        print("ERROR: La constante ID_DEL_GRUPO no ha sido configurada.")
        return False
        
    try:
        # Calcular la hora: Al minuto siguiente para envío 'instantáneo'
        now = datetime.datetime.now()
        # Sumamos 1 minuto. Si ya es el minuto 59, se pasa a la hora siguiente.
        future_time = now + datetime.timedelta(minutes=1) 
        
        hour = future_time.hour
        minute = future_time.minute
        
        # 1. Enviar el mensaje al grupo
        # El 4to argumento (15) es el tiempo de espera para que se cargue WhatsApp Web.
        # El 6to argumento (True) es para cerrar la pestaña después del envío.
        kit.sendwhatmsg_to_group(
            ID_DEL_GRUPO, 
            mensaje, 
            hour, 
            minute, 
            15, 
            True 
        )
        # Esperar un momento para asegurar que la automatización se complete
        time.sleep(30) 
        print(f"Notificación programada para las {hour}:{minute:02d}. Revisa la ventana del navegador.")
        return True
    except Exception as e:
        print(f"Ocurrió un error en la función de WhatsApp: {e}")
        return False

# =========================================================
# RUTA DEL WEBHOOK DE GITHUB
# =========================================================
@app.route('/github-commit', methods=['POST'])
def handle_webhook():
    """
    Esta ruta recibe la solicitud POST enviada por GitHub al hacer un push/commit.
    """
    # 1. Verificar si es una petición POST y si contiene datos
    if request.method != 'POST':
        return jsonify({"message": "Método no permitido"}), 405
        
    payload = request.json
    if not payload or 'head_commit' not in payload:
        # Podría ser un evento diferente a 'push', lo ignoramos
        print("Payload recibido, pero no es un evento de commit o está vacío.")
        return jsonify({"message": "Evento de GitHub ignorado o payload inválido"}), 200

    try:
        # 2. Extraer la información relevante del payload
        commit_message = payload['head_commit']['message']
        author_name = payload['head_commit']['author']['name']
        repo_name = payload['repository']['full_name']
        commit_url = payload['head_commit']['url']

        # 3. Formatear el mensaje de WhatsApp
        mensaje_whatsapp = (
            f"🚀 **NUEVA ACTUALIZACIÓN DISPONIBLE**\n"
            f"----------------------------------------\n"
            f"👤 Autor: {author_name}\n"
            f"📝 Mensaje: {commit_message}\n"
            f"🔗 Revisar: https://muebleria-mvp.vercel.app/es"
        )

        # 4. Enviar la notificación al grupo de WhatsApp
        exito = enviar_a_grupo_whatsapp(mensaje_whatsapp)
        
        if exito:
            return jsonify({"message": "Webhook procesado y notificación de WhatsApp enviada"}), 200
        else:
            return jsonify({"message": "Webhook procesado, pero falló el envío de WhatsApp"}), 500

    except Exception as e:
        print(f"Error al procesar el webhook: {e}")
        return jsonify({"message": f"Error interno del servidor: {e}"}), 500

# =========================================================
# INICIO DEL SERVIDOR
# =========================================================
if __name__ == '__main__':
    print("Servidor Flask iniciado...")
    print(f"Esperando Webhook de GitHub en la ruta /github-commit")
    # Es recomendable ejecutarlo en modo de depuración para desarrollo.
    app.run(port=5000, debug=True)