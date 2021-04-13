import xml.etree.ElementTree as ET
import struct
import pprint

pp = pprint.PrettyPrinter(indent=4)

old_tree = ET.parse('def_old.xml')
old_root = old_tree.getroot()

new_tree = ET.parse('def_new.xml')
new_root = new_tree.getroot()

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

with open("LFG2EL_Rev_201201.bin", "rb") as binaryfile :
    stock_data = bytearray(binaryfile.read())

with open("post-dyno-4-more-timing-under-3k.bin", "rb") as binaryfile2 :
    modified_data = bytearray(binaryfile2.read())

with open("new_patched.bin", "rb") as binaryfile3 :
    new_data = bytearray(binaryfile3.read())


if old_root[0].tag != 'rom':
    print("Input definition not in correct format!")
    exit()

scaling = {}

all_scaling_elements = old_root.findall('.//scaling')

for scaling_element in all_scaling_elements:
    scaling[scaling_element.attrib['name']] = scaling_element.attrib
    #print(scaling_element.attrib['storagetype'])




modified_tables = []

all_table_elements = old_root.findall('.//table')
for child in all_table_elements:
    if child.tag == "table":
        # Check if table modified in input ROM
        # Read data from input ROM if modified

        name = child.attrib['name']
        elements = int(child.attrib['elements'])
        address = int(child.attrib['address'], 16)
        scaling_id = child.attrib['scaling']
        
        storagetype = storagetype_format[scaling[scaling_id]['storagetype']]
        data_length = storagetype_length[scaling[scaling_id]['storagetype']] * elements

        stock = struct.unpack('>' + str(elements) +  storagetype, stock_data[address:address+data_length])
        modified = struct.unpack('>' + str(elements) + storagetype, modified_data[address:address+data_length])


        if stock != modified:
            if elements == 1:
                if storagetype == 'f':
                    print('{} changed! Old: {:0.2f} New: {:0.2f}'.format(name, stock[0], modified[0]))
                    #print(child.attrib['name'] + ' changed! Old: {:.2%} New: {:.2%}'.format(stock[0], modified[0]))
                else:
                    print(child.attrib['name'] + ' changed! Old: {:-9} New: {:-9}'.format(stock[0], modified[0]))
            else:
                print(child.attrib['name'] + ' changed! Content is a table.')
  
            table_data = {}
            table_data = {
                'name': name,
                'content': modified,
                'elements': elements, 
                'data_length': data_length,
                'storagetype': storagetype,
                'address': address
            }
            modified_tables.append(table_data)

#pp.pprint(modified_tables)

for item in modified_tables:
    all_table_elements = new_root.findall('.//table')
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
        new_data[item['newaddress']:item['newaddress']+item['data_length']] = struct.pack('>' + str(item['elements']) + item['storagetype'], *item['content'])
