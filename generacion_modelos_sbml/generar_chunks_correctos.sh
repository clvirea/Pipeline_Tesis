#!/bin/bash
# =============================================================================
# generar_chunks_correctos.sh
# Genera chunks REALES dividiendo FNA + FAA + annotations por subconjunto de genes
# Cada chunk tendrá ~41K genes con sus propias secuencias FNA y FAA
# =============================================================================

FNA="/home/claire/emapper2gbk/TESIS/fna/ilq_contigs.fasta.db.fna"
FAA="/home/claire/emapper2gbk/TESIS/faa/ilq_contigs.fasta.db.faa"
ANNOT="/home/claire/emapper2gbk/TESIS/annotations/ilq_contigs.fasta.db.faa.emapper6.emapper.annotations"
GO_OBO="/home/claire/emapper2gbk/go-basic.obo"

CHUNKS_DIR="/home/claire/emapper2gbk/TESIS/chunks_reales"
GBK_DIR="/home/claire/emapper2gbk/TESIS/gbk_reales"

N_CHUNKS=5

mkdir -p "$CHUNKS_DIR" "$GBK_DIR"

echo "============================================"
echo "PASO 1: Dividir anotaciones en $N_CHUNKS chunks"
echo "============================================"

# Extraer header y datos limpios
HEADER=$(grep "^#query" "$ANNOT" | head -1)
grep -v "^#" "$ANNOT" > /tmp/annot_clean.tsv
TOTAL=$(wc -l < /tmp/annot_clean.tsv)
CHUNK_SIZE=$(( (TOTAL + N_CHUNKS - 1) / N_CHUNKS ))
echo "Total genes anotados: $TOTAL | Chunk size: $CHUNK_SIZE"

# Dividir anotaciones
split -l "$CHUNK_SIZE" -d --suffix-length=3 /tmp/annot_clean.tsv "$CHUNKS_DIR/annot_chunk_"
rm /tmp/annot_clean.tsv

# Añadir header a cada chunk de anotaciones
for f in "$CHUNKS_DIR"/annot_chunk_*; do
    tmp=$(mktemp)
    echo "$HEADER" > "$tmp"
    cat "$f" >> "$tmp"
    mv "$tmp" "$f"
done

echo "Chunks de anotaciones generados: $(ls $CHUNKS_DIR/annot_chunk_* | wc -l)"

echo ""
echo "============================================"
echo "PASO 2: Por cada chunk, extraer FNA y FAA correspondientes"
echo "============================================"

for annot_chunk in $(ls "$CHUNKS_DIR"/annot_chunk_* | sort); do
    chunk_name=$(basename "$annot_chunk")
    chunk_id=${chunk_name#annot_chunk_}

    echo ""
    echo "--- Procesando chunk_$chunk_id ---"

    # Extraer IDs de genes de este chunk (columna 1, sin header)
    grep -v "^#" "$annot_chunk" | cut -f1 > /tmp/ids_chunk.txt
    N_GENES=$(wc -l < /tmp/ids_chunk.txt)
    echo "  Genes en este chunk: $N_GENES"

    # Extraer secuencias FNA para estos IDs usando python (más robusto que grep)
    python3 - <<PYEOF
import sys
ids_file = "/tmp/ids_chunk.txt"
fna_in = "$FNA"
fna_out = "$CHUNKS_DIR/fna_chunk_$chunk_id.fna"
faa_in = "$FAA"
faa_out = "$CHUNKS_DIR/faa_chunk_$chunk_id.faa"

# Cargar IDs del chunk
with open(ids_file) as f:
    ids = set(line.strip() for line in f if line.strip())

print(f"  IDs a buscar: {len(ids)}")

# Extraer FNA
found_fna = 0
with open(fna_in) as fin, open(fna_out, 'w') as fout:
    write = False
    for line in fin:
        if line.startswith('>'):
            seq_id = line[1:].strip().split()[0]
            write = seq_id in ids
            if write:
                found_fna += 1
        if write:
            fout.write(line)
print(f"  FNA extraídas: {found_fna}")

# Extraer FAA
found_faa = 0
with open(faa_in) as fin, open(faa_out, 'w') as fout:
    write = False
    for line in fin:
        if line.startswith('>'):
            seq_id = line[1:].strip().split()[0]
            write = seq_id in ids
            if write:
                found_faa += 1
        if write:
            fout.write(line)
print(f"  FAA extraídas: {found_faa}")
PYEOF

    rm /tmp/ids_chunk.txt

    # Verificar que los tres archivos tienen contenido
    N_FNA=$(grep -c "^>" "$CHUNKS_DIR/fna_chunk_$chunk_id.fna" 2>/dev/null || echo 0)
    N_FAA=$(grep -c "^>" "$CHUNKS_DIR/faa_chunk_$chunk_id.faa" 2>/dev/null || echo 0)
    N_ANNOT=$(grep -v "^#" "$annot_chunk" | wc -l)
    echo "  Verificación: FNA=$N_FNA | FAA=$N_FAA | Annot=$N_ANNOT"

    if [ "$N_FNA" -eq 0 ] || [ "$N_FAA" -eq 0 ]; then
        echo "  ERROR: FNA o FAA vacíos, saltando chunk"
        continue
    fi

    echo ""
    echo "PASO 3: Generar GBK para chunk_$chunk_id"
    GBK_OUT="$GBK_DIR/chunk_${chunk_id}.gbk"

    emapper2gbk genes \
        -fn "$CHUNKS_DIR/fna_chunk_$chunk_id.fna" \
        -fp "$CHUNKS_DIR/faa_chunk_$chunk_id.faa" \
        -a  "$annot_chunk" \
        -n  "metagenome" \
        -o  "$GBK_OUT" \
        -go "$GO_OBO" \
        --ete

    if [ $? -eq 0 ]; then
        N_LOCUS=$(grep -c "^LOCUS" "$GBK_OUT" 2>/dev/null || echo 0)
        SIZE=$(du -sh "$GBK_OUT" | cut -f1)
        echo "  OK → $GBK_OUT | LOCUSes: $N_LOCUS | Tamaño: $SIZE"
    else
        echo "  ERROR generando GBK para chunk_$chunk_id"
    fi
done

echo ""
echo "============================================"
echo "RESUMEN FINAL"
echo "============================================"
for gbk in "$GBK_DIR"/*.gbk; do
    N=$(grep -c "^LOCUS" "$gbk" 2>/dev/null || echo "?")
    S=$(du -sh "$gbk" | cut -f1)
    echo "  $(basename $gbk): $N LOCUSes, $S"
done
echo "Espacio total: $(du -sh $GBK_DIR)"