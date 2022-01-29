############################################################################
#
#   utils.py
#       utility functions for zettelkasten implementation in python
#
############################################################################

import yaml
import datetime
import re
import os
from config import kasten_dir, template_file

# entry point: list of IDs and titles
def list_IDs_titles():
    IDs = os.listdir(path=kasten_dir)

    zett = []
    for ID in IDs:
        with open(kasten_dir+ID, 'r') as f:
            try:
                zettel = yaml.load(f, Loader=yaml.SafeLoader)
                zett += [{'ID': ID, 'TITLE': zettel['TITLE']}]
            except yaml.scanner.ScannerError:
                zett += [{'ID': ID,
                    'TITLE': '-'*15+' HELP MY YAML IS BROKEN '+'-'*15}]
    return zett

# load zettel from ID
def load_zettel(ID):
    try:
        with open(kasten_dir+ID, 'r') as f:
                zettel = yaml.load(f, Loader=yaml.SafeLoader)
    except Exception as e:
        zettel = {'ID': ID,
                'TITLE': str(e),
                'BODY': str(e)}
    # insist on returning string title and body
    if 'TITLE' not in zettel or not isinstance(zettel['TITLE'], str):
        zettel['TITLE'] = ''
    if 'BODY' not in zettel or not isinstance(zettel['BODY'], str):
        zettel['BODY'] = ''
    return zettel

# increment letters in IDs, a -> b -> ... -> z -> aa -> ab -> ...
def increment_letters(letters):
    # convert letters to list of numbers a=0, ..., z=25
    numbers = [ord(c)-97 for c in list(letters)][::-1]
    for i in range(len(numbers)):
        if numbers[i] < 25:
            numbers[i] += 1
            break
        else: # carry
            numbers[i] = 0
    else: # carried all the way through, need to add another letter
        numbers += [0]
    # convert back to letters
    letters = ''.join([chr(x+97) for x in numbers[::-1]])
    return letters

# sort key for sorting IDs
def ID_sort(ID):
    YYMMDD = ID.rstrip('abcdefghijklmnopqrstuvwxyz')
    letters = ID.lstrip('0123456789')
    # in descending order of priority:
    #   date, then number of letters, then lexicographic order of letters
    return [YYMMDD, len(letters), letters]

# create a new zettel and return ID
def new_zettel():
    # find ID: YYMMDD followed by letters a, b, ..., z, aa, ab, ...
    YYMMDD = datetime.date.today().isoformat().replace('-','')[2:]
    IDs = sorted(os.listdir(path=kasten_dir), key=ID_sort)
    if len(IDs) > 0:
        last = IDs[-1]
    else:
        last = ''
    if last[:6] == YYMMDD:
        # if it's the same YYMMDD as the last, increment letters
        letters = increment_letters(last[6:])
    else: # otherwise just start from the beginning
        letters = 'a'
    ID = YYMMDD + letters

    # create file from template
    with open(template_file, 'r') as f:
        template = f.read()
    template = template.replace('YYMMDDxx', ID)
    with open(kasten_dir+ID, 'w') as f:
        f.write(template)

    return ID

# search zettels for text, return list of ID & title dicts
def search_IDs_titles(search_text):
    IDs = os.listdir(path=kasten_dir)

    zett = []
    for ID in IDs:
        with open(kasten_dir+ID, 'r') as f:
            file_text = f.read()
            # only add to the list if we found the search text
            if search_text.lower() in file_text.lower():
                try:
                    f.seek(0) # go back to beginning of file
                    zettel = yaml.load(f, Loader=yaml.SafeLoader)
                    zett += [{'ID': ID, 'TITLE': zettel['TITLE']}]
                except yaml.scanner.ScannerError:
                    zett += [{'ID': ID,
                        'TITLE': '-'*15+' HELP MY YAML IS BROKEN '+'-'*15}]
    return zett

# generate graph using protograph
def protograph():
    IDs = os.listdir(kasten_dir)
    link = re.compile(r'#\d+[a-z]+')    # regex to match links in notes
    node_list = []
    edge_list = []
    for i, ID in enumerate(IDs):
        with open(kasten_dir+ID, 'r') as f:
            text = f.read()     # grab text to search for links
            f.seek(0)
            try:                # grab data to extract title
                data = yaml.load(f, Loader=yaml.SafeLoader)
            except yaml.scanner.ScannerError:
                data = {'TITLE': '--BROKEN YAML--'}
        # add node with ID and title to list in protograph format
        node_list.append(f'node {ID} --hovertext {data["TITLE"]}')
        # for each link
        for link_ID in link.findall(text):
            # get node number of linked zettel
            j = IDs.index(link_ID.lstrip('#'))  # (get rid of leading hash)
            # add edge to list in protograph format
            edge_list.append(f'edge {i+1} {j+1}') # recall pg indexes by 1
    # set commands to define nodes, define edges, then render
    commands = '\n'.join(node_list + edge_list + ['render'])
    commands += '\n'    # file-end newline for unix happiness
    # write to temp file
    temp_file = '/tmp/zk_to_pg.txt'
    with open(temp_file, 'w') as f:
        f.write(commands)
    # call pg on temp file
    os.system(f'pg -f {temp_file} >/dev/null 2>&1')
