#!/bin/python3

############################################################################
#
#   utils.py
#       utility functions for zettelkasten implementation in python
#
############################################################################

import yaml
import datetime
import os
from config import kasten_dir

# entry point: list of IDs and titles
def list_IDs_titles():
    IDs = os.listdir(path=kasten_dir)

    zett = []
    for ID in IDs:
        with open(kasten_dir+ID, 'r') as f:
            zettel = yaml.load(f, Loader=yaml.SafeLoader)
            zett += [{'ID': ID, 'TITLE': zettel['TITLE']}]
    return zett

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
    
# create an ID for a new zettel
def new_ID():
    # YYMMDD followed by a, b, ..., z, aa, ab, ...
    YYMMDD = datetime.date.today().isoformat().replace('-','')[2:]
    IDs = sorted(os.listdir(path=kasten_dir)) # is there a faster way?
    last = IDs[-1]
    if last[:6] == YYMMDD:
        # if it's the same YYMMDD as the last, increment letters
        letters = increment_letters(last[6:])
    else: # otherwise just start from the beginning
        letters = 'a'
    return YYMMDD + letters

#    # open template file for editing
#    with open('/tmp/zettel.yaml', 'w') as f:
#        yaml.dump(zettel_template, f)
#    os.system('vim /tmp/zettel.yaml')
#    os.system(f'mv /tmp/zettel.yaml {kasten_dir}{ID}')
