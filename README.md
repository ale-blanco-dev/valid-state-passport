# Verificación de Citas - Pasaporte

Este proyecto automatiza la verificación mensual de disponibilidad de citas en la plataforma de agendamiento.

Utiliza Selenium en modo headless para simular la interacción con la interfaz web, captura posibles resultados, y genera un reporte visual en HTML que incluye una captura de pantalla si ocurre un error. 
También notifica el estado de la verificación mediante Telegram.

---

## ¿Qué incluye?

- Navegación automatizada con Selenium.
- Notificaciones por Telegram (mediante bot).
- Generación de reporte HTML.
- Captura automática de pantalla en caso de fallo.
- Ejecución cada cierto tiempo vía GitHub Actions.
- Lógica de expiración dentro de un mes.

---

## Ejecución local

1. Instala dependencias:

```bash
pip install -r requirements.txt
python check_appointments.py
