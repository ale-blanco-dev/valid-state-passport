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
CITA_URL = os.getenv("CITA_URL")

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

        driver.get(CITA_URL)
        print("Página cargada correctamente.")
        time.sleep(25)

        text = driver.find_element(By.ID, "datosPrivacidadHeader").text.strip().lower()
        if "privacidad" not in text:
            print("Texto de privacidad no detectado.")
            
        click_element_js(driver, wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[@id='idAutorizaEnvioDatos']//div[contains(@class, 'ui-chkbox-box')]"))))
        print("Checkbox 'Autoriza envío' clickeado.")

        time.sleep(10)
        click_element_js(driver, wait.until(EC.element_to_be_clickable((By.ID, "buttonPreConsultar"))))
        print("Botón 'Consultar' presionado.")

        time.sleep(15)
        click_element_js(driver, wait.until(EC.element_to_be_clickable((By.ID, "btAgendar"))))
        print("Botón 'Agendar' presionado.")

        time.sleep(15)
        click_element_js(driver, wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[span[contains(text(),'Oficina Sede Centro')]]"))))
        time.sleep(2)

        try:
            driver.find_element(By.XPATH, "//span[contains(text(), 'No hay citas disponibles')]")
            send_telegram_message("No hay citas disponibles en este momento.")
        except NoSuchElementException:
            print("¡Podrían haber citas disponibles!")
            send_telegram_message("¡Posible disponibilidad de citas. Revisa el sistema!")

    except Exception as e:
        print(f"Error general: {e}")
        send_telegram_message(f"Error en ejecución del script: {e}")
    finally:
        if driver:
            driver.quit()
        else:
            print("Driver no fue inicializado.")

def click_element_js(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        driver.execute_script("arguments[0].click();", element)
        return True
    except Exception as e:
        print(f"Error al hacer clic con JS: {e}")
        return False
if __name__ == "__main__":
    check_availability()