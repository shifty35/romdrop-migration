import xml.etree.ElementTree as ET
import os
import struct
import configparser
config = configparser.ConfigParser()
config.read('romdrop-migrate.ini')

stock_roms_dir = config['directories']['stock_roms_dir'] 
patch_dir = config['directories']['patch_dir'] 
patched_roms_dir = config['directories']['output_patched_roms_dir']
metadata_dir = config['directories']['output_definitions_dir']




[directories]
input_definitions_dir = metadata_input
output_definitions_dir = metadata
input_patched_roms_dir = patched_roms_input
output_patched_roms_dir = patched_roms_output
user_roms_dir = user_roms
user_roms_output_dir = user_roms_output
stock_roms_dir = stock_roms
patch_dir = romdrop_patches



def check_if_rom_matches_definition(romid, rom_contents):
    internalidaddress = int(romid.find('.//internalidaddress').text,16)
    internalidstring = romid.find('.//internalidstring').text
    ecuid = romid.find('.//ecuid').text
    input_rom_string = struct.unpack(str(len(internalidstring)) + "s", rom_contents[internalidaddress:internalidaddress+len(internalidstring)])[0]
    if input_rom_string.decode('ascii')== internalidstring:
        return internalidstring 
    else:
        return ""

# Loop over directory looking for definition matching rom contents
def find_def_in_directory(rom_contents, path):
    for filename in os.listdir(path):
        if filename.endswith(".xml"):
            def_file = os.path.join(path, filename)
            tree = ET.parse(def_file)
            root = tree.getroot()
            if root[0].tag != 'rom':
                print("{} - not in correct format!".format(def_file))
            romid = root.find('.//romid')
            internalidstring =  check_if_rom_matches_definition(romid, rom_contents)
            if internalidstring != "":
                return internalidstring
    return ""

# Loop over directory looking for definition matching rom contents
def find_patch_in_directory(path, romidstring):
    for filename in os.listdir(path):
        if romidstring.lower() in filename.lower():
            return filename
    return ""

storagetype_format = {
    "float": 'f',
    "uint16": 'H',
    "uint32": 'I',
    "uint8": 'B'
}

storagetype_length = {
    "float": 4,
    "uint16": 2,
    "uint32": 4,
    "uint8": 1
}


for filename in os.listdir(stock_roms_dir):
    # Open rom to migrate
    with open(os.path.join(stock_roms_dir, filename), "rb") as binaryfile:
        stock_rom_data = bytearray(binaryfile.read())

    print("Found stock ROM: {} - attempting to patch".format(filename))

    # Find input and output definitions
    print("Scanning metadata for correct definition...")
    rom_id_string = find_def_in_directory(stock_rom_data, metadata_dir)

    if rom_id_string == "":
        print("Unable to determine ROM identifier for stock rom: {}!".format(filename))
        exit()

    print("Found ROM ID: {}".format(rom_id_string))
    print("Searching for appropriate patch...")

    # Locate patch
    patchfile = find_patch_in_directory(patch_dir, rom_id_string)

    if patchfile == "":
        print("Unable to find patchfile for stock rom: {}!".format(filename))
        exit()

    print("Found patch file: {}".format(patchfile))

    # Open patch
    with open(os.path.join(patch_dir, patchfile), "rb") as binaryfile:
        patch_data = bytearray(binaryfile.read())

    output_data = patch_data

    # apply patch
    for i in range(len(patch_data)):
        output_data[i] = stock_rom_data[i] ^ patch_data[i]

    print("Writing patched ROM: {}".format(os.path.join(patched_roms_dir, filename)))

    output_file = open(os.path.join(patched_roms_dir, filename), "wb")
    output_file.write(output_data)
