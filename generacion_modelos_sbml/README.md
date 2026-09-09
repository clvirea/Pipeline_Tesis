# Generación de modelos SBML

Esta carpeta contiene el pipeline para generar los modelos metabólicos (SBML) 
a partir de los metagenomas anotados de cada sitio, usando `emapper2gbk`, 
`mpwt` (Pathway Tools) y `padmet_utils`.

## Archivos

- `generar_chunks_correctos.sh`: script plantilla que divide los archivos 
  de anotación (.faa, .fna, .annotations) en chunks manejables por Pathway 
  Tools, genera los GBK, corre mpwt, fusiona a PADMET y exporta al formato final SBML.
  Solo se incluyen los genes con anotación funcional.
    
- `parametros_por_sitio.md`: tabla con los valores usados (N_CHUNKS, archivos 
  base, número de genes) para cada uno de los 8 sitios, ya que el script se 
  modifica manualmente por sitio.

## Cómo se usa

Por cada sitio se copia el script, se reemplazan las rutas de entrada 
(fna/faa/annotations) y se ajusta `N_CHUNKS` según el número de genes del 
sitio (aprox. genes / 41.000; este número fue el tamaño definido empíricamente en la primera 
corrida: sitio Ilque, N_CHUNKS=5). 

Los datos de entrada (fna/faa/anotaciones) están disponibles en: [https://drive.google.com/drive/u/3/folders/1_sEGeOHrAnkgh3px7VRD88SxQoieFjvA].
OBS:Añadir SBMLs a Github o dejar en Drive??
