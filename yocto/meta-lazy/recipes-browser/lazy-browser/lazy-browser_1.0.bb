SUMMARY = "Lazy OS Isolated Headless Web Browser and WebDriver Integration"
DESCRIPTION = "Provides isolated headless web browsing with WebDriver integration and pure-Python sandbox fallback for Lazy OS WebBroker (Rule F9)."
HOMEPAGE = "https://github.com/lazy-os/lazy-os"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

RDEPENDS:${PN} += " \
    python3-core \
    python3-json \
    python3-urllib \
    python3-modules \
    python3-pyyaml \
"

do_install() {
    install -d ${D}${sysconfdir}/lazy/browser
    install -d ${D}/var/quarantine
}

FILES:${PN} += " \
    ${sysconfdir}/lazy/browser \
    /var/quarantine \
"
