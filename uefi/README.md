# R5Q UEFI bring-up

The phone's XBL extraction is staged locally in `files/Binaries/r5q/` (ignored by Git); the live phone DTB is tracked at
`files/Resources/DTBs/r5q.dtb`.

## Current platform data

- XBL build: `BOOT.XF.3.0-00498-SM8150LZB-2`.
- Boot image: header version 1, gzip kernel, DTB appended, according to this XBL's `RawFiles/uefiplat.cfg`.
- UEFI firmware region: `0x9FC00000` for `0x00300000` bytes, from the XBL memory map. These values are used by `r5q.toml` and still need verification with the built Mu-Silicium image.
- Display reservation: `0x9C400000` for `0x02000000` bytes. This is not yet proven to be the GOP framebuffer base.
- Panel: `S6E3FA9_AMB667UM01`, 1080 x 2400, 60 Hz DSI command mode. The extracted RawFiles XML set has no matching panel description.

## Not built yet

The pinned Mu-Silicium tree has no Samsung `r5qPkg` and no Qualcomm `MsmnilePkg` for SM8150. `r5q.toml` only records boot-image packaging values; it does not supply an EDK2 platform. Do not use `redwoodPkg`, `KonaPkg`, `LahainaPkg`, or `NapaliPkg` as a drop-in substitute. This blocks the Mu-Silicium route. The separate open U-Boot route is under development; its fastboot image candidate must still pass on-device validation before it can be called bootable.

Vendor drivers under `files/Binaries/r5q/` are local-only and must never be committed.
