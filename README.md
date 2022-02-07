# Zettelkasten terminal application in python

## Usage

### Navigation

- `CTRL+UP` and `CTRL+DOWN` to cycle through windows (not including index)
- `CTRL+g` (home) to hide/show index window (alas `CTRL+h` is backspace)

### Index Window

- Navigate with `UP`/`DOWN` arrow keys
- `o` (open) to open zettel for viewing
- `e` (edit) to open zettel for editing
- `CTRL+n` (new) to create and edit new zettel
- `r` (refresh) to refresh list (after adding or editing zettel)
- `/` (vim-style) to start a search, then type search query, then `ENTER` to interact with search results or `ESC` to cancel search
- `//` to only search titles rather than full text
- `:` (vim-style) to start a command, then type command, then `ENTER` to execute or `ESC` to cancel. Recognized commands:
    - `protograph` to visualize zettel network using [amackcrane/protograph](https://github.com/amackcrane/protograph)

### Viewer Window

- Scroll with `UP`/`DOWN` arrow keys
- Select links with `LEFT`/`RIGHT` arrow keys
- `e` (edit) to change to editing
- `r` (refresh) to refresh (e.g. in case of new backlinks)
- `ENTER` to open selected link for viewing
- `CTRL+n` (new) to create and edit new zettel
- `CTRL+SHIFT+UP` to expand window vertically, `CTRL+SHIFT+DOWN` to shrink vertically, `CTRL+SHIFT+LEFT` and `CTRL+SHIFT+RIGHT` to expand and shrink horizontally

### Editor Window

- Type to insert text
- Zettel must be written in proper YAML
- `CTRL+a` (emacs-style) to jump to beginning of line, `CTRL+e` (emacs-style) to jump to end
- `CTRL+s` (save) or `CTRL+w` (write) to save
- `CTRL+q` (quit) to close
- `CTRL+o` (open) to change to viewing
- `CTRL+n` (new) to create and edit new zettel
- `CTRL+f` (find) to start a search, then `UP`/`DOWN` to interact with results, `ENTER` to insert selected link, `ESC` to cancel (begin search with `/` to only search titles)
- `CTRL+SHIFT+UP` to expand window vertically, `CTRL+SHIFT+DOWN` to shrink vertically, `CTRL+SHIFT+LEFT` and `CTRL+SHIFT+RIGHT` to expand and shrink horizontally

## Setup

- Put repo somewhere on y'r machine
- Edit `config.py` to direct `path` towards repo
- Create `kasten` directory top level in repo (as specified in `config.py`)
- Maybe edit `Keys.py` if your compty has different key codes?
- Run `zk.py` and enjoy
