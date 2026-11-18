import time

from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.support.ui import Select

from pages.base_page import BasePage, data_test


def id_producto(nombre: str) -> str:
    """Convierte el nombre del producto al formato de sus botones (p. ej., sauce-labs-backpack)."""
    return "-".join(nombre.split()).lower()


class InventoryPage(BasePage):
    RUTA = "/inventory.html"
    TITULO = data_test("title")
    PRODUCTOS = data_test("inventory-item")
    NOMBRES = data_test("inventory-item-name")
    PRECIOS = data_test("inventory-item-price")
    ORDENAR = data_test("product-sort-container")
    INSIGNIA_CARRITO = data_test("shopping-cart-badge")
    ENLACE_CARRITO = data_test("shopping-cart-link")
    ABRIR_MENU = data_test("open-menu")
    CERRAR_SESION = data_test("logout-sidebar-link")

    def esperar_carga(self):
        self.esperar_url(self.RUTA)
        self.encontrar(self.TITULO)
        return self

    @property
    def titulo(self) -> str:
        return self.texto(self.TITULO)

    def cantidad_productos(self) -> int:
        return len(self.encontrar_todos(self.PRODUCTOS))

    def nombres(self) -> list:
        return [e.text.strip() for e in self.encontrar_todos(self.NOMBRES)]

    def precios(self) -> list:
        return [float(e.text.strip().replace("$", "")) for e in self.encontrar_todos(self.PRECIOS)]

    def catalogo(self) -> dict:
        return dict(zip(self.nombres(), self.precios()))

    def ordenar_por(self, valor: str):
        Select(self.encontrar(self.ORDENAR)).select_by_value(valor)

    def agregar_al_carrito(self, nombre: str):
        self.clic(data_test(f"add-to-cart-{id_producto(nombre)}"))

    def quitar_del_carrito(self, nombre: str):
        self.clic(data_test(f"remove-{id_producto(nombre)}"))

    def cantidad_en_carrito(self) -> int:
        insignias = self.driver.find_elements(*self.INSIGNIA_CARRITO)
        return int(insignias[0].text) if insignias else 0

    def ir_al_carrito(self):
        self.clic(self.ENLACE_CARRITO)

    def cerrar_sesion(self):
        self.clic(self.ABRIR_MENU)
        # El menú lateral se abre con una animación: se reintenta el clic si aún está en movimiento.
        for intento in range(3):
            try:
                self.clic(self.CERRAR_SESION)
                return
            except ElementClickInterceptedException:
                time.sleep(0.5)
        self.clic(self.CERRAR_SESION)
