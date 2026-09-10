# Parámetros por sitio

Cada sitio requiere ajustar `N_CHUNKS` en el script `generar_chunks_correctos.sh` según 
el número de genes anotados, manteniendo un tamaño de chunk cercano a 41.000 
genes (ver README de esta carpeta para el detalle de por qué). Estos valores se copiaron desde los logs obtenidos al momento de correr el script.

| Sitio | Archivo base | N_CHUNKS | Genes totales anotados |
|---|---|---|---|
| Las Docas | doc_contigs.fasta.db. | 34 | 1.404.601 |
| Algarrobo | al_contigs.fasta.db. | 38 | 2.259.334 |
| San Antonio | sant_contigs.fasta.db. | 40 | 1.643.218 |
| Topocalma | top_contigs.fasta.db. | 49 | 1.398.385 |
| Ilque | ilq_contigs.fasta.db. | 5 | 207.463 |
| Navidad | nav_contigs.fasta.db. | 23 | 664.006 |
| Pargua | par_contigs.fasta.db. | 48 | 1.045.315 |
| Los Chonos | lc_contigs.fasta.db. | 46 | 1.866.766 |
