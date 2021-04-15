#!/bin/bash

# Rename output to input
#mv metadata metadata_input
#mv patched_roms_output patched_roms_input

# Fetch latest metadata
git clone --depth 1 https://github.com/speepsio/romdrop.git
mv romdrop/metadata metadata
rm -rf romdrop

# Fetch latest patches
git clone --depth 1 https://github.com/speepsio/romdrop-patches.git

# Patch stock roms
python3 patch.py

# Migrate user roms
python3 migrate.py
