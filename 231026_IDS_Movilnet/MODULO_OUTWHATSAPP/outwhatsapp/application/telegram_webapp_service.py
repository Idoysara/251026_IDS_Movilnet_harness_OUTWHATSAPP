"""
Servicio Deflector para Telegram WebApp (Mini-Apps de Telegram).
Gobernanza: Universal Best Practices Engineering Rule (Pilares I y III).
Permite integrar la PWA Soberana directamente dentro del chat de Telegram sin costos ni riesgo de baneo.
"""
from typing import Dict, Any, Optional
try:
    from outwhatsapp.domain.models import TelegramWebAppData
except ImportError:
    from outwhatsapp.domain.models import TelegramWebAppData


class TelegramWebAppService:
    """
    Construye cargas útiles para la API de Telegram con botones de apertura de la PWA.
    """

    @staticmethod
    def construir_payload_webapp(
        chat_id: int,
        webapp_url: str,
        mensaje_texto: str = "👋 ¡Hola! Accede a tu portal oficial Movilnet 4GMAX sin costo de datos:",
        texto_boton: str = "🚀 Abrir Portal Movilnet"
    ) -> Dict[str, Any]:
        """
        Genera el payload estándar de Telegram Bot API para abrir una WebApp embebida.
        """
        data = TelegramWebAppData(
            chat_id=chat_id,
            button_text=texto_boton,
            webapp_url=webapp_url,
            reply_text=mensaje_texto
        )

        return {
            "chat_id": data.chat_id,
            "text": data.reply_text,
            "parse_mode": "HTML",
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {
                            "text": data.button_text,
                            "web_app": {
                                "url": data.webapp_url
                            }
                        }
                    ]
                ]
            }
        }
