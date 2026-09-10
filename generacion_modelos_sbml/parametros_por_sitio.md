# Parámetros por sitio

Cada sitio requiere ajustar `N_CHUNKS` en el script `generar_chunks_correctos.sh` según 
el número de genes anotados, manteniendo un tamaño de chunk cercano a 41.000 
genes (ver README de esta carpeta para el detalle de por qué), considerando que "N genes / N_CHUNKS = tamaño de chunk resultante". Estos valores se copiaron desde los logs obtenidos al momento de correr el script, que se pueden encontrar en la carpeta `logs`. Los archivos base corresponden a estos formatos: "sitio_contigs.fasta.db.faa", "sitio_contigs.fasta.db.fna" y "sitio_contigs.fasta.db.faa.emapper6.emapper.annotations". El número de genes totales anotados no es el total de genes predichos en el metagenoma, sino los genes que eggNOG-mapper logró anotar funcionalmente (es decir, el número de líneas del archivo de anotaciones).

| Sitio | Archivos base | N_CHUNKS | Genes totales anotados 
|---|---|---|---|
| Las Docas | doc_contigs.fasta.db... | 34 | 971.602 |
| Algarrobo | al_contigs.fasta.db... | 38 | 1.560.107 |
| San Antonio | sant_contigs.fasta.db... | 40 | 734.722 |
| Topocalma | top_contigs.fasta.db... | 49 | 1.398.385 |
| Ilque | ilq_contigs.fasta.db... | 5 | 207.463 |
| Navidad | nav_contigs.fasta.db... | 23 | 664.006 |
| Pargua | par_contigs.fasta.db... | 48 | 1.045.315 |
| Los Chonos | chon_contigs.fasta.db... | 46 | 1.866.766 |
