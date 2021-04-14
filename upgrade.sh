#!/bin/bash

# Rename output to input 
#mv metadata_output metadata_input
#mv patched_roms_output patched_roms_input

# Fetch latest metadata
git clone --depth 1 https://github.com/speepsio/romdrop.git
mv romdrop/metadata metadata_output
rm -rf romdrop

# Fetch latest patches
git clone --depth 1 https://github.com/speepsio/romdrop-patches.git 
