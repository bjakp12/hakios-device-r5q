#!/bin/sh
# Build the open Qualcomm U-Boot path for r5q. On fastboot boot, ABL passes
# the phone's live DTB and the HKUB ramdisk to U-Boot.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
UB=${U_BOOT:-$ROOT/u-boot}
OUT=${O:-$UB/build-r5q}
CROSS_COMPILE=${CROSS_COMPILE:-aarch64-linux-gnu-}
MAKE=${MAKE:-make}

[ -f "$UB/Makefile" ] || { echo "build-r5q-uboot: missing $UB; run uefi/u-boot/apply.sh r5q first" >&2; exit 1; }
[ -f "$UB/cmd/hakios.c" ] || { echo "build-r5q-uboot: HakiOS command patch is missing" >&2; exit 1; }
[ -f "$UB/board/qualcomm/qcom-phone.config" ] || { echo "build-r5q-uboot: upstream qcom-phone fragment missing" >&2; exit 1; }

"$MAKE" -C "$UB" O="$OUT" CROSS_COMPILE="$CROSS_COMPILE" qcom_defconfig
"$UB/scripts/kconfig/merge_config.sh" -m -O "$OUT" "$OUT/.config" \
	"$UB/board/qualcomm/qcom-phone.config" \
	"$ROOT/devices/r5q/u-boot/files/configs/hakios_r5q.fragment"
"$MAKE" -C "$UB" O="$OUT" CROSS_COMPILE="$CROSS_COMPILE" olddefconfig

grep -qx 'CONFIG_ARCH_SNAPDRAGON=y' "$OUT/.config"
grep -qx 'CONFIG_CLK_QCOM_SM8150=y' "$OUT/.config"
grep -qx 'CONFIG_CMD_HAKIOS=y' "$OUT/.config"
grep -qx 'CONFIG_EFI_LOADER=y' "$OUT/.config"

"$MAKE" -C "$UB" O="$OUT" CROSS_COMPILE="$CROSS_COMPILE" -j"${JOBS:-2}"
[ -s "$OUT/u-boot.bin" ] || { echo "build-r5q-uboot: build did not produce u-boot.bin" >&2; exit 1; }
echo "build-r5q-uboot: $OUT/u-boot.bin"
