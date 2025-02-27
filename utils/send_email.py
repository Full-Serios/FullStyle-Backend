import resend
import os
from flask import jsonify
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.environ["RESEND_API_KEY"]
APP_WEB_URL = os.environ["APP_WEB_URL"]

def ResetPassword(email, name, token):
    reset_link = f"{APP_WEB_URL}password_reset?token={token}"

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;
                border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9; text-align: center;">
        <h1 style="color: #333;">Hola, {name} 👋</h1>
        <p style="font-size: 16px; color: #555;">Has solicitado restablecer tu contraseña.</p>
        <p style="font-size: 14px; color: #666;">Haz clic en el botón de abajo para continuar:</p>

        <a href="{reset_link}" target="_blank" rel="noopener noreferrer"
           style="display: inline-block; padding: 12px 20px; margin: 10px 0;
                  font-size: 16px; color: #fff; background-color: #007bff;
                  text-decoration: none; border-radius: 5px;">
            🔑 Restablecer contraseña
        </a>

        <p style="font-size: 14px; color: #666;">Si no solicitaste este cambio, ignora este correo.</p>
        <hr style="margin: 20px 0; border: 0; border-top: 1px solid #ddd;" />

        <p style="font-size: 12px; color: #999;">
            📩 Este es un mensaje automático, no respondas a este correo.
        </p>
        <p style="font-size: 14px; font-weight: bold; color: #007bff;">
            — El equipo de FullStyle
        </p>
    </div>
    """

    params: resend.Emails.SendParams = {
        "from": "soporte@full-style.com",
        "to": email,
        "subject": "🔑 Recuperación de contraseña - FullStyle",
        "html": html,
    }

    r = resend.Emails.send(params)
    return jsonify(r)
