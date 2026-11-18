"""Genera la matriz de gestión de casos de prueba (docs/casos_de_prueba.xlsx).

Combina el diseño de los casos (definido abajo) con los resultados de la última
ejecución (reports/resultados.json), de modo que la matriz refleje siempre el
resultado obtenido real.

Uso:  python -m utils.matriz_casos
"""
import json
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

RAIZ = Path(__file__).resolve().parent.parent
RESULTADOS = RAIZ / "reports" / "resultados.json"
SALIDA = RAIZ / "docs" / "casos_de_prueba.xlsx"

CASOS = [
    {
        "id": "CP-01", "modulo": "Autenticación", "prioridad": "Alta", "tipo": "Funcional / humo",
        "titulo": "Inicio de sesión exitoso con el usuario estándar",
        "precondiciones": "Navegador abierto en la página de inicio de sesión.",
        "datos": "Usuario: standard_user; contraseña pública de demostración.",
        "pasos": "1. Abrir la página de inicio.\n2. Digitar usuario y contraseña.\n3. Presionar «Login».",
        "esperado": "Se muestra /inventory.html con el título «Products» y 6 productos.",
        "prueba": "tests/test_01_login.py::test_inicio_sesion_exitoso",
    },
    {
        "id": "CP-02", "modulo": "Autenticación", "prioridad": "Alta", "tipo": "Funcional / negativa",
        "titulo": "Rechazo de credenciales inválidas o incompletas",
        "precondiciones": "Navegador abierto en la página de inicio de sesión.",
        "datos": "4 clases no válidas: contraseña incorrecta, usuario inexistente, usuario vacío y contraseña vacía.",
        "pasos": "1. Abrir la página de inicio.\n2. Digitar la combinación de datos.\n3. Presionar «Login».",
        "esperado": "Mensaje de error correspondiente a cada caso; el usuario permanece en la página de inicio.",
        "prueba": "tests/test_01_login.py::test_inicio_sesion_invalido",
    },
    {
        "id": "CP-03", "modulo": "Autenticación", "prioridad": "Media", "tipo": "Funcional / negativa",
        "titulo": "Bloqueo de acceso para un usuario inhabilitado",
        "precondiciones": "Navegador abierto en la página de inicio de sesión.",
        "datos": "Usuario: locked_out_user; contraseña pública de demostración.",
        "pasos": "1. Abrir la página de inicio.\n2. Digitar usuario bloqueado y contraseña.\n3. Presionar «Login».",
        "esperado": "Mensaje «Sorry, this user has been locked out.» y sin acceso al catálogo.",
        "prueba": "tests/test_01_login.py::test_usuario_bloqueado",
    },
    {
        "id": "CP-04", "modulo": "Catálogo", "prioridad": "Alta", "tipo": "Funcional / datos",
        "titulo": "Nombres y precios del catálogo coinciden con los datos de referencia",
        "precondiciones": "Sesión iniciada con standard_user.",
        "datos": "Catálogo de referencia: 6 productos con su precio en USD.",
        "pasos": "1. Iniciar sesión.\n2. Leer nombre y precio de cada producto.\n3. Comparar con la referencia.",
        "esperado": "Los 6 productos y sus precios coinciden con los datos de referencia.",
        "prueba": "tests/test_02_catalogo.py::test_catalogo_coincide_con_datos_publicados",
    },
    {
        "id": "CP-05", "modulo": "Catálogo", "prioridad": "Media", "tipo": "Funcional",
        "titulo": "Ordenamiento del catálogo por nombre y por precio",
        "precondiciones": "Sesión iniciada con el usuario de la combinación.",
        "datos": "standard_user con az, za, lohi, hilo; problem_user con lohi.",
        "pasos": "1. Iniciar sesión.\n2. Elegir el criterio de orden.\n3. Leer la lista mostrada.",
        "esperado": "La lista mostrada está ordenada según el criterio elegido.",
        "prueba": "tests/test_02_catalogo.py::test_ordenamiento_de_productos",
    },
    {
        "id": "CP-06", "modulo": "Carrito", "prioridad": "Alta", "tipo": "Funcional / humo",
        "titulo": "Agregar y quitar productos del carrito",
        "precondiciones": "Sesión iniciada con standard_user y carrito vacío.",
        "datos": "Sauce Labs Backpack y Sauce Labs Bike Light.",
        "pasos": "1. Agregar 2 productos.\n2. Revisar contador y carrito.\n3. Quitar 1 producto.\n4. Revisar contador y carrito.",
        "esperado": "Contador 0 → 2 → 1; el carrito lista exactamente los productos agregados.",
        "prueba": "tests/test_03_carrito.py::test_agregar_y_quitar_productos",
    },
    {
        "id": "CP-07", "modulo": "Compra", "prioridad": "Alta", "tipo": "Funcional / extremo a extremo",
        "titulo": "Compra completa con cálculo de subtotal, impuesto y total",
        "precondiciones": "Sesión iniciada con standard_user.",
        "datos": "Backpack (29.99) + Bike Light (9.99); impuesto 8 %; comprador Ana Pérez, CP 10101.",
        "pasos": "1. Agregar productos.\n2. Ir al carrito y pagar.\n3. Completar datos.\n4. Revisar el resumen.\n5. Finalizar.",
        "esperado": "Subtotal 39.98, impuesto 3.20, total 43.18 y mensaje «Thank you for your order!».",
        "prueba": "tests/test_04_checkout.py::test_compra_completa_con_totales_correctos",
    },
    {
        "id": "CP-08", "modulo": "Compra", "prioridad": "Media", "tipo": "Funcional / negativa",
        "titulo": "Validación de campos obligatorios del comprador",
        "precondiciones": "Sesión iniciada y un producto en el carrito.",
        "datos": "3 combinaciones: sin nombre, sin apellido y sin código postal.",
        "pasos": "1. Ir al formulario de compra.\n2. Dejar vacío un campo.\n3. Presionar «Continue».",
        "esperado": "Mensaje «Error: <campo> is required» y el usuario permanece en el formulario.",
        "prueba": "tests/test_04_checkout.py::test_datos_de_envio_obligatorios",
    },
    {
        "id": "CP-09", "modulo": "Sesión", "prioridad": "Media", "tipo": "Funcional / seguridad",
        "titulo": "Cierre de sesión y bloqueo del catálogo sin autenticación",
        "precondiciones": "Sesión iniciada con standard_user.",
        "datos": "Ruta protegida /inventory.html.",
        "pasos": "1. Abrir el menú y cerrar sesión.\n2. Ingresar directamente a /inventory.html.",
        "esperado": "Regresa al inicio de sesión y se muestra el mensaje de acceso restringido.",
        "prueba": "tests/test_05_sesion.py::test_cierre_de_sesion_protege_el_catalogo",
    },
]

AZUL = PatternFill("solid", start_color="1F3864")
GRIS = PatternFill("solid", start_color="F2F2F2")
VERDE = PatternFill("solid", start_color="E2EFDA")
ROJO = PatternFill("solid", start_color="FCE4D6")
BORDE = Border(*(Side(style="thin", color="BFBFBF"),) * 4)
FUENTE = Font(name="Arial", size=10)
FUENTE_ENCABEZADO = Font(name="Arial", size=10, bold=True, color="FFFFFF")


def _encabezados(hoja, titulos, anchos, fila=1):
    for col, (titulo, ancho) in enumerate(zip(titulos, anchos), start=1):
        celda = hoja.cell(row=fila, column=col, value=titulo)
        celda.font, celda.fill, celda.border = FUENTE_ENCABEZADO, AZUL, BORDE
        celda.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        hoja.column_dimensions[get_column_letter(col)].width = ancho
    hoja.freeze_panes = hoja.cell(row=fila + 1, column=1)


def _fila(hoja, fila, valores, relleno=None):
    for col, valor in enumerate(valores, start=1):
        celda = hoja.cell(row=fila, column=col, value=valor)
        celda.font, celda.border = FUENTE, BORDE
        celda.alignment = Alignment(vertical="top", wrap_text=True)
        if relleno:
            celda.fill = relleno


def generar():
    datos = json.loads(RESULTADOS.read_text(encoding="utf-8")) if RESULTADOS.exists() else None
    resultados = datos["resultados"] if datos else []
    libro = Workbook()

    # ---------------------------------------------------------------- Ejecución
    ejecucion = libro.active
    ejecucion.title = "Ejecución"
    _encabezados(
        ejecucion,
        ["Caso", "Prueba automatizada", "Resultado", "Duración (s)", "Verificaciones", "Cumplen", "Mensaje", "Evidencia"],
        [8, 52, 11, 11, 13, 10, 60, 58],
    )
    orden = {c["id"]: i for i, c in enumerate(CASOS)}
    resultados = sorted(resultados, key=lambda r: (orden.get(r["caso"], 99), r["prueba"]))
    for i, r in enumerate(resultados, start=2):
        relleno = VERDE if r["resultado"] == "Aprobada" else ROJO if r["resultado"] == "Fallida" else None
        _fila(
            ejecucion, i,
            [r["caso"], r["prueba"], r["resultado"], r["duracion_s"], len(r["verificaciones"]),
             sum(v["cumple"] for v in r["verificaciones"]), r["mensaje"], "reports/" + r["captura"] if r["captura"] else ""],
            relleno,
        )
    ultima = max(len(resultados) + 1, 2)

    # ---------------------------------------------------------------- Verificaciones
    verif = libro.create_sheet("Verificaciones")
    _encabezados(verif, ["Caso", "Prueba automatizada", "Verificación", "Esperado", "Obtenido", "¿Cumple?"], [8, 46, 38, 44, 44, 10])
    fila = 2
    for r in resultados:
        for v in r["verificaciones"]:
            _fila(verif, fila, [r["caso"], r["prueba"], v["descripcion"], v["esperado"], v["obtenido"], "Sí" if v["cumple"] else "No"],
                  None if v["cumple"] else ROJO)
            fila += 1

    # ---------------------------------------------------------------- Casos de prueba
    casos = libro.create_sheet("Casos de prueba", 0)
    _encabezados(
        casos,
        ["ID", "Módulo", "Título", "Precondiciones", "Datos de prueba", "Pasos", "Resultado esperado", "Prioridad",
         "Tipo", "Automatizado", "Prueba automatizada", "Ejecuciones", "Aprobadas", "Fallidas", "Estado", "Defecto asociado"],
        [8, 13, 30, 24, 30, 34, 34, 10, 16, 12, 40, 11, 11, 10, 12, 30],
    )
    rango_caso = f"'Ejecución'!$A$2:$A${ultima}"
    rango_res = f"'Ejecución'!$C$2:$C${ultima}"
    for i, c in enumerate(CASOS, start=2):
        defecto = ""
        if c["id"] == "CP-05" and any(r["caso"] == "CP-05" and r["resultado"] == "Fallida" for r in resultados):
            defecto = "DEF-01: con problem_user el ordenamiento no cambia el orden de la lista."
        _fila(casos, i, [
            c["id"], c["modulo"], c["titulo"], c["precondiciones"], c["datos"], c["pasos"], c["esperado"],
            c["prioridad"], c["tipo"], "Sí", c["prueba"],
            f'=COUNTIF({rango_caso},A{i})',
            f'=COUNTIFS({rango_caso},A{i},{rango_res},"Aprobada")',
            f'=COUNTIFS({rango_caso},A{i},{rango_res},"Fallida")',
            f'=IF(L{i}=0,"Pendiente",IF(N{i}>0,"Fallido","Aprobado"))',
            defecto,
        ])
    for col in "LMN":
        for i in range(2, len(CASOS) + 2):
            casos[f"{col}{i}"].alignment = Alignment(horizontal="center", vertical="top")
    lista = DataValidation(type="list", formula1='"Alta,Media,Baja"', allow_blank=True)
    casos.add_data_validation(lista)
    lista.add(f"H2:H{len(CASOS) + 1}")

    # ---------------------------------------------------------------- Resumen
    resumen = libro.create_sheet("Resumen", 1)
    resumen.column_dimensions["A"].width = 30
    resumen.column_dimensions["B"].width = 42
    resumen["A1"] = "Resumen de la ejecución"
    resumen["A1"].font = Font(name="Arial", size=13, bold=True)
    entorno = datos["entorno"] if datos else {}
    filas = [
        ("Sitio bajo prueba", entorno.get("url_base", "")),
        ("Navegador", f"{entorno.get('navegador', '')} {entorno.get('version_navegador', '')} ({entorno.get('modo', '')})".strip()),
        ("Sistema operativo", entorno.get("sistema_operativo", "")),
        ("Python / Selenium / pytest",
         f"{entorno.get('python', '')} / {entorno.get('selenium', '')} / {entorno.get('pytest', '')}"),
        ("Inicio de la ejecución", entorno.get("inicio", "")),
        ("Fin de la ejecución", entorno.get("fin", "")),
        ("Casos de prueba diseñados", f"=COUNTA('Casos de prueba'!A2:A{len(CASOS) + 1})"),
        ("Ejecuciones (casos parametrizados)", f"=COUNTA('Ejecución'!A2:A{ultima})"),
        ("Ejecuciones aprobadas", f"=COUNTIF('Ejecución'!C2:C{ultima},\"Aprobada\")"),
        ("Ejecuciones fallidas", f"=COUNTIF('Ejecución'!C2:C{ultima},\"Fallida\")"),
        ("Porcentaje de aprobación", "=IF(B10=0,0,B11/B10)"),
        ("Verificaciones esperado vs. obtenido", f"=COUNTA('Verificaciones'!A2:A{max(fila - 1, 2)})"),
        ("Verificaciones que no cumplen", f"=COUNTIF('Verificaciones'!F2:F{max(fila - 1, 2)},\"No\")"),
        ("Duración total de las pruebas (s)", f"=SUM('Ejecución'!D2:D{ultima})"),
    ]
    for i, (etiqueta, valor) in enumerate(filas, start=3):
        _fila(resumen, i, [etiqueta, valor])
        resumen.cell(row=i, column=1).fill = GRIS
        resumen.cell(row=i, column=1).font = Font(name="Arial", size=10, bold=True)
    resumen["B13"].number_format = "0.0%"
    resumen["B16"].number_format = "0.00"
    resumen["A18"] = "Fuente: reports/resultados.json generado por pytest en la última ejecución."
    resumen["A18"].font = Font(name="Arial", size=9, italic=True)

    SALIDA.parent.mkdir(exist_ok=True)
    libro.save(SALIDA)
    return SALIDA


if __name__ == "__main__":
    print(f"Matriz generada: {generar()}")
