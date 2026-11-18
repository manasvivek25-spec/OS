################################################################################
#
# llama-cpp
#
################################################################################

LLAMA_CPP_VERSION = b2600
LLAMA_CPP_SITE = $(call github,ggerganov,llama.cpp,$(LLAMA_CPP_VERSION))
LLAMA_CPP_LICENSE = MIT
LLAMA_CPP_LICENSE_FILES = LICENSE

$(eval $(cmake-package))
