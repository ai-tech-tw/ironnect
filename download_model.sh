#!/bin/sh
# download_model.sh - Download the gguf model file
# SPDX-License-Identifier: MIT
# (c) Taiwan Web Technology Promotion Organization

set -e

# Create models directory if it doesn't exist
mkdir -p models/

# Download the model
wget -O models/gemma-3-270m-it-Q4_K_M.gguf \
    https://ncurl.xyz/s/SGi_ypqHR

# Echo completion message
echo "Model downloaded."
