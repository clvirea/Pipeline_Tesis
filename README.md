# Pipeline_Tesis

Evaluación del potencial metabólico emergente del holobionte de Macrocystis pyrifera a lo largo de la costa chilena mediante reconstrucciones a escala metagenómica (MetaG-GEMs)

## Estructura del pipeline

1. `generacion_modelos_sbml/`: generación de los modelos metabólicos (SBML) crudos
   a partir de metagenomas anotados, por sitio. Ver README de la carpeta.
2. `cofactores/`: curación de los modelos generados para eliminar fugas de metabolitos
   no-cofactor bajo la semilla de cofactores (y otros tests que se hacen para asegurar que la curación de cofactores funcione bien). Ver README de la carpeta.
3. `scope_pcoa/`: análisis de scope metabólico y PCoA entre sitios. Ver README.

