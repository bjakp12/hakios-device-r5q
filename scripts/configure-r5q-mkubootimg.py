#!/usr/bin/env python3
"""Add page-size and load-address controls to the common Android boot image packer."""

from pathlib import Path
import sys


ARGUMENT = "    ap.add_argument('--pagesize', type=int, choices=(2048, 4096, 8192, 16384), default=2048, help='Android boot-image page size')\n"
ARGUMENT_ANCHOR = "    ap.add_argument('-o', '--output', help='the boot image (default: hakios-u-boot.img)')\n"
PACKER_OLD = "                               '--header_version', '1', '-o', out])\n"
PACKER_NEW = (
    "                               '--header_version', '1', '--pagesize', str(args.pagesize),\n"
    "                               '--base', str(args.base), '--kernel_offset', str(args.kernel_offset),\n"
    "                               '--ramdisk_offset', str(args.ramdisk_offset), '--tags_offset', str(args.tags_offset),\n"
    "                               '-o', out])\n"
)
ADDRESS_ARGS = (
    "    ap.add_argument('--base', type=lambda v: int(v, 0), default=0x10000000)\n"
    "    ap.add_argument('--kernel-offset', type=lambda v: int(v, 0), default=0x00008000)\n"
    "    ap.add_argument('--ramdisk-offset', type=lambda v: int(v, 0), default=0x01000000)\n"
    "    ap.add_argument('--tags-offset', type=lambda v: int(v, 0), default=0x00000100)\n"
)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} PATH/TO/tools/mkubootimg.py", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    source = path.read_text(encoding="utf-8")
    if ARGUMENT in source and ADDRESS_ARGS in source and PACKER_NEW in source:
        print("mkubootimg already supports explicit Android boot header parameters")
        return 0
    if (source.count(ARGUMENT_ANCHOR) != 1 or source.count(PACKER_OLD) != 1 or
            source.count(ARGUMENT) != 0 or source.count(ADDRESS_ARGS) != 0):
        print("mkubootimg source differs from the expected HakiOS version", file=sys.stderr)
        return 1
    source = source.replace(ARGUMENT_ANCHOR, ARGUMENT_ANCHOR + ARGUMENT, 1)
    source = source.replace(ARGUMENT, ARGUMENT + ADDRESS_ARGS, 1)
    source = source.replace(PACKER_OLD, PACKER_NEW, 1)
    path.write_text(source, encoding="utf-8", newline="\n")
    print(f"added --pagesize support to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
