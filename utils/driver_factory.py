"""Fábrica de WebDriver (patrón Factory).

Centraliza la creación del navegador para que las pruebas no dependan de un
navegador concreto. Desde Selenium 4.6, Selenium Manager descarga
automáticamente el driver compatible con el navegador instalado.
"""
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService

# Preferencias que desactivan el gestor de contraseñas de Chrome/Edge.
# Evitan que aparezca el aviso "Cambia tu contraseña" al usar las credenciales
# públicas de prueba de SauceDemo, que interrumpe la ejecución.
_PREFS_SIN_GESTOR_CONTRASENAS = {
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False,
    "profile.password_manager_leak_detection": False,
}


def _opciones_chromium(opciones, headless):
    if headless:
        opciones.add_argument("--headless=new")
    opciones.add_argument("--window-size=1366,900")
    opciones.add_argument("--disable-notifications")
    opciones.add_argument("--disable-features=PasswordLeakDetection")
    opciones.add_experimental_option("prefs", _PREFS_SIN_GESTOR_CONTRASENAS)
    return opciones


def crear_driver(navegador: str = "chrome", headless: bool = False):
    """Crea y devuelve una instancia de WebDriver según el navegador indicado."""
    navegador = navegador.lower()

    if navegador == "chrome":
        opciones = _opciones_chromium(webdriver.ChromeOptions(), headless)
        binario = os.getenv("CHROME_BINARY")  # opcional: navegador en ruta no estándar
        if binario:
            opciones.binary_location = binario
        ruta_driver = os.getenv("CHROMEDRIVER_PATH")  # opcional: driver manual
        servicio = ChromeService(executable_path=ruta_driver) if ruta_driver else ChromeService()
        driver = webdriver.Chrome(options=opciones, service=servicio)

    elif navegador == "edge":
        opciones = _opciones_chromium(webdriver.EdgeOptions(), headless)
        driver = webdriver.Edge(options=opciones)

    elif navegador == "firefox":
        opciones = webdriver.FirefoxOptions()
        if headless:
            opciones.add_argument("-headless")
        driver = webdriver.Firefox(options=opciones)
        driver.set_window_size(1366, 900)

    else:
        raise ValueError(f"Navegador no soportado: {navegador}. Use chrome, edge o firefox.")

    # Se usan esperas explícitas en los Page Objects; la implícita queda en cero.
    driver.implicitly_wait(0)
    return driver
