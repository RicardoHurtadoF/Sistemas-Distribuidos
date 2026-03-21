import grpc
import json
import threading
from concurrent import futures
from datetime import date, timedelta

import biblioteca_pb2
import biblioteca_pb2_grpc

ARCHIVO_DB = "libros.json"
lock = threading.Lock()  # para que no se dañe el archivo si hay varios clientes


def leer_libros():
    with open(ARCHIVO_DB, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_libros(libros):
    with open(ARCHIVO_DB, "w", encoding="utf-8") as f:
        json.dump(libros, f, ensure_ascii=False, indent=2)


def buscar_isbn(libros, isbn):
    for i, libro in enumerate(libros):
        if libro["isbn"] == isbn:
            return i, libro
    return None, None


def buscar_titulo(libros, titulo):
    # busqueda sin importar mayusculas
    for i, libro in enumerate(libros):
        if titulo.lower() in libro["titulo"].lower():
            return i, libro
    return None, None


class BibliotecaServicer(biblioteca_pb2_grpc.BibliotecaServicer):

    def PrestamoPorISBN(self, request, context):
        print(f"[prestamo isbn] {request.isbn}")
        with lock:
            libros = leer_libros()
            i, libro = buscar_isbn(libros, request.isbn)

            if libro is None:
                return biblioteca_pb2.RespuestaPrestamo(
                    aprobado=False,
                    mensaje="No existe ese libro"
                )

            disp = libro["total"] - libro["prestados"]
            if disp <= 0:
                return biblioteca_pb2.RespuestaPrestamo(
                    aprobado=False,
                    mensaje=f"No hay ejemplares disponibles de '{libro['titulo']}'"
                )

            libros[i]["prestados"] += 1
            guardar_libros(libros)

            fecha = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
            return biblioteca_pb2.RespuestaPrestamo(
                aprobado=True,
                mensaje=f"Prestamo aprobado: '{libro['titulo']}'",
                fecha_devolucion=fecha
            )

    def PrestamoPorTitulo(self, request, context):
        print(f"[prestamo titulo] {request.titulo}")
        with lock:
            libros = leer_libros()
            i, libro = buscar_titulo(libros, request.titulo)

            if libro is None:
                return biblioteca_pb2.RespuestaPrestamo(
                    aprobado=False,
                    mensaje="No existe ese libro"
                )

            disp = libro["total"] - libro["prestados"]
            if disp <= 0:
                return biblioteca_pb2.RespuestaPrestamo(
                    aprobado=False,
                    mensaje=f"No hay ejemplares disponibles de '{libro['titulo']}'"
                )

            libros[i]["prestados"] += 1
            guardar_libros(libros)

            fecha = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
            return biblioteca_pb2.RespuestaPrestamo(
                aprobado=True,
                mensaje=f"Prestamo aprobado: '{libro['titulo']}'",
                fecha_devolucion=fecha
            )

    def Consulta(self, request, context):
        print(f"[consulta] {request.isbn}")
        libros = leer_libros()
        i, libro = buscar_isbn(libros, request.isbn)

        if libro is None:
            return biblioteca_pb2.RespuestaConsulta(encontrado=False)

        return biblioteca_pb2.RespuestaConsulta(
            encontrado=True,
            titulo=libro["titulo"],
            autor=libro["autor"],
            total=libro["total"],
            disponibles=libro["total"] - libro["prestados"]
        )

    def Devolucion(self, request, context):
        print(f"[devolucion] {request.isbn}")
        with lock:
            libros = leer_libros()
            i, libro = buscar_isbn(libros, request.isbn)

            if libro is None:
                return biblioteca_pb2.RespuestaDevolucion(
                    ok=False,
                    mensaje="No existe ese libro"
                )

            if libro["prestados"] == 0:
                return biblioteca_pb2.RespuestaDevolucion(
                    ok=False,
                    mensaje="Ese libro no tiene prestamos activos"
                )

            libros[i]["prestados"] -= 1
            guardar_libros(libros)

            return biblioteca_pb2.RespuestaDevolucion(
                ok=True,
                mensaje=f"Devolucion registrada: '{libro['titulo']}'"
            )


def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    biblioteca_pb2_grpc.add_BibliotecaServicer_to_server(BibliotecaServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Servidor corriendo en el puerto 50051...")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Servidor detenido")
        server.stop(0)


if __name__ == "__main__":
    main()
