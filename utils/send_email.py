import resend
import os
from flask import jsonify
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.environ["RESEND_API_KEY"]
APP_WEB_URL = os.environ["APP_WEB_URL"]

def ResetPassword(email, name, token):
    html = f"""
      <div>
        <h1>Hola, {name}</h1>
        <p>Has solicitado restablecer tu contraseña.</p>
        <p>Haz clic en el siguiente enlace para continuar con el proceso:</p>
        <a href='{APP_WEB_URL}password_reset?token={token}' target="_blank" rel="noopener noreferrer">
          Restablecer contraseña
        </a>
        <p>Si no solicitaste este cambio, puedes ignorar este correo.</p>
        <small>Atentamente, el equipo de soporte.</small>
      </div>
    """
    params: resend.Emails.SendParams = {
        "from": "soporte@full-style.com",
        "to": email,
        "subject": "Recuperación de contraseña - FullStyle",
        "html": html,
    }

    r = resend.Emails.send(params)
    return jsonify(r)
