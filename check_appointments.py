from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests
import time
import os

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram_message(message):
    ##url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    response = requests.get(url)
    print(response.status_code, response.text)
    if response.status_code == 200:
        print("Mensaje enviado por Telegram ✅")
    else:
        print("Error al enviar mensaje ❌", response.text)

def check_availability():
    print("🟡 Iniciando revisión de citas...")

    # Configuración de Chrome en modo headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 15)

    try:
        # 1. Entrar a la página
        driver.get("https://agendacitas.cancilleria.gov.co/agendamiento-citas/agendamiento/agendamiento.xhtml")
        time.sleep(3)
        
        texto = driver.find_element(By.ID, "datosPrivacidadHeader").text
        if "Privacidad" in texto:
            print("OK")
        else:
            print("❌ No se encontró el texto de privacidad esperado.")
            
            
        myButton = driver.find_element(By.ID, "buttonPreConsultar")
        driver.execute_script("arguments[0].scrollIntoView(true);", myButton)
            
        driver.execute_script("window.scrollTo(0, 10000);")
        
        if myButton.is_displayed():
            print("✅ Botón 'Consultar' visible.")
        else:
            print("❌ No se encontró el boton.")
            
        print("✅ Página scrolleada correctamente.")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1000)")
        time.sleep(2)
        print("✅ Página scrolleada correctamente X2.")
        check_box = driver.find_element(By.XPATH, "//div[@id='idAutorizaEnvioDatos']//div[contains(@class, 'ui-chkbox-box')]")
        check_box.click()
        time.sleep(5)
        print("✅ Checkbox de privacidad marcado.")
        wait = WebDriverWait(driver, 15)
        myButton = wait.until(EC.element_to_be_clickable((By.ID, "buttonPreConsultar")))
        time.sleep(5)
        myButton.click()
        time.sleep(5)
        print("✅ Botón 'Consultar' presionado.")
        mysecondButton = wait.until(EC.element_to_be_clickable((By.ID, "btAgendar")))
        time.sleep(5)
        mysecondButton.click()
        time.sleep(5)
        print("✅ Botón 'Agendar' presionado.")
        buttonOfficeCenter = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[span[contains(text(),'Oficina Sede Centro')]]")))
        buttonOfficeCenter.click()
        time.sleep(5)
        try:
            driver.find_element(By.XPATH, "//span[contains(text(), 'No hay citas disponibles')]")
            send_telegram_message("❌ No hay citas disponibles en este momento.")
        except NoSuchElementException:
            send_telegram_message("🚨 ¡Posible disponibilidad de citas! Revisa el sistema.")
        except Exception as e:
            print("❌ Error durante la ejecución:", str(e))

    finally:
        driver.quit()
        print("🔚 Revisión finalizada.")

# Ejecutar
if __name__ == "__main__":
    check_availability()