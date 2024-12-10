#!/usr/bin/env python

import sys
import os
import re

# Supporting Functions

def read_file(filename, mode='r'):
    '''read the content of a file into lines'''
    with open(filename, mode, encoding='utf-8') as filey:
        content = filey.readlines()
    return content

def write_file(filename, content, mode='w'):
    '''read the content of a file into lines'''
    with open(filename, mode, encoding='utf-8') as filey:
        filey.write(content)

def apply_lines(func, content):
    def wrapper():
        lines = []
        for line in content:
            line = func(line)
            lines.append(line)
        return lines
    return wrapper

# Converter

class MarkdownConverter:

    def __init__(self, source, dest):
        self.source = self._check_path(source)
        self.dest = dest

    def run(self):

        # If printing to terminal, might pipe to file, must be quiet
        if self.dest:
            print("Transforming Org from '%s' to MarkDown syntax..." % self.source)

        lines = read_file(self.source)
        lines = apply_lines(self._convert_headers, lines)()
        lines = apply_lines(self._convert_emphasis, lines)()
        lines = apply_lines(self._convert_links, lines)()
        lines = apply_lines(self._convert_codeblocks, lines)()
        lines = apply_lines(self._convert_lists, lines)()

        if self.dest:
            print("Writing output to %s" % self.dest)
            write_file(self.dest, ''.join(lines))
        else:
            print(''.join(lines))


# Conversion Functions ---------------------------------------------------------
# Each function below handles parsing one line, and should be wrapped by
# apply_lines, with the function as the first argument, and a list
# of lines as the second:  apply_lines(func, lines)(). This is a lazy
# man's decorator :)


    def _convert_lists(self, line):
        '''handle bullets in lists.
        '''
        # if line.startswith('::-'):
        #     line = line.replace('::-', '  -', 1)
        return line

    def _convert_links(self, line):
        '''convert a org link to a standard markdown one.

           [[https://slurm.schedmd.com/pdfs/summary.pdf][Slurm commands]]
           to
           [Slurm Commands](https://slurm.schedmd.com/pdfs/summary.pdf)
           
           ![img](data/test.png) to ![](data/test.png)
           [[file:attachment/ipv6_faq.img.39ca12b7.png]] to ![](attachment/ipv6_faq.img.39ca12b7.png)
        '''
        # External Links convert to markdown
        markup_regex = '\[\[(http[s]?://.+?)\]\[(.+?)\]\]'
        # First address external links
        for match in re.findall(markup_regex, line):
            #print("match is", match)
            url, text = match
            markdown = "[%s](%s)" %(text.strip(), url.strip())
            line = line.replace("[[%s][%s]]" % (url, text), markdown)

        IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg"}
        markup_regex = '\[\[file:(.+?)\]\]'
        # First address external links
        for match in re.findall(markup_regex, line):
            #print("match is", match)
            file_path = match
            file_name = file_path.split("/")[-1]
            file_extension = "." + file_name.split(".")[-1].lower()
            if file_extension in IMAGE_EXTENSIONS:
                markdown = "![%s](%s)" %(file_name.strip(), file_path.strip())
            else:
                markdown = "[%s](%s)" %(file_name.strip(), file_path.strip())
            line = line.replace("[[file:%s]]" % (file_path), markdown)

        return line
         

    def _convert_headers(self, line):
        '''convert headers to markdown, e.g
           ** Cluster description == --> ## Cluster Description
           This function should be handled by the apply_lines wrapper.
        '''
        if line.startswith('*'):
            markup_regex = '\*+[ ]+[^*]+'
            if not re.match(markup_regex, line):
                return line
            header = line.split(" ")[0]
            # line = line.rstrip().rstrip(header).strip()
            line = line.replace('*', "#", len(header))
        return line


    def _convert_codeblocks(self, line):
        '''convert source blocks (#+begin_src c #+end_src) to ```
        '''
        code = "```"
        if line.startswith("#+begin_src"):
             lang = (line.replace("#+begin_src", "").strip())
             if lang:
                 code = "%s%s\n" %(code, lang)
             line = code
        line = line.replace("#+end_src", "```")
        return line

    def _convert_emphasis(self, line):
        '''convert in text code (e.g. ''only'') to markdown for bold
           or italic.
           [ ]inline_code[ ] -> [ ]`inline_code`[ ]
           [ ]inline_code$ -> [ ]`inline_code`$
           ^~inline_code~[ ] -> ^`inline_code`[]
           ^~inline_code~$ -> ^`inline_code`$
        '''
        groups = [
                  ("*", "*", "**"), # bold
                  ("/", "/", "_"), # italic
                  ("~", "~", "`"), # code blocks
                  ("=", "=", "`") # verbatim
                 ]
        for group in groups:
            left, right, new = group
            pattern = r"(?:(?<=\s)|^)" + re.escape(left) + r"([^\s" + re.escape(right) + r"][^"+ re.escape(right) + r"]*?)" + re.escape(right) + r"(?:(?=\s)|$)"
            for match in re.findall(pattern, line):
                #print("em match", match)
                inner = new + match + new
                line = line.replace(left + match + right, inner)
        return line


    def _check_path(self, path):
        path = os.path.abspath(path)
        if os.path.exists(path):
            return path
        else:
            raise ValueError("Cannot access file at '%s'" % path)
 
if __name__=="__main__":
    if len(sys.argv) == 1:
        print("Input file is required!\n")
        print("Usage: python rst2md.py input [output]")
        sys.exit(1)

    source = sys.argv[1]

    dest = None
    if len(sys.argv) > 2:
        dest = sys.argv[2]

    converter = MarkdownConverter(source, dest)
    converter.run()
