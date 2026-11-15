SUMMARY = "Port of Facebook's LLaMA model in C/C++"
HOMEPAGE = "https://github.com/ggerganov/llama.cpp"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "git://github.com/ggerganov/llama.cpp.git;protocol=https;branch=master;tag=b3800"
SRCREV = "392daefb1c0ea4457e935409d799988ff4579c29"

S = "${WORKDIR}/git"

inherit cmake

EXTRA_OECMAKE += " \
    -DLLAMA_BUILD_TESTS=OFF \
    -DLLAMA_BUILD_EXAMPLES=ON \
    -DLLAMA_BUILD_SERVER=ON \
    -DLLAMA_NATIVE=OFF \
"

FILES:${PN} += "${bindir}/llama-server ${bindir}/llama-cli"
