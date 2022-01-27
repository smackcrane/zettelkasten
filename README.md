# Zettelkasten CLI in python

## Usage

### Navigation

- `CTRL+UP` and `CTRL+DOWN` to cycle through windows

### Index Window

- Navigate with `UP`/`DOWN` arrow keys
- `o` to open zettel for viewing
- `e` to open zettel for editing
- `CTRL+n` to create and edit new zettel
- `r` to refresh list (after adding or editing zettel)
- `/` to start a search, then type search query, then `ENTER` to interact with search results or `ESC` to cancel search

### Viewer Window

- Scroll with `UP`/`DOWN` arrow keys
- Select links with `LEFT`/`RIGHT` arrow keys
- `e` to change to editing
- `ENTER` to open selected link for viewing
- `CTRL+n` to create and edit new zettel

### Editor Window

- Type to insert text
- Zettel must be written in proper YAML
- `CTRL+a` to jump to beginning of line, `CTRL+e` to jump to end
- `CTRL+s` or `CTRL+w` to save
- `CTRL+q` to close
- `CTRL+o` to change to viewing
- `CTRL+n` to create and edit new zettel

## Setup

- Put repo somewhere on y'r machine
- Edit `config.py` to direct `path` towards repo
- Create `kasten` directory top level in repo (as specified in `config.py`)
- Maybe edit `Keys.py` if your compty has different key codes?
- Run `zk.py` and enjoy
