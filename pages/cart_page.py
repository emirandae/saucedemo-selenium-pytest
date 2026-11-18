from pages.base_page import BasePage, data_test


class CartPage(BasePage):
    RUTA = "/cart.html"
    TITULO = data_test("title")
    NOMBRES = data_test("inventory-item-name")
    BOTON_PAGAR = data_test("checkout")
    SEGUIR_COMPRANDO = data_test("continue-shopping")

    def esperar_carga(self):
        self.esperar_url(self.RUTA)
        self.encontrar(self.TITULO)
        return self

    def productos(self) -> list:
        if not self.existe(self.NOMBRES):
            return []
        return [e.text.strip() for e in self.driver.find_elements(*self.NOMBRES)]

    def seguir_comprando(self):
        self.clic(self.SEGUIR_COMPRANDO)

    def ir_a_pagar(self):
        self.clic(self.BOTON_PAGAR)
