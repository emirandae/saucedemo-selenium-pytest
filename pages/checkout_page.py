from pages.base_page import BasePage, data_test


def _monto(texto: str) -> float:
    """Extrae el monto de un texto como 'Item total: $39.98'."""
    return float(texto.split("$")[-1])


class CheckoutInformacionPage(BasePage):
    RUTA = "/checkout-step-one.html"
    NOMBRE = data_test("firstName")
    APELLIDO = data_test("lastName")
    CODIGO_POSTAL = data_test("postalCode")
    CONTINUAR = data_test("continue")
    MENSAJE_ERROR = data_test("error")

    def completar(self, nombre: str, apellido: str, codigo_postal: str):
        self.esperar_url(self.RUTA)
        self.escribir(self.NOMBRE, nombre)
        self.escribir(self.APELLIDO, apellido)
        self.escribir(self.CODIGO_POSTAL, codigo_postal)
        self.clic(self.CONTINUAR)

    @property
    def mensaje_error(self) -> str:
        return self.texto(self.MENSAJE_ERROR)


class CheckoutResumenPage(BasePage):
    RUTA = "/checkout-step-two.html"
    NOMBRES = data_test("inventory-item-name")
    SUBTOTAL = data_test("subtotal-label")
    IMPUESTO = data_test("tax-label")
    TOTAL = data_test("total-label")
    FINALIZAR = data_test("finish")

    def esperar_carga(self):
        self.esperar_url(self.RUTA)
        self.encontrar(self.TOTAL)
        return self

    def productos(self) -> list:
        return [e.text.strip() for e in self.encontrar_todos(self.NOMBRES)]

    @property
    def subtotal(self) -> float:
        return _monto(self.texto(self.SUBTOTAL))

    @property
    def impuesto(self) -> float:
        return _monto(self.texto(self.IMPUESTO))

    @property
    def total(self) -> float:
        return _monto(self.texto(self.TOTAL))

    def finalizar(self):
        self.clic(self.FINALIZAR)


class CheckoutCompletoPage(BasePage):
    RUTA = "/checkout-complete.html"
    ENCABEZADO = data_test("complete-header")

    @property
    def encabezado(self) -> str:
        self.esperar_url(self.RUTA)
        return self.texto(self.ENCABEZADO)
