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

# === Variables de entorno obligatorias ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CHROME_BIN = os.getenv("CHROME_BIN")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")

if not BOT_TOKEN or not CHAT_ID:
    raise EnvironmentError("BOT_TOKEN y CHAT_ID deben estar definidos en las variables de entorno.")

# === Utilidades ===
def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    response = requests.get(url, params=payload)
    status = "Mensaje enviado" if response.ok else f"Error al enviar mensaje: {response.status_code} - {response.text}"
    print(status)

def click_element_js(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        driver.execute_script("arguments[0].click();", element)
        return True
    except Exception as e:
        print(f"Error al hacer clic con JS: {e}")
        return False

def get_chrome_options():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = CHROME_BIN
    return options

# === Lógica principal ===
def check_availability():
    print("Iniciando revisión de citas...")

    driver = webdriver.Chrome(
        service=Service(CHROMEDRIVER_PATH),
        options=get_chrome_options()
    )
    wait = WebDriverWait(driver, 15)

    try:
        driver.get("https://agendacitas.cancilleria.gov.co/agendamiento-citas/agendamiento/agendamiento.xhtml")
        time.sleep(2)

        if "Privacidad" not in driver.find_element(By.ID, "datosPrivacidadHeader").text:
            print("Texto de privacidad no detectado.")
            return
        print("Texto de privacidad encontrado.")

        click_element_js(driver, wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='idAutorizaEnvioDatos']//div[contains(@class, 'ui-chkbox-box')]"))))
        print("Checkbox clickeado.")

        time.sleep(1)
        click_element_js(driver, wait.until(EC.element_to_be_clickable((By.ID, "buttonPreConsultar"))))
        print("Botón 'Consultar' presionado.")

        time.sleep(3)
        click_element_js(driver, wait.until(EC.element_to_be_clickable((By.ID, "btAgendar"))))
        print("Botón 'Agendar' presionado.")

        time.sleep(3)
        click_element_js(driver, wait.until(EC.element_to_be_clickable((By.XPATH, "//button[span[contains(text(),'Oficina Sede Centro')]]"))))
        print("Botón 'Oficina Sede Centro' presionado.")

        time.sleep(2)
        try:
            driver.find_element(By.XPATH, "//span[contains(text(), 'No hay citas disponibles')]")
            send_telegram_message("No hay citas disponibles en este momento.")
        except NoSuchElementException:
            send_telegram_message("Posible disponibilidad de citas. Revisa el sistema.")

    except Exception as e:
        print(f"Error general: {e}")
        send_telegram_message(f"Error en ejecución del script: {e}")
    finally:
        driver.quit()
        print("Revisión finalizada.")

if __name__ == "__main__":
    check_availability()