#!/bin/sh
# Verifica se o computador está pronto para os exemplos da aula de E/S.
# Uso: sh 00_verificar_ambiente.sh
#
# Gestão de Entrada e Saída — Sistemas Operacionais (PUCRS)
# Prof. Filipo Novo Mór - filipomor.com - github.com/ProfessorFilipo
cd "$(dirname "$0")" || exit 1
PROBLEMAS=0
ok()    { printf '  [ OK ]  %s\n' "$1"; }
falta() { printf '  [FALTA] %s\n' "$1"; PROBLEMAS=$((PROBLEMAS + 1)); }

echo "Sistema: $(uname -s) $(uname -r) | arquitetura: $(uname -m)"
case "$(uname -s)" in
    Darwin) DICA_PY="xcode-select --install"; DICA_CC="xcode-select --install" ;;
    Linux)  DICA_PY="sudo apt install python3"; DICA_CC="sudo apt install build-essential" ;;
    *)      echo "Sistema não suportado (use Linux ou macOS)."; exit 1 ;;
esac

if python3 -c 'import sys; sys.exit(sys.version_info < (3, 8))' 2>/dev/null; then
    ok "Python $(python3 -c 'import platform; print(platform.python_version())')"
else
    falta "Python 3.8 ou mais recente -> $DICA_PY"
fi

TMPBIN="${TMPDIR:-/tmp}/verifica_cc_$$"
if cc -O0 privilegiada.c -o "$TMPBIN" 2>/dev/null; then
    ok "compilador C (cc)"
    rm -f "$TMPBIN"
else
    falta "compilador C -> $DICA_CC"
fi

for cmd in dd ps df; do
    if command -v "$cmd" >/dev/null 2>&1; then ok "comando $cmd"; else falta "comando $cmd"; fi
done

if [ -t 0 ] && [ -t 1 ]; then ok "rodando num terminal"; else falta "rode este script direto num terminal"; fi

echo
if [ "$PROBLEMAS" -eq 0 ]; then
    echo "Tudo pronto para a aula!"
else
    echo "Corrija os $PROBLEMAS item(ns) marcados com [FALTA] e rode novamente."
fi
