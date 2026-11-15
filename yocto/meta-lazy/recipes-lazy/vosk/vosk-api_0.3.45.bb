SUMMARY = "Offline open source speech recognition toolkit"
HOMEPAGE = "https://alphacephei.com/vosk/"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/Apache-2.0;md5=89aea4e17d99a7cacdbeed46a0096b10"

SRC_URI = "git://github.com/alphacep/vosk-api.git;protocol=https;branch=master;tag=v0.3.45"
SRCREV = "1b37a5b3f27ee985e98dcad445b27464019be7f1"

S = "${WORKDIR}/git"

inherit setuptools3
