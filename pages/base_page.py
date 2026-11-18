"""Clase base de los Page Objects.

Reúne las operaciones comunes (esperas explícitas, clics, escritura y lectura
de texto) para que cada página solo describa sus elementos y acciones.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from data.datos_prueba import URL_BASE


def data_test(valor: str):
    """Localizador por el atributo data-test que SauceDemo expone para pruebas."""
    return (By.CSS_SELECTOR, f'[data-test="{valor}"]')


class BasePage:
    RUTA = "/"
    TIEMPO_ESPERA = 10  # segundos

    def __init__(self, driver):
        self.driver = driver
        self.espera = WebDriverWait(driver, self.TIEMPO_ESPERA)

    # Navegación
    def abrir(self):
        self.driver.get(URL_BASE + self.RUTA)
        return self

    @property
    def url_actual(self) -> str:
        return self.driver.current_url

    # Esperas y acciones
    def encontrar(self, localizador):
        return self.espera.until(EC.visibility_of_element_located(localizador))

    def encontrar_todos(self, localizador):
        self.espera.until(EC.presence_of_all_elements_located(localizador))
        return self.driver.find_elements(*localizador)

    def clic(self, localizador):
        self.espera.until(EC.element_to_be_clickable(localizador)).click()

    def escribir(self, localizador, texto: str):
        campo = self.encontrar(localizador)
        campo.clear()
        if texto:
            campo.send_keys(texto)

    def texto(self, localizador) -> str:
        return self.encontrar(localizador).text.strip()

    def existe(self, localizador) -> bool:
        return len(self.driver.find_elements(*localizador)) > 0

    def esperar_url(self, fragmento: str):
        self.espera.until(EC.url_contains(fragmento))
