"""Cliente de consola para la API de tareas (requiere: pip install requests)."""
import requests

URL = "http://127.0.0.1:5000"
sesion = requests.Session()  # mantiene la cookie de sesión tras el login


def pedir_datos():
    return {"usuario": input("Usuario: ").strip(), "contraseña": input("Contraseña: ")}


def mostrar(resp):
    try:
        print(f"[{resp.status_code}]", resp.json())
    except ValueError:
        print(f"[{resp.status_code}]\n{resp.text}")


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
