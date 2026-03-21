# Evaluación de Rendimiento MPI — Multiplicación de Matrices

**Pontificia Universidad Javeriana**  
Departamento de Ingeniería de Sistemas — Sistemas Distribuidos  
Febrero 2026

---

## Descripción

Implementación y evaluación de rendimiento de la multiplicación de matrices cuadradas (N×N) usando un modelo de paralelismo híbrido **MPI + OpenMP**. Se comparan dos algoritmos:

- **FxC** — Filas × Columnas (`mxmOmpMPIfxc`)
- **FxT** — Filas × Transpuesta (`mxmOmpMPIfxt`)

MPI distribuye filas de la matriz A entre nodos del clúster; OpenMP paraleliza el cómputo dentro de cada nodo mediante hilos.

---

## Estructura del proyecto

```
evalMxM_MPI/
├── moduloMPI.h          # Cabecera: prototipos de todas las funciones auxiliares
├── moduloMPI.c          # Módulo compartido: inicialización, multiplicación, tiempo, validaciones
├── mxmOmpMPIfxc.c       # Programa principal: algoritmo Filas × Columnas
├── mxmOmpMPIfxt.c       # Programa principal: algoritmo Filas × Transpuesta
├── Makefile             # Compilación de ambos ejecutables
├── lanzador.pl          # Script Perl para automatizar la batería de experimentos
├── filehost             # Archivo de nodos del clúster (IPs y slots)
├── resultados.csv       # Resultados completos de la batería de experimentos
└── resultados_reducidos.csv  # Resultados de la batería reducida
```

---

## Requisitos

- SO Linux (nativo o máquina virtual)
- OpenMPI: `sudo apt install openmpi-bin openmpi-common libopenmpi-dev`
- Compilador MPI con soporte OpenMP (`mpicc` con flag `-fopenmp`)
- Perl con módulo `Time::HiRes` (incluido en la mayoría de instalaciones)
- Sistema de ficheros compartido entre nodos (NFS recomendado)

---

## Compilación

```bash
make
```

Esto compila ambos ejecutables:

```bash
mpicc -o mxmOmpMPIfxc mxmOmpMPIfxc.c moduloMPI.c -lm -fopenmp
mpicc -o mxmOmpMPIfxt mxmOmpMPIfxt.c moduloMPI.c -lm -fopenmp
```

Para limpiar los binarios:

```bash
make clean
```

---

## Ejecución manual

```bash
mpirun -hostfile filehost -np <numProcesos> ./mxmOmpMPIfxc <DimMatriz> <NumHilos>
mpirun -hostfile filehost -np <numProcesos> ./mxmOmpMPIfxt <DimMatriz> <NumHilos>
```

**Parámetros:**

| Parámetro     | Descripción                                              |
|---------------|----------------------------------------------------------|
| `numProcesos` | Total de procesos MPI (1 MASTER + N workers)             |
| `DimMatriz`   | Dimensión N de la matriz cuadrada N×N                    |
| `NumHilos`    | Número de hilos OpenMP por worker                        |

**Restricción:** `DimMatriz` debe ser divisible por `numProcesos - 1` (número de workers). El programa aborta con mensaje de error si no se cumple.

**Ejemplo:**

```bash
mpirun -hostfile filehost -np 3 ./mxmOmpMPIfxc 1024 4
```

Ejecuta con 2 workers, matrices de 1024×1024, 4 hilos OpenMP por worker.

---

## Archivo filehost

Define los nodos del clúster y la cantidad de slots (cores) disponibles en cada uno:

```
10.43.99.126    slots=4
10.43.99.70     slots=4
```

Editar este archivo para agregar o quitar nodos antes de ejecutar.

---

## Automatización con lanzador.pl

El script Perl itera sobre todas las combinaciones de tamaño de matriz, procesos MPI e hilos OpenMP, ejecuta cada combinación 30 veces y guarda los resultados en un CSV.

```bash
perl lanzador.pl
```

**Variables configurables al inicio del script:**

| Variable          | Valor por defecto        | Descripción                              |
|-------------------|--------------------------|------------------------------------------|
| `$hostfile`       | `"filehost"`             | Archivo de nodos del clúster             |
| `$programa`       | `"./mxmOmpMPIfxc"`       | Ejecutable a lanzar (cambiar para FxT)   |
| `@tam_matrices`   | `(512, 1024)`            | Dimensiones N a evaluar                  |
| `@num_procesos`   | `(2, 3)`                 | Valores de `-np` para mpirun             |
| `@num_hilos`      | `(1, 2, 4)`              | Hilos OpenMP por worker                  |
| `$repeticiones`   | `30`                     | Ejecuciones por combinación              |
| `$timeout_seg`    | `60`                     | Límite de tiempo por ejecución (segundos)|
| `$archivo_salida` | `"resultados_reducidos.csv"` | Archivo CSV de salida               |

**Formato de salida CSV:**

```
tamMatriz, np, workers, hilos, repeticion, tiempo_seg, estado
512, 2, 1, 1, 1, 1.538788, OK
```

Los estados posibles son `OK`, `TIMEOUT` y `ERROR`. Solo las filas con estado `OK` se incluyen en el análisis estadístico.

con cambiar el programa objetivo y el nombre del csv desde el lanzador.pl se puede elejir cual de los dos programas usar.


---

## Algoritmos implementados

### FxC — Filas × Columnas (`mxmOmpFxC`)

Algoritmo clásico. Cada worker multiplica su tajada de filas de A por las columnas de B. El acceso a B es por columnas (stride = N), lo que genera **cache misses frecuentes**.

### FxT — Filas × Transpuesta (`mxmOmpFxT`)

Antes de multiplicar, transpone B en un buffer local `mT`. El producto se calcula como fila de A × fila de `mT`, con **acceso contiguo en ambas matrices** (stride = 1). Mejor localidad de caché que FxC a costa de memoria adicional (O(N²)).

con cambiar el pro

---

## Métricas de rendimiento

- **Speedup:** `S = T_serie / T_paralelo`
- **Eficiencia:** `E = S / (workers × hilos)`

El tiempo se mide en microsegundos con `gettimeofday()`, cubriendo desde el `MPI_Bcast` de B hasta el último `MPI_Recv` del MASTER.
