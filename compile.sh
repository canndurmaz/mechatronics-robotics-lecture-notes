#!/usr/bin/env bash
# Compile the training decks.
#   ./compile.sh          -> all five days (in parallel)
#   ./compile.sh 2 4      -> only day 2 and day 4
#   CLEAN=1 ./compile.sh  -> also remove aux/log files afterwards
set -u
ROOT="$(cd "$(dirname "$0")" && pwd)"
export TEXINPUTS="$ROOT/common//:"
DAYS=("$@"); [ ${#DAYS[@]} -eq 0 ] && DAYS=(1 2 3 4 5)

build() {
  local d=$1 dir="$ROOT/day$1"
  cd "$dir" || { echo "day$d: missing folder"; return 1; }
  for _ in 1 2; do pdflatex -interaction=nonstopmode -halt-on-error "day$d.tex" >/dev/null 2>&1; done
  if grep -q '^!' "day$d.log"; then
    echo "day$d: FAILED — see day$d/day$d.log"; grep -m3 -A2 '^!' "day$d.log"; return 1
  fi
  echo "day$d: OK ($(pdfinfo "day$d.pdf" 2>/dev/null | awk '/Pages/{print $2}') pages)"
  [ "${CLEAN:-0}" = 1 ] && rm -f day$d.{aux,log,nav,out,snm,toc,vrb}
  return 0
}

fail=0
for d in "${DAYS[@]}"; do build "$d" & done
for job in $(jobs -p); do wait "$job" || fail=1; done
exit $fail
