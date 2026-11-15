SUMMARY = "Lazy OS First-Boot and Filesystem Overlay Setup"
DESCRIPTION = "Initializes Btrfs subvolumes on data partition and mounts OverlayFS for /etc and /var over SquashFS read-only root."
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = " \
    file://lazy-first-boot.sh \
    file://lazy-first-boot.service \
"

inherit systemd

SYSTEMD_SERVICE:${PN} = "lazy-first-boot.service"
SYSTEMD_AUTO_ENABLE = "enable"

RDEPENDS:${PN} += "btrfs-progs util-linux"

do_install() {
    install -d ${D}${sbindir}
    install -m 0755 ${WORKDIR}/lazy-first-boot.sh ${D}${sbindir}/lazy-first-boot

    install -d ${D}${systemd_unitdir}/system
    install -m 0644 ${WORKDIR}/lazy-first-boot.service ${D}${systemd_unitdir}/system/lazy-first-boot.service
}

FILES:${PN} += "${sbindir}/lazy-first-boot ${systemd_unitdir}/system/lazy-first-boot.service"
