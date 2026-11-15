SUMMARY = "Vosk Small English Speech Recognition Acoustic Model"
HOMEPAGE = "https://alphacephei.com/vosk/models"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/Apache-2.0;md5=89aea4e17d99a7cacdbeed46a0096b10"

SRC_URI = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"

S = "${WORKDIR}"

do_install() {
    install -d ${D}/var/lib/lazy/models/vosk
    cp -r ${WORKDIR}/vosk-model-small-en-us-0.15/* ${D}/var/lib/lazy/models/vosk/
}

FILES:${PN} += "/var/lib/lazy/models/vosk"
