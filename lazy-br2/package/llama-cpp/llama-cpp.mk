################################################################################
#
# llama-cpp
#
################################################################################

LLAMA_CPP_VERSION = b2608
LLAMA_CPP_SITE = $(call github,ggml-org,llama.cpp,$(LLAMA_CPP_VERSION))
LLAMA_CPP_LICENSE = MIT
LLAMA_CPP_LICENSE_FILES = LICENSE
LLAMA_CPP_CONF_OPTS = -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=ON

define LLAMA_CPP_INSTALL_BINARIES
	if [ -f "$(@D)/bin/main" ]; then \
		install -D -m 0755 "$(@D)/bin/main" "$(TARGET_DIR)/usr/bin/llama-cli"; \
		ln -sf llama-cli "$(TARGET_DIR)/usr/bin/main"; \
	fi
	if [ -f "$(@D)/bin/llama-cli" ]; then \
		install -D -m 0755 "$(@D)/bin/llama-cli" "$(TARGET_DIR)/usr/bin/llama-cli"; \
	fi
	if [ -f "$(@D)/bin/llama-bench" ]; then \
		install -D -m 0755 "$(@D)/bin/llama-bench" "$(TARGET_DIR)/usr/bin/llama-bench"; \
	fi
	if [ -f "$(@D)/bin/server" ]; then \
		install -D -m 0755 "$(@D)/bin/server" "$(TARGET_DIR)/usr/bin/llama-server"; \
		ln -sf llama-server "$(TARGET_DIR)/usr/bin/server"; \
	fi
	if [ -f "$(@D)/bin/llama-server" ]; then \
		install -D -m 0755 "$(@D)/bin/llama-server" "$(TARGET_DIR)/usr/bin/llama-server"; \
	fi
endef
LLAMA_CPP_POST_INSTALL_TARGET_HOOKS += LLAMA_CPP_INSTALL_BINARIES

$(eval $(cmake-package))
