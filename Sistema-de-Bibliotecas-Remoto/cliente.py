import grpc
import sys

import biblioteca_pb2
import biblioteca_pb2_grpc


def main():
    # por defecto conecta a localhost, pero se puede pasar la ip como argumento
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    puerto = sys.argv[2] if len(sys.argv) > 2 else "50051"

    canal = grpc.insecure_channel(f"{host}:{puerto}")
    stub = biblioteca_pb2_grpc.BibliotecaStub(canal)

    print(f"Conectado a {host}:{puerto}")

    while True:
        print("\n--- Menu ---")
        print("1. Prestamo por ISBN")
        print("2. Prestamo por titulo")
        print("3. Consultar libro")
        print("4. Devolucion")
        print("0. Salir")

        op = input("Opcion: ").strip()

        if op == "0":
            break

        elif op == "1":
            isbn = input("ISBN: ").strip()
            resp = stub.PrestamoPorISBN(biblioteca_pb2.SolicitudISBN(isbn=isbn))
            if resp.aprobado:
                print(f"Aprobado! Devolver antes del {resp.fecha_devolucion}")
            else:
                print(f"Rechazado: {resp.mensaje}")

        elif op == "2":
            titulo = input("Titulo: ").strip()
            resp = stub.PrestamoPorTitulo(biblioteca_pb2.SolicitudTitulo(titulo=titulo))
            if resp.aprobado:
                print(f"Aprobado! Devolver antes del {resp.fecha_devolucion}")
            else:
                print(f"Rechazado: {resp.mensaje}")

        elif op == "3":
            isbn = input("ISBN: ").strip()
            resp = stub.Consulta(biblioteca_pb2.SolicitudISBN(isbn=isbn))
            if resp.encontrado:
                print(f"Titulo: {resp.titulo}")
                print(f"Autor: {resp.autor}")
                print(f"Disponibles: {resp.disponibles} de {resp.total}")
            else:
                print("Libro no encontrado")

        elif op == "4":
            isbn = input("ISBN: ").strip()
            resp = stub.Devolucion(biblioteca_pb2.SolicitudISBN(isbn=isbn))
            if resp.ok:
                print(f"Devolucion exitosa: {resp.mensaje}")
            else:
                print(f"Error: {resp.mensaje}")

        else:
            print("Opcion invalida")


if __name__ == "__main__":
    main()
