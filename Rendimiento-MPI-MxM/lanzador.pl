#!/usr/bin/perl
use strict;
use warnings;
use Time::HiRes qw(gettimeofday tv_interval);

my $hostfile       = "filehost";
my $programa       = "./mxmOmpMPIfxc";

# Batería ajustada
my @tam_matrices   = (512, 1024);
my @num_procesos   = (2, 3);      # np=2 -> 1 worker, np=3 -> 2 workers
my @num_hilos      = (1, 2, 4);   # 4 CPUs
my $repeticiones   = 30;
my $timeout_seg    = 60;

my $archivo_salida = "resultados_reducidos.csv";

print "=" x 60 . "\n";
print " Lanzador MPI + OpenMP (bateria reducida)\n";
print "=" x 60 . "\n";

open(my $fh, '>', $archivo_salida)
    or die "No se pudo crear '$archivo_salida': $!\n";

print $fh "tamMatriz,np,workers,hilos,repeticion,tiempo_seg,estado\n";

my $total_combos = 0;

foreach my $tam (@tam_matrices) {
    foreach my $np (@num_procesos) {
        my $workers = $np - 1;

        next if $workers < 1;
        next if ($tam % $workers != 0);

        foreach my $hilos (@num_hilos) {
            $total_combos++;
        }
    }
}

my $total_ejecuciones = $total_combos * $repeticiones;

print "Combinaciones: $total_combos\n";
print "Ejecuciones  : $total_ejecuciones\n\n";

my $combo_actual = 0;

foreach my $tam (@tam_matrices) {
    foreach my $np (@num_procesos) {
        my $workers = $np - 1;

        next if $workers < 1;
        next if ($tam % $workers != 0);

        foreach my $hilos (@num_hilos) {
            $combo_actual++;

            print "-" x 50 . "\n";
            print "Combo $combo_actual/$total_combos -> tam=$tam, np=$np, workers=$workers, hilos=$hilos\n";

            for my $rep (1 .. $repeticiones) {
                my $cmd = "env -u DISPLAY -u XAUTHORITY " .
                          "OMP_NUM_THREADS=$hilos " .
                          "timeout $timeout_seg " .
                          "mpirun --hostfile $hostfile -np $np $programa $tam $hilos";

                my $inicio = [gettimeofday];
                my $rc = system($cmd);
                my $tiempo = tv_interval($inicio);
                my $tiempo_fmt = sprintf("%.6f", $tiempo);

                my $estado = "OK";
                if ($rc == -1) {
                    $estado = "ERROR";
                } else {
                    my $exit_code = $rc >> 8;
                    if ($exit_code == 124) {
                        $estado = "TIMEOUT";
                    } elsif ($exit_code != 0) {
                        $estado = "ERROR";
                    }
                }

                print $fh "$tam,$np,$workers,$hilos,$rep,$tiempo_fmt,$estado\n";

                if ($rep % 10 == 0 || $rep == $repeticiones) {
                    print "  Rep $rep/$repeticiones -> $tiempo_fmt s [$estado]\n";
                }
            }
        }
    }
}

close($fh);

print "\n" . "=" x 60 . "\n";
print " Experimentos finalizados\n";
print " Resultados: $archivo_salida\n";
print "=" x 60 . "\n";
