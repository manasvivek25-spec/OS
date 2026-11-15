SUMMARY = "SmolLM2-360M-Instruct-Q4_K_M GGUF Model Weights for Lazy OS"
HOMEPAGE = "https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct-GGUF"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/Apache-2.0;md5=89aea4e17d99a7cacdbeed46a0096b10"

SRC_URI = "https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct-GGUF/resolve/main/smollm2-360m-instruct-q4_k_m.gguf;downloadfilename=smollm2-360m-instruct-q4_k_m.gguf"

S = "${WORKDIR}"

do_install() {
    install -d ${D}/var/lib/lazy/models
    install -m 0644 ${WORKDIR}/smollm2-360m-instruct-q4_k_m.gguf ${D}/var/lib/lazy/models/default.gguf
}

FILES:${PN} += "/var/lib/lazy/models/default.gguf"
