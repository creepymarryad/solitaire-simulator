#!/usr/bin/env sh
# Linux / macOS counterpart of run.bat
cd "$(dirname "$0")" || exit 1
PY="${PYTHON:-python3}"

echo "========================================"
echo "          SYMULATOR PASJANSA"
echo "========================================"

"$PY" main.py --batch || { echo "[BLAD KRYTYCZNY] Program Python zakonczyl sie bledem"; exit 1; }

echo
echo "[SUKCES] Obliczenia zakonczone. Raport: out/raport.html"
if command -v xdg-open >/dev/null 2>&1; then xdg-open out/raport.html >/dev/null 2>&1 &
elif command -v open >/dev/null 2>&1; then open out/raport.html; fi

if [ -f out/replay.pkl ]; then
    printf "Uruchomic wizualizacje? (t/n): "
    read -r ans
    case "$ans" in [tT]*) "$PY" main.py --replay ;; esac
else
    echo "Brak wygranych partii - wizualizacja niedostepna"
fi
