# Org to Markdown

This is a simple script to convert from org files to markdown.

## Usage

The script will print the resulting markdown to the screen:

```bash
$ python org2md.py test.org
```

And then here is an example piping this output to file:

```bash
$ python org2md.py test.rst > test.md
```

or you can provide the file path to write it directly:

```bash
$ python org2md.py test.rst test.md
```
