import xml.etree.ElementTree as ET
import struct
import pprint
import os

input_metadata_dir = "metadata_input"
output_metadata_dir = "metadata_output"
input_patched_roms_dir = "patched_roms_input"
output_patched_roms_dir = "patched_roms_output"

def check_if_rom_matches_definition(romid, rom_contents):
    internalidaddress = int(romid.find('.//internalidaddress').text,16)
    internalidstring = romid.find('.//internalidstring').text
    ecuid = romid.find('.//ecuid').text
    input_rom_string = struct.unpack(str(len(internalidstring)) + "s", rom_contents[internalidaddress:internalidaddress+len(internalidstring)])[0]
    if input_rom_string == internalidstring:
        return True
    else:
        return False

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
            if check_if_rom_matches_definition(romid, rom_contents):
                return def_file
    return ""

# Loop over directory looking for definition matching rom contents
def find_patched_rom_in_directory(path, def_to_match):
    for filename in os.listdir(path):
        if filename.endswith(".bin"):
            bin_file = os.path.join(path, filename)
            with open(bin_file, "rb") as binaryfile :
                rom_data = bytearray(binaryfile.read())
            romid = def_to_match.find('.//romid')
            if check_if_rom_matches_definition(romid, rom_data):
                return bin_file
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

# Open rom to migrate
with open("rom_to_migrate.bin", "rb") as binaryfile:
    modified_data = bytearray(binaryfile.read())

# Find input and output definitions
print("Scanning metadata for correct definition...")
input_def = find_def_in_directory(modified_data, input_metadata_dir)
if input_def == "":
    print("Input definition not found in {}!".format(input_metadata_dir))
else:
    print("Input definition found! {}".format(input_def))

output_def = find_def_in_directory(modified_data, output_metadata_dir)
if output_def == "":
    print("Output definition not found in {}!".format(output_metadata_dir))
else:
    print("Output definition found! {}".format(output_def))

# Open definitions again
input_tree = ET.parse(input_def)
input_root = input_tree.getroot()

output_tree = ET.parse(output_def)
output_root = output_tree.getroot()

# Locate patched roms
input_patched_rom = find_patched_rom_in_directory(input_patched_roms_dir, input_root)

if input_patched_rom == "":
    print("Input patched rom not found in {}!".format(input_patched_roms_dir))
else:
    print("Input patched rom found! {}".format(input_patched_rom))

output_patched_rom = find_patched_rom_in_directory(output_patched_roms_dir, input_root)

if output_patched_rom == "":
    print("Output patched rom not found in {}!".format(output_patched_roms_dir))
else:
    print("Output patched rom found! {}".format(output_patched_rom))

# Open patched roms
with open(input_patched_rom, "rb") as binaryfile:
    stock_data = bytearray(binaryfile.read())
with open(output_patched_rom, "rb") as binaryfile:
    output_data = bytearray(binaryfile.read())

scaling = {}

input_tree = ET.parse(input_def)
input_root = input_tree.getroot()

output_tree = ET.parse(output_def)
output_root = output_tree.getroot()

all_scaling_elements = input_root.findall('.//scaling')

for scaling_element in all_scaling_elements:
    scaling[scaling_element.attrib['name']] = scaling_element.attrib

modified_tables = []

# Iterate over all tables in input ROM - find all tables where data has been changed compared to the stock patched rom
all_table_elements = input_root.findall('.//table')
for child in all_table_elements:
    name = child.attrib['name']
    elements = int(child.attrib['elements'])
    address = int(child.attrib['address'], 16)
    scaling_id = child.attrib['scaling']

    storagetype = storagetype_format[scaling[scaling_id]['storagetype']]
    data_length = storagetype_length[scaling[scaling_id]['storagetype']] * elements

    # Extract table data from both stock and input ROMs
    stock = struct.unpack('>' + str(elements) +  storagetype, stock_data[address:address+data_length])
    modified = struct.unpack('>' + str(elements) + storagetype, modified_data[address:address+data_length])

    # Compare table data
    if stock != modified:
        if elements == 1:
            if storagetype == 'f':
                print('{} changed! Old: {:0.2f} New: {:0.2f}'.format(name, stock[0], modified[0]))
                #print(child.attrib['name'] + ' changed! Old: {:.2%} New: {:.2%}'.format(stock[0], modified[0]))
            else:
                print(child.attrib['name'] + ' changed! Old: {:-9} New: {:-9}'.format(stock[0], modified[0]))
        else:
            print(child.attrib['name'] + ' changed! Content is a table.')

        table_data = {
            'name': name,
            'content': modified,
            'elements': elements,
            'data_length': data_length,
            'storagetype': storagetype,
            'address': address
        }
        modified_tables.append(table_data)

# Iterate over all modified values.  Locate corresponding table in output patched ROM, overwrite with data from input ROM
for item in modified_tables:
    all_table_elements = output_root.findall('.//table')
    found = False
    for table in all_table_elements:
        if table.attrib['name'] == item['name'] and int(table.attrib['address'],16) == item['address']:
            if int(table.attrib['elements']) == item['elements']:
                found = True
                #print("{}: Matching table found by name in new definition XML".format(item['name']))
                item['newaddress'] = int(table.attrib['address'],16)
            else:
                found = False
                print("{}: Matching table found by name in new definition XML, but element number has changed Old: {} New: {}".format(item['name'], int(table.attrib['elements']), item['elements']))
        elif int(table.attrib['address'],16) == item['address']:
            if int(table.attrib['elements']) == item['elements']:
                found = True
                #print("{}: Matching table found by address / length in new definition XML".format(item['name']))
                item['newaddress'] = int(table.attrib['address'],16)
            else:
                found = False
                print("{}: Matching table found by address in new definition XML, but element number has changed Old: {} New: {}".format(item['name'], int(table.attrib['elements']), item['elements']))
    if found == False:
            print("{}: Matching table NOT in new definition XML - looking for match by address".format(item['name']))
    else:
        # Write data into new ROM binary
        print("Writing {}: {} bytes to address {}".format(item['name'], item['data_length'], item['newaddress']))
        output_data[item['newaddress']:item['newaddress']+item['data_length']] = struct.pack('>' + str(item['elements']) + item['storagetype'], *item['content'])

output_file = open("output.bin", "wb")
output_file.write(output_data)
