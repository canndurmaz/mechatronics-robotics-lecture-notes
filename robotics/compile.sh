#!/usr/bin/env bash
# Compile the two-week robotics decks.
#   ./compile.sh               -> all ten days (in parallel)
#   ./compile.sh w1d3 w2d1     -> selected days
#   CLEAN=1 ./compile.sh       -> also remove aux/log files
set -u
ROOT="$(cd "$(dirname "$0")" && pwd)"
export TEXINPUTS="$ROOT/../common//:"
DAYS=("$@"); [ ${#DAYS[@]} -eq 0 ] && DAYS=(w1d1 w1d2 w1d3 w1d4 w1d5 w2d1 w2d2 w2d3 w2d4 w2d5)

build() {
  local d=$1
  cd "$ROOT/$d" || { echo "$d: missing folder"; return 1; }
  for _ in 1 2; do pdflatex -interaction=nonstopmode -halt-on-error "$d.tex" >/dev/null 2>&1; done
  if grep -q '^!' "$d.log"; then
    echo "$d: FAILED — see $d/$d.log"; grep -m3 -A2 '^!' "$d.log"; return 1
  fi
  echo "$d: OK ($(pdfinfo "$d.pdf" 2>/dev/null | awk '/Pages/{print $2}') pages)"
  [ "${CLEAN:-0}" = 1 ] && rm -f $d.{aux,log,nav,out,snm,toc,vrb}
  return 0
}

fail=0
for d in "${DAYS[@]}"; do build "$d" & done
for job in $(jobs -p); do wait "$job" || fail=1; done
exit $fail
