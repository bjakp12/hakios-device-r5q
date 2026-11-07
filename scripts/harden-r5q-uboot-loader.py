#!/usr/bin/env python3
"""Refuse the HakiOS fixed payload copy if U-Boot cannot reserve its RAM range."""

from pathlib import Path
import sys


OLD = "\tlmb_alloc_mem(LMB_MEM_ALLOC_ADDR, 0, &addr, SZ_64M, LMB_NONE);\n"
NEW = (
    "\tif (lmb_alloc_mem(LMB_MEM_ALLOC_ADDR, 0, &addr, SZ_64M, LMB_NONE)) {\n"
    "\t\tprintf(\"[oosexgang] hakios: payload RAM at %#lx is not free\\n\", PAYLOAD_BASE);\n"
    "\t\treturn -ENOMEM;\n"
    "\t}\n"
)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} PATH/TO/u-boot/cmd/hakios.c", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    source = path.read_text(encoding="utf-8")
    if NEW in source:
        print("HakiOS U-Boot payload reservation is already checked")
        return 0
    if source.count(OLD) != 1:
        print("expected one fixed payload reservation in cmd/hakios.c; upstream source changed", file=sys.stderr)
        return 1
    path.write_text(source.replace(OLD, NEW, 1), encoding="utf-8", newline="\n")
    print(f"added fixed-payload reservation failure check to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
