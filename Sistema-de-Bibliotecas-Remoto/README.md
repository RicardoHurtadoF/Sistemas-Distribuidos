# Taller gRPC - Sistema de Biblioteca

Taller de Introducción a Sistemas Distribuidos - Javeriana 2026  
Autor:Ricardo Hurtado

---

Servidor gRPC que maneja prestamos de libros. El cliente se conecta y puede:
- Pedir prestado un libro por ISBN
- Pedir prestado un libro por titulo
- Consultar si un libro esta disponible
- Registrar una devolucion

Los libros se guardan en libros.json que hace de base de datos.

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

primero se descarga el taller_grpc_biblioteca.zip


debes estar en la carpeta donde estan los archivos
```bash
cd taller_grpc
```

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
- 
si vas a probar servidor y cliente en el mismo computador no necesitas la IP, usa simplemente localhost:
```bash
python cliente.py localhost 50051
```
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
