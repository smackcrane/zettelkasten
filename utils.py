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

def debugger(s):
    log = '/dev/pts/3'
    with open(log, 'w') as f:
        print(s, file=f)

# entry point: list of IDs and titles
def list_IDs_titles():
    IDs = os.listdir(path=kasten_dir)

    zett = []
    for ID in IDs:
        with open(kasten_dir+ID, 'r') as f:
            try:
                zettel = yaml.load(f, Loader=yaml.SafeLoader)
                zett += [{'ID': ID, 'TITLE': zettel['TITLE']}]
            except Exception as e:
                zett += [{'ID': ID,
                    'TITLE': '----- ERROR ----- '+' '.join(str(e).split())}]
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

# list IDs of zettel that link to target ID
def list_backlinks(target):
    IDs = os.listdir(kasten_dir)    # get list of IDs
    link = re.compile(f'#{target}') # regex to match link to target ID
    backlinks = []
    for ID in IDs:
        with open(kasten_dir+ID, 'r') as f:
            text = f.read()
        match = link.search(text)   # search for link in filetext
        if match:
            backlinks.append(ID)    # if we found one, add ID to list
    return backlinks

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
    
    # if search_text begins with '/', (remove it and) only search titles
    if search_text[:1] == '/':
        search_text = search_text[1:]
        search_type = 'title'
    # if search_text begins with '#', (remove it and) only search IDs
    elif search_text[:1] == '#':
        search_text = search_text[1:]
        search_type = 'ID'
    else:
        search_type = 'full_text'
    zett = []
    for ID in IDs:
        with open(kasten_dir+ID, 'r') as f:
            if search_type == 'title' or search_type == 'ID':
                try:
                    zettel = yaml.load(f, Loader=yaml.SafeLoader)
                    zettel['TITLE'] = zettel['TITLE'] or '' # beware None
                    # caution: oversize load
                    if (search_type == 'title' and search_text.lower() in zettel['TITLE'].lower()) or (search_type == 'ID' and search_text.lower() in ID):
                        zett.append({'ID':ID, 'TITLE': zettel['TITLE']})
                except:
                    # if we can't read the yaml then just ignore it
                    pass
            else: # search_type == 'full_text'
                file_text = f.read()
                # add to the list if we found the search text
                if search_text.lower() in file_text.lower():
                    try:
                        f.seek(0) # go back to beginning of file
                        zettel = yaml.load(f, Loader=yaml.SafeLoader)
                        zett.append({'ID': ID, 'TITLE': zettel['TITLE']})
                    except yaml.scanner.ScannerError:
                        zett.append({'ID': ID,
                            'TITLE': '-'*15 +
                                ' HELP MY YAML IS BROKEN ' +
                                '-'*15})
    return zett

# generate graph using protograph
def protograph(directed=False):
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
            # add edge to list in protograph format, both ways if undirected
            # recall pg indexes by 1, so +1 everywhere
            if not directed:
                forward = f'edge {i+1} {j+1}'
                backward = f'edge {j+1} {i+1}'
                if forward not in edge_list: # check to avoid duplicates
                    edge_list.append(forward)
                if backward not in edge_list:
                    edge_list.append(backward)
            else:
                edge_list.append(f'edge {i+1} {j+1}')
    # set commands to define nodes, define edges, then render
    commands = '\n'.join(node_list + edge_list + ['render'])
    commands += '\n'    # file-end newline for unix happiness
    # write to temp file
    temp_file = '/tmp/zk_to_pg.txt'
    with open(temp_file, 'w') as f:
        f.write(commands)
    # call pg on temp file
    os.system(f'pg -f {temp_file} >/dev/null 2>&1')

# convert row numbers between Viewer and Editor
# give it one of the two, it returns the other
def convert_row(ID, cols, viewer_row=None, editor_row=None):
    assert viewer_row != None or editor_row != None, 'must provide row'
    line_lengths = []
    with open(kasten_dir+ID, 'r') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line:
                # empty line still takes up one row
                line_lengths.append(1)
            else:
                # ceiling division to find number of rows
                line_lengths.append( -(len(line) // -cols) )
    if viewer_row != None:
        # convert from viewer to editor
        editor_row = 0
        viewer_row -= line_lengths[0]
        while viewer_row >= 0:
            editor_row += 1
            viewer_row -= line_lengths[editor_row]
        # done, now delete viewer_row so editor_row gets returned
        viewer_row = 0
    else: # editor_row != None
        # convert from editor to viewer
        viewer_row = sum(line_lengths[:editor_row])
        # done, now delete editor_row so viewer_row gets returned
        editor_row = 0
    # after converting the one to the other we set the one to zero, so
    #   this will return the other
    return viewer_row or editor_row
