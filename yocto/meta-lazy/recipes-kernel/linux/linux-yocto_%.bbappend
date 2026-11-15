# BitBake append recipe integrating Lazy OS custom kernel fragments into linux-yocto

FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI:append = " \
    file://base-minimal.cfg \
    file://memory.cfg \
    file://fs.cfg \
    file://security.cfg \
    file://laptop.cfg \
"
