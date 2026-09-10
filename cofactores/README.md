# Curación con cofactores

Esta carpeta contiene el pipeline de curación de los modelos metabólicos (SBML) generados en `generacion_modelos_sbml/`, usando una semilla de cofactores para detectar y eliminar reacciones que generan fugas de metabolitos no-cofactor.
Este metodología se aplicó en el trabajo de Ulloa, et al. (2026) y fue inspirado a partir de lo expuesto por Saadat, et al., 2022. (doi: 10.3390/metabo12040275)

## Archivos

- `cofactors.tsv` TSV utilizado en el trabajo de Ulloa, et al. (2026) para la curación de MAGs. Contiene 30 pares de metabolitos que aparecen en reacciones en su versión oxidada y reducida. Obs: el metabolito "ATP_c" aparece dos veces.  
- `seed_cofactors.sbml`: semilla que contiene los metabolitos cofactores (cone el tag "_cof_") expuestos en el TSV.
- `cofactores_metagenomas.py`: script de curación. No carga los modelos vía Cobra (esto es demasiado lento para modelos de metagenomas); trabaja directamente con los SBML. Aquí se duplican las reacciones donde se identifican los pares de cofactores, y se renombra tanto el nombre de la reacción como el de los metabolitos añadiendo el sufijo "_cof_"
- `cofactores_oficial_v2.ipynb`: cuadernillo final donde se ejecuta `cofactores_metagenomas.py` con el TSV y se testea el scope con semillas sobre los 8 modelos curados. El modelo queda guardado en la carpeta `sbml_curado` en: https://drive.google.com/drive/folders/1it7D4Ucdo8WPooAbmDJR0UT93wKm-yeQ?usp=sharing   
- `test_cofactores_v2_i.ipynb`: test post-curación (parte 1). Corre semillas triviales (OnlyWater, OnlyAMP, OnlyPPI, OnlyProton, OnlyNothing) para verificar que el scope y las reacciones activadas son coherentes en los 8 modelos. Luego calcula el scope con la semilla de solo cofactores (metabolitos con tag `_cof_`) y se detectan fugas hacia metabolitos sin ese tag, y se identifican así las reacciones "madre" responsables (reacciones con metabolitos `_cof_` que producen metabolitos sin el tag), guardadas en un archivo JSON. Las semillas se encuentran en la carpeta: https://drive.google.com/drive/folders/1yVp0tjO231X4aMIOue74VSUEu2F_g30P?usp=sharing. 
- `test_cofactores_v2_ii.ipynb`: test post-curación (parte 2, para ahorrar recursos). Carga el JSON de reacciones "madre", las elimina, guardando el modelo en la carpeta `sbml_curado_final` por sitio, en el mismo Drive mencionado antes. Luego recalcula el scope de la semilla de cofactpres con un chequeo de reversibilidad corregido, y elimina en una segunda ronda las reacciones "derivadas" restantes, guardando el modelo finalmente curado en la carpeta `sbml_curado_final_v2`. El resultado son los 8 modelos sin fuga de metabolitos no-cofactor bajo la semilla de solo cofactores, verificado en la celda final.
- `test_genes.ipynb`: sirve para revisar que todos los modelos tengan el mismo número de genes, pues la curación no interviene en las reacciones del modelo original, solo las duplicadas con el tag de cofactores.

## Cómo se usa

1. Se parte de los SBML crudos generados en `generacion_modelos_sbml/`.
2. Se corre `cofactores_oficial.ipynb`, que aplica `cofactores_metagenomas.py` con `cofactors.tsv` sobre los 8 modelos.
3. Se valida la curación con `test_cofactores_v2_i.ipynb` y `test_cofactores_v2_ii.ipynb`: la semilla de solo cofactores `seed_cofactors.sbml` debe dar un scope bajo, compuesto únicamente por metabolitos con tag `_cof_`. Si aparecen fugas, estos cuadernillos las diagnostican y las corrigen en rondas de eliminación de reacciones.
