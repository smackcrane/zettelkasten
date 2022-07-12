# Zettelkasten-style notes application for terminal

## Usage

### Navigation

- `CTRL+UP` and `CTRL+DOWN` to cycle through windows (not including index)
- `CTRL+g` (home) to hide/show index window (alas `CTRL+h` is backspace)
- `CTRL+n` (new) to create and edit new zettel

### Index Window

- Navigate with `UP`/`DOWN` arrow keys
- `o` (open) or `ENTER` to open zettel for viewing
- `e` (edit) to open zettel for editing
- `r` (refresh) to refresh list (after adding or editing zettel)
- `/` (vim-style) to start a search, then type search query, then `ENTER` to interact with search results or `ESC` to cancel search

### Viewer Window

- Scroll with `UP`/`DOWN` arrow keys
- Select links with `LEFT`/`RIGHT` arrow keys
- `e` (edit) to change to editing
- `r` (refresh) to refresh (e.g. in case of new backlinks)
- `ENTER` to open selected link for viewing

### Editor Window

- Type to insert text
- Zettel must be written in proper YAML (usually just write notes indented in `BODY:` field)
- `CTRL+s` (save) to save
- `CTRL+w` (browser/etc-style) to close
- `CTRL+x` (cut) to cut current line to clipboard
- `CTRL+v` (paste) to paste last cut below current line (and repeat to paste previous cuts)
- `CTRL+o` (open) to change to viewing
- `CTRL+f` (find) to start a search, then `UP`/`DOWN` to interact with results, `ENTER` to insert selected link, `ESC` to cancel (begin search with `/` to only search titles, '#' to only search IDs)

## Setup

- Put repo somewhere on y'r machine
- Edit `config.py` to direct `path` towards repo
- Create `kasten` directory top level in repo (as specified in `config.py`)
- Maybe edit `Keys.py` if your compty has different key codes?
- Run `zk.py` and enjoy

### `exec` Disclaimer

This application allows you to write arbitrary python code in notes, which will be `exec`'d (see `CODE:` below). This is great for writing dynamic notes in y'r fancy electronic notebook, but obviously unsuitable for any application that requires security.

## Advanced Techniques

- Windows can be resized using `CTRL+SHIFT+UP` (expand vertically), `CTRL+SHIFT+DOWN` (shrink vertically), `CTRL+SHIFT+RIGHT`, and `CTRL+SHIFT+LEFT` (expand and shrink horizontally)
- In index window, use `:` (vim-style) to start a command, then type command, then `ENTER` to execute or `ESC` to cancel. Recognized commands:
    - `protograph` to visualize zettel network using [amackcrane/protograph](https://github.com/amackcrane/protograph)
    - `count` to count the current list of zettel in index
    - `sort` to sort current list by ID
- In index window, use `//` to only search titles rather than full text, `/#` to search IDs
- In Editor, use `CTRL+a` (emacs-style) to jump to beginning of line, `CTRL+e` (emacs-style) to jump to end
- Viewer will recognize strings like `https://blah` or `http://blah` as hyperlinks and make them active---pressing `ENTER` will open in firefox
- Viewer will recognize strings like `~/foo/bar.baz` as filepaths and make them active---.jpg and .pdf extensions will be opened with qpdfview (other extensions/filetypes not yet supported, also only paths starting with `~/`)
- Adding a `CODE:` field in editor will cause the viewer to execute the contents of the field as python code and show the output
