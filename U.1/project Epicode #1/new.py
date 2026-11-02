#!/bin/bash
#
# ctf_image_scan.sh
# Automatizza i controlli forensi/steganografici di base su tutte le immagini
# di una cartella, per sfide CTF.
#
# Uso:
#   ./ctf_image_scan.sh <cartella_con_le_immagini>
#
# Richiede (installabili su Kali con: sudo apt install exiftool binwalk steghide zsteg):
#   file, exiftool, binwalk, strings (binutils), steghide, zsteg (ruby gem)

set -uo pipefail

TARGET_DIR="${1:-.}"
OUT_DIR="ctf_scan_results_$(date +%Y%m%d_%H%M%S)"

if [ ! -d "$TARGET_DIR" ]; then
    echo "Errore: la cartella '$TARGET_DIR' non esiste."
    exit 1
fi

mkdir -p "$OUT_DIR"
REPORT="$OUT_DIR/report.txt"
echo "=== CTF Image Scan — $(date) ===" > "$REPORT"
echo "Cartella analizzata: $TARGET_DIR" >> "$REPORT"
echo "" >> "$REPORT"

check_cmd() {
    command -v "$1" >/dev/null 2>&1
}

echo "Avvio scansione su: $TARGET_DIR"
echo "I risultati verranno salvati in: $OUT_DIR"
echo ""

find "$TARGET_DIR" -type f | while read -r f; do
    base=$(basename "$f")
    safe_name=$(echo "$base" | tr -c '[:alnum:].-' '')
    file_out_dir="$OUT_DIR/$safe_name"
    mkdir -p "$file_out_dir"

    echo "----------------------------------------" | tee -a "$REPORT"
    echo "FILE: $f" | tee -a "$REPORT"
    echo "----------------------------------------" >> "$REPORT"

    # 1. Tipo file reale
    echo "" >> "$REPORT"
    echo "[1] file (tipo reale):" >> "$REPORT"
    file "$f" >> "$REPORT" 2>&1

    # 2. exiftool - metadati
    echo "" >> "$REPORT"
    echo "[2] exiftool (metadati):" >> "$REPORT"
    if check_cmd exiftool; then
        exiftool -a -u -g1 "$f" >> "$REPORT" 2>&1
    else
        echo "exiftool non installato (sudo apt install libimage-exiftool-perl)" >> "$REPORT"
    fi

    # 3. binwalk - file nascosti embedded
    echo "" >> "$REPORT"
    echo "[3] binwalk (file nascosti):" >> "$REPORT"
    if check_cmd binwalk; then
        binwalk "$f" >> "$REPORT" 2>&1
        # estrazione automatica in una sottocartella dedicata
        (cd "$file_out_dir" && binwalk -e "$(realpath "$f")" >/dev/null 2>&1)
    else
        echo "binwalk non installato (sudo apt install binwalk)" >> "$REPORT"
    fi

    # 4. strings - cerca pattern tipo flag{...}, CTF{...}
    echo "" >> "$REPORT"
    echo "[4] strings (ricerca pattern flag/CTF):" >> "$REPORT"
    strings -n 6 "$f" | grep -iE "flag\{|ctf\{|flag:|password|pwd|key" >> "$REPORT" 2>&1
    strings -n 6 "$f" > "$file_out_dir/strings_full.txt"
    echo "(output completo di strings salvato in $file_out_dir/strings_full.txt)" >> "$REPORT"

    # 5. steghide - solo se è jpg/jpeg/bmp (gli unici formati supportati)
    ext="${base##*.}"
    ext_lower=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
    if [[ "$ext_lower" =~ ^(jpg|jpeg|bmp)$ ]]; then
        echo "" >> "$REPORT"
        echo "[5] steghide info (controllo dati nascosti):" >> "$REPORT"
        if check_cmd steghide; then
            steghide info "$f" >> "$REPORT" 2>&1 </dev/null
            echo "Nota: se richiede password, provare: steghide extract -sf \"$f\"" >> "$REPORT"
        else
            echo "steghide non installato (sudo apt install steghide)" >> "$REPORT"
        fi
    fi

    # 6. zsteg - solo per png/bmp
    if [[ "$ext_lower" =~ ^(png|bmp)$ ]]; then
        echo "" >> "$REPORT"
        echo "[6] zsteg -a (LSB steganography):" >> "$REPORT"
        if check_cmd zsteg; then
            zsteg -a "$f" >> "$REPORT" 2>&1
        else
            echo "zsteg non installato (sudo gem install zsteg)" >> "$REPORT"
        fi
    fi

    echo "" >> "$REPORT"
done

echo ""
echo "=== Scansione completata ==="
echo "Report completo: $REPORT"
echo "File estratti e strings completi: $OUT_DIR/<nome_file>/"
echo ""
echo "Consiglio: apri il report e cerca manualmente 'flag' o 'CTF' con:"
echo "  grep -i flag $REPORT"