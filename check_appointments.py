import os
import time
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from jinja2 import Template
from datetime import datetime



BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CHROME_BIN = os.getenv("CHROME_BIN")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")

if not BOT_TOKEN or not CHAT_ID:
    raise EnvironmentError("BOT_TOKEN y CHAT_ID deben estar definidos como variables de entorno.")


def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    response = requests.get(url, params=payload)
    if response.ok:
        print("✅ Mensaje enviado a Telegram.")
    else:
        print(f"❌ Error al enviar mensaje: {response.status_code} - {response.text}")


def get_chrome_options():
    print("Configurando opciones de Chrome...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = CHROME_BIN

    print("Chrome Options activadas:")
    for opt in options.arguments:
        print(f"  - {opt}")
    if options.binary_location:
        print(f"  - Binary location: {options.binary_location}")
    else:
        print("  - Binary location: NO DEFINIDO")

    return options


# ==================== Lógica principal ====================

def check_availability():
    print("Iniciando revisión de citas...")
    driver = None
    status = "Éxito"
    details = "Citas disponibles encontradas."

    try:
        driver = webdriver.Chrome(options=get_chrome_options())
        wait = WebDriverWait(driver, 15)

        driver.get("https://agendacitas.cancilleria.gov.co/agendamiento-citas/agendamiento/agendamiento.xhtml")
        print("Página cargada correctamente.")
        time.sleep(5)

        text = driver.find_element(By.ID, "datosPrivacidadHeader").text.strip().lower()
        if "privacidad" not in text:
            print("Texto de privacidad no detectado.")
            status = "Falló"
            details = "Texto de privacidad no detectado en la página."
            return

        print("Texto de privacidad encontrado.")

        # Flujo
        click_element_js(driver, wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[@id='idAutorizaEnvioDatos']//div[contains(@class, 'ui-chkbox-box')]"))))
        print("Checkbox 'Autoriza envío' clickeado.")

        time.sleep(1)
        click_element_js(driver, wait.until(EC.element_to_be_clickable((By.ID, "buttonPreConsultar"))))
        print("Botón 'Consultar' presionado.")

        time.sleep(3)
        click_element_js(driver, wait.until(EC.element_to_be_clickable((By.ID, "btAgendar"))))
        print("Botón 'Agendar' presionado.")

        time.sleep(3)
        click_element_js(driver, wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[span[contains(text(),'Oficina Sede Centro')]]"))))
        print("Botón 'Oficina Sede Centro' presionado.")

        time.sleep(2)

        try:
            driver.find_element(By.XPATH, "//span[contains(text(), 'No hay citas disponibles')]")
            print("No hay citas disponibles.")
            send_telegram_message("No hay citas disponibles en este momento.")
            details = "No hay citas disponibles en el sistema."
        except NoSuchElementException:
            print("¡Podrían haber citas disponibles!")
            send_telegram_message("✅ Posible disponibilidad de citas. Revisa el sistema.")
            details = "¡Parece que hay citas disponibles!"

    except Exception as e:
        print(f"Error general: {e}")
        send_telegram_message(f"❌ Error en ejecución del script: {e}")
        status = "Falló"
        details = f"Excepción: {e}"
        if driver:
            driver.save_screenshot("screenshot.png")
            print("📸 Captura tomada tras el fallo.")

    finally:
        if driver:
            driver.quit()
            print("Navegador cerrado.")
        else:
            print("Driver no fue inicializado.")

        write_html_report(status, details, "screenshot.png" if status == "Falló" else None)

def click_element_js(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        driver.execute_script("arguments[0].click();", element)
        return True
    except Exception as e:
        print(f"Error al hacer clic con JS: {e}")
        return False

def write_html_report(status: str, details: str, screenshot_path: str = None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    template_str = """
    <html>
      <head>
        <title>UI Test Report</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 20px; background: #f9f9f9; }
          h1 { color: #333; }
          .status { font-size: 1.2em; margin-bottom: 20px; }
          .screenshot img { max-width: 100%; border: 1px solid #ccc; }
          pre { background: #eee; padding: 10px; border-radius: 5px; }
        </style>
      </head>
      <body>
        <h1>Estado de la revisión: {{ status }}</h1>
        <p><strong>Fecha:</strong> {{ timestamp }}</p>
        <div class="status"><strong>Detalles:</strong></div>
        <pre>{{ details }}</pre>
        {% if screenshot_path %}
        <div class="screenshot">
          <h2>Captura de pantalla:</h2>
          <img src="{{ screenshot_path }}" alt="screenshot">
        </div>
        {% endif %}
      </body>
    </html>
    """
    template = Template(template_str)
    html_content = template.render(
        status=status,
        timestamp=timestamp,
        details=details,
        screenshot_path=screenshot_path
    )
    with open("ui_test_report.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Reporte HTML generado: ui_test_report.html")
if __name__ == "__main__":
    check_availability()