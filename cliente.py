"""Cliente de consola para la API de tareas (requiere: pip install requests)."""
import os
import re
import tempfile
import webbrowser

import requests

URL = "http://127.0.0.1:5000"
sesion = requests.Session()  # mantiene la cookie de sesión tras el login


def pedir_datos():
    return {"usuario": input("Usuario: ").strip(), "contraseña": input("Contraseña: ")}


def mostrar(resp):
    try:
        print(f"[{resp.status_code}]", resp.json())
    except ValueError:
        mostrar_html(resp)


def mostrar_html(resp):
    """La terminal no interpreta HTML: se muestra el texto limpio y la página se abre en el navegador."""
    html = resp.text
    texto = re.sub(r"<(style|script).*?</\1>", "", html, flags=re.S)  # saca CSS y scripts
    texto = re.sub(r"<[^>]+>", " ", texto)                            # saca las etiquetas
    texto = re.sub(r"\s+", " ", texto).strip()
    print(f"[{resp.status_code}] {texto}")

    # Se guarda en un archivo temporal y se abre en el navegador para verla con su diseño
    ruta = os.path.join(tempfile.gettempdir(), "bienvenida_tareas.html")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(html)
    webbrowser.open("file://" + ruta)
    print("(Se abrió la página de bienvenida en tu navegador)")


def main():
    while True:
        print("\n1) Registrarse  2) Iniciar sesión  3) Ver tareas  4) Salir")
        op = input("Opción: ").strip()
        try:
            if op == "1":
                mostrar(sesion.post(f"{URL}/registro", json=pedir_datos()))
            elif op == "2":
                mostrar(sesion.post(f"{URL}/login", json=pedir_datos()))
            elif op == "3":
                mostrar(sesion.get(f"{URL}/tareas"))
            elif op == "4":
                break
            else:
                print("Opción inválida")
        except requests.ConnectionError:
            print("No se pudo conectar. ¿Está corriendo servidor.py?")


if __name__ == "__main__":
    main()
