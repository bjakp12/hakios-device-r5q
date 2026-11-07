# Device: Samsung R5Q PROJECT Rev09 (r5q)

Made by `tools/new-device.py` on 2026-11-07, from the file r5q.dtb. Edit it as the port goes.

This repository is an experimental port scaffold. Its GitHub Actions workflow checks the HakiOS device/configuration and builds
the configured XNU kernel, an open loader with the provisional R5Q platform profile, an Apple-free first-boot test payload
(`r5q-open-test.xnup`), and a U-Boot `fastboot boot` image candidate. The U-Boot image uses the R5Q DTB passed by ABL and keeps
the phone's partitions untouched. A successful build does not certify that U-Boot or XNU boots on the handset; display/GOP,
reserved-memory and early-driver behavior still require a controlled device test.

| What | Value |
|---|---|
| Board (the tree's `model`) | Samsung R5Q PROJECT Rev09 |
| Compatible | `qcom,sm8150-mtp qcom,sm8150 qcom,mtp` |

## The SoC addresses

No reference tree to compare with (devices/redwood/prebuilt/device-tree.dtb is missing).

| Argument | Value | Against the reference |
|---|---|---|
| `soc_ipa_base` | `0x1e40000` |  |
| `soc_gsi_base` | `0x1e04000` |  |
| `soc_ipcc` | `(not found)` | **missing**: the tree has no node this was read from; see the table in devices/redwood/README.md |
| `soc_aoss` | `0xc300000` |  |
| `soc_rsc` | `(not found)` | **missing**: the tree has no node this was read from; see the table in devices/redwood/README.md |
| `soc_apps_smmu` | `0x15000000` |  |
| `soc_cmd_db` | `(not found)` | **missing**: the tree has no node this was read from; see the table in devices/redwood/README.md |
| `soc_mpss_mem` | `(not found)` | **missing**: the tree has no node this was read from; see the table in devices/redwood/README.md |
| `modem_ipa_fw_at` | `(not found)` | **missing**: the tree has no node this was read from; see the table in devices/redwood/README.md |
| `soc_smem` | `0x86000000` |  |
| `soc_imem` | `0x14600000` |  |
| `soc_ipa_stream` | `0x520` |  |
| `soc_ipa_stream_uc` | `0x522` |  |
| `soc_pas_mpss` | `0x4` |  |
| `soc_pas_ipa` | `0xf` |  |
| `soc_ipa_fw` | `ipa_fws` |  |

`soc.args` is what `tools/soc-args.py` read out of the tree; `pull-soc.sh` makes it again from the phone on
adb. The run scripts add it to the kernel command line. Where each argument comes from in the tree:
`devices/redwood/README.md`.

## Bring-up findings (not a working port)

- The live DTB identifies `Samsung R5Q PROJECT Rev09`, compatible with `qcom,sm8150-mtp` / `qcom,sm8150`.
- SM8150 is Qualcomm's **msmnile** platform. Mu-Silicium's `LahainaPkg` is for SM8350/Snapdragon 888, not this phone; the pinned tree has no SM8150 `MsmnilePkg` or Samsung `r5qPkg`. This blocks the Mu-Silicium route. The experimental alternative is open Qualcomm U-Boot (`u-boot/files/`), which receives the live R5Q DTB from ABL; it has not been tested on the handset. HakiOS redwood's `KodiakPkg` is for SM7325 and is not a compatible base.
- The Samsung kernel source's R5Q Rev09 overlay selects `S6E3FA9_AMB667UM01`, **1080 x 2400**, 60 Hz, DSI command mode. It uses Samsung `sec_ts` touch at I2C address `0x48`, interrupt GPIO 87, with 1.8 V / 3.3 V rails.
- UEFIReader extracted build `BOOT.XF.3.0-00498-SM8150LZB-2` from the phone's XBL. Its `RawFiles/uefiplat.cfg` reports SMEM at `0x86000000`, GIC distributor/redistributor at `0x17A00000` / `0x17A60000`, and a 32 MiB display reservation at `0x9C400000`. The display reservation is **not yet verified as the GOP framebuffer address**.
- No `2400`, `AMB667`, or `S6E3FA9` panel entry was found in the extracted UEFI XML/CFG files. Do not select one of the unrelated 1080 x 1920 XML panels as a substitute.
- The common HakiOS loader currently detects redwood from framebuffer address `0xE1000000`; otherwise it selects QEMU. It has no R5Q platform descriptor, and no R5Q boot has been tested.

The XBL/UEFI extraction is vendor firmware: keep it in the local ignored `uefi/files/Binaries/r5q/` directory only. Never commit it. The experimental U-Boot route only consumes the public/live DTB and open U-Boot code; the XBL extraction is reserved for a later Mu-Silicium implementation.

## What is this phone's own

The kernel, loader and user space know nothing about a phone: addresses, interrupts, rails and firmware
come from its tree and its Android. What is written for one phone is the list below. The head of each file
says where its numbers came from; that is the map of what to rewrite.

- [ ] **UEFI and loader**: no R5Q package exists in Mu-Silicium yet. The loader needs an R5Q platform profile; its framebuffer address is not confirmed.
- [ ] **Display**: Samsung S6E3FA9 / AMB667UM01, 1080 x 2400, 60 Hz, DSI command mode. The extracted XBL XML files have no matching panel entry.
- [ ] **Touch**: Samsung `sec_ts` at I2C `0x48`, IRQ GPIO 87, 1.8 V / 3.3 V rails; HakiOS has no `sec_ts` driver.
- [ ] **Buttons**: Samsung/PMIC controls not mapped to a HakiOS driver.
- [ ] **Storage**: the phone uses UFS; HakiOS UFS support has not been validated against R5Q's SM8150 controller/firmware.
- [ ] **CPU and thermal**: eight SM8150 cores identified in the device tree; HakiOS clock and thermal drivers are not ported to msmnile.
- [ ] **GPU**: Adreno 640; HakiOS's current GPU driver targets the Adreno 642L, so it is not enabled for R5Q.
- [ ] **Wi-Fi, audio, battery, cellular, cameras and haptics**: hardware and firmware mapping and HakiOS driver bring-up remain outstanding.

## Configuration

The kernel's settings are layered the way an Android kernel's are: the common kernel, the SoC's, this phone's
(`docs/configs.md`). Two short files make this phone a configuration:

    configs/r5q.config          CONFIG_DEVICE="r5q"   and whatever is true of this phone only
    configs/r5q_defconfig       #include common_defconfig
                                   #include <the SoC's fragment: sc7280.config for the SC7280 family>
                                   #include r5q.config

Then `make r5q_defconfig`. Turn on only what this phone has been shown to do; `tools/hakios-config.py check` says what the
choice needs.

The drivers are part of the configuration too (`docs/drivers-config.md`): every one is built unless a configuration leaves it out,
and the addresses, pins and rails in each are the reference phone's. Leave out in `configs/r5q.config` what has not been
ported to this phone yet (`# CONFIG_HAKIOS_GOODIX is not set`, ...; `configs/qemu_defconfig` leaves out all of them), and put
each one back when it has been made to work here. `tools/hakios-config.py show` lists what is built in.

## Firmware

The XBL extraction used for UEFI development is vendor firmware. Keep it under the local ignored path
`uefi/files/Binaries/r5q/`; do not commit or publish it. A device-specific XNU firmware-pull script has not been written yet.

## Before you open a pull request

`tools/provenance-check.py` must pass: no vendor firmware, no UEFI drivers, no Apple files in the tree. The CI job builds a
candidate kernel and placeholder-identity loader only; neither is verified to boot R5Q.

## The repository

A HakiOS device repository: what is true of this device and of no other. The kernel, the loader, the drivers and the tools are
the common repository's; the sm8150 family's facts are in `soc/`, carried with the device. How the three are put together:
[docs/porting/repositories.md](https://github.com/oosexgang/hakios-xnu-kernel/blob/main/docs/porting/repositories.md).

| File | What |
|---|---|
| `metal.args` | what `tools/metal-run.sh` gives this phone: its cores, its panel's rate, the threads that copy frames, the touch poll |
| `device.conf` | what the device is, and how far each part of it works: its page in the documentation is made from it |
| `configs/r5q_defconfig` | the common kernel, the SoC's fragment, this device's: `make r5q_defconfig` |
| `configs/r5q.config` | what is this device's own: the drivers built in, the arguments it needs |
| `soc/` | its SoC family's layer (sm8150): `soc.conf`, `configs/sm8150.config`, the SoC's drivers; carried here so that this one repository is all the device needs |
| `drivers/` | drivers of its own, if it needs any (`drivers/<subsystem>/conf`, as in the common repository) |

Every phone driver of the common repository is left out to begin with: their addresses and pins are the phone they were written
for. Put one back in `configs/r5q.config` when it has been made to work here, and say so in `device.conf`.

Check with `tools/hakios-device.py check r5q`.
