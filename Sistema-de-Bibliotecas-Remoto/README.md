# Taller gRPC - Sistema de Biblioteca

Taller de Introducción a Sistemas Distribuidos - Javeriana 2026  
Autor:Ricardo Hurtado

---

Servidor gRPC que maneja prestamos de libros. El cliente se conecta y puede:
- Pedir prestado un libro por ISBN
- Pedir prestado un libro por titulo
- Consultar si un libro esta disponible
- Registrar una devolucion

Los libros se guardan en libros.json que hace las veces de base de datos.

## Archivos

```
biblioteca.proto        <- define los servicios y mensajes
servidor.py             <- el servidor gRPC
cliente.py              <- el cliente
libros.json             <- los libros
biblioteca_pb2.py       <- generado automaticamente, no tocar
biblioteca_pb2_grpc.py  <- generado automaticamente, no tocar
```

## Como correrlo

**Primero instalar dependencias y generar el codigo:**

```bash
pip install grpcio grpcio-tools
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. biblioteca.proto
```

**Computador A - servidor:**

```bash
python servidor.py
```

**Computador B - cliente:**

```bash
python cliente.py 192.168.X.X 50051
```

Reemplazar la IP con la del servidor. Para saber la IP del servidor:
- Windows: `ipconfig`
- Linux: `hostname -I`

Si es en la misma maquina usar `localhost`.

## Libros de prueba

| ISBN | Titulo | Disponibles |
|------|--------|-------------|
| 978-0-13-468599-1 | Clean Code | 2 de 3 |
| 978-0-13-235088-4 | The Pragmatic Programmer | 2 de 2 |
| 978-0-596-51774-8 | Python Cookbook | 0 de 4 (todos prestados) |
| 978-0-13-110362-7 | The C Programming Language | 2 de 2 |
| 978-0-201-63361-0 | Design Patterns | 2 de 3 |

######
Python Cookbook sirve para el caso de rechazo.
Todas las operaciones son sincronas.
La fecha de devolucion es 7 dias despues del prestamo.
