from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service

import requests
import time
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    response = requests.get(url)
    if response.status_code == 200:
        print("✅ Mensaje enviado por Telegram")
    else:
        print(f"❌ Error al enviar mensaje: {response.status_code} - {response.text}")

def click_element_js(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        driver.execute_script("arguments[0].click();", element)
        return True
    except Exception as e:
        print(f"❌ Error al hacer clic con JS: {e}")
        return False

def check_availability():
    print("🟡 Iniciando revisión de citas x2...")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # 🚨 Asegura que Chrome está en la ruta esperada
    chrome_options.binary_location = "/usr/bin/google-chrome"

    driver = webdriver.Chrome(service=Service(), options=chrome_options)
    wait = WebDriverWait(driver, 15)

    try:
        driver.get("https://agendacitas.cancilleria.gov.co/agendamiento-citas/agendamiento/agendamiento.xhtml")
        time.sleep(2)

        try:
            texto = driver.find_element(By.ID, "datosPrivacidadHeader").text
            if "Privacidad" in texto:
                print("✅ Texto de privacidad encontrado.")
            else:
                print("❌ Texto de privacidad no detectado.")
        except NoSuchElementException:
            print("❌ Elemento de privacidad no encontrado.")
            return

        button_pre_consultar = wait.until(EC.presence_of_element_located((By.ID, "buttonPreConsultar")))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1000)")
        print("✅ Página scrolleada.")

        check_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='idAutorizaEnvioDatos']//div[contains(@class, 'ui-chkbox-box')]")))
        click_element_js(driver, check_box)
        print("✅ Checkbox clickeado.")

        time.sleep(1)
        click_element_js(driver, button_pre_consultar)
        print("✅ Botón 'Consultar' presionado.")

        button_agendar = wait.until(EC.element_to_be_clickable((By.ID, "btAgendar")))
        time.sleep(3)
        click_element_js(driver, button_agendar)
        print("✅ Botón 'Agendar' presionado.")

        button_oficina = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[span[contains(text(),'Oficina Sede Centro')]]")))
        time.sleep(3)
        click_element_js(driver, button_oficina)
        print("✅ Botón 'Oficina Sede Centro' presionado.")


        time.sleep(2)
        try:
            driver.find_element(By.XPATH, "//span[contains(text(), 'No hay citas disponibles')]")
            send_telegram_message("❌ No hay citas disponibles en este momento.")
        except NoSuchElementException:
            send_telegram_message("🚨 ¡Posible disponibilidad de citas! Revisa el sistema.")
    except Exception as e:
        print(f"❌ Error general: {e}")
    finally:
        driver.quit()
        print("🔚 Revisión finalizada.")

if __name__ == "__main__":
    check_availability()