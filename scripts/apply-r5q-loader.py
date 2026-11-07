#!/usr/bin/env python3
"""Apply the experimental R5Q platform profile to a HakiOS checkout."""

from pathlib import Path
import sys


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} PATH/TO/xnuloader/loader.c", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    source = path.read_text(encoding="utf-8")

    platform_anchor = "\t.small_cores = 0x0f,\n};\n"
    platform = (
        "\n"
        "/*\n"
        " * Samsung Galaxy S10 Lite (r5q), Snapdragon 855 / SM8150 (Lahaina).\n"
        " * The register window and GIC bases are from the SM8150 device tree and\n"
        " * UEFI's uefiplat.cfg. CPU MPIDRs are 0x0..0x700: four silver CPUs (0..3),\n"
        " * three gold CPUs (4..6), and the gold-prime CPU (7).\n"
        " *\n"
        " * 0x9c400000 is the 32 MiB display-reserved region in both the live DT and\n"
        " * the extracted XBL platform config. Treating it as GOP's framebuffer base\n"
        " * is still provisional: confirm it from a loader log before relying on this\n"
        " * platform on hardware.\n"
        " */\n"
        "static const struct platform platform_r5q = {\n"
        "\t.name = \"r5q\", .io_base = 0x00400000, .io_size = 0x3FC00000,\n"
        "\t.gic_dist = 0x17A00000, .gic_redist = 0x17A60000, .uart = 0,\n"
        "\t.cores = 8, .core_shift = 8, .small_cores = 0x0f,\n"
        "};\n"
    )
    if source.count(platform_anchor) != 1:
        print("expected one redwood platform anchor; HakiOS loader source changed", file=sys.stderr)
        return 1
    source = source.replace(platform_anchor, platform_anchor + platform, 1)

    display_anchor = (
        "\t\tif (SCREEN.base == 0xE1000000ULL) {\n"
        "\t\t\tPLAT = &platform_redwood;\n"
        "\t\t} else {\n"
    )
    display_profile = (
        "\t\tif (SCREEN.base == 0xE1000000ULL) {\n"
        "\t\t\tPLAT = &platform_redwood;\n"
        "\t\t} else if (SCREEN.base == 0x9C400000ULL) {\n"
        "\t\t\tPLAT = &platform_r5q;\n"
        "\t\t} else {\n"
    )
    if source.count(display_anchor) != 1:
        print("expected one platform selection anchor; HakiOS loader source changed", file=sys.stderr)
        return 1

    path.write_text(source.replace(display_anchor, display_profile, 1), encoding="utf-8", newline="\n")
    print(f"applied provisional R5Q loader profile to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
