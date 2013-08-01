#!/usr/bin/env python3
import sys, os
from optparse import OptionParser
import xml.etree.ElementTree as ET

class wholeProgram():
    """The whole program in a class. The program is too small for more classes
;-)."""
    def __init__(self):
        """Set up cmd parser."""
        usage = "usage: %prog [options] INPUTFILE"
        parser = OptionParser(usage=usage)
        parser.add_option("-o", "--output", dest="output",
                  help="set output file (if unset, overwrite input file)",
                  metavar="FILE")
        parser.add_option("-l", "--ligature",
                  action="store_true", dest="ligature", default=False,
                  help='''replace ligatures through normal letters (at least in
Latin languages where they are only for better readibility)''')
        (self.options, self.args) = parser.parse_args()
        if(len(self.args) < 1):
            print("You must at least specify an input file.\n")
            parser.print_help()
            sys.exit(0)
        if(self.options.output == None): self.output = self.args[0]
        else: self.output = self.options.output

        # translation table
        self.T = {}

    def setup_table(self):
        """Set up unicode translation table by parsing XML file and adding
(Latin) ligatures, if wished."""
        root = ET.fromstring( open( os.path.join( \
                os.path.dirname(os.path.realpath(__file__)), 'unicode.xml')).read())
        for child in root:
            if(child.tag == 'character'):
                attr = child.attrib
                try:
                    if(attr['mode'] == 'math'):
                        latex = [e for e in child.getchildren() if(e.tag == 'latex')][0]
                        id = attr['id'][1:]
                        if(id.find('-')>0): ids=id[1:].split('-')
                        else: ids = [id]
                        for id in ids:
                            self.T[int(id, 16)] = latex.text
                except (KeyError, IndexError):
                    continue
        # translate ligatures?
        if(self.options.ligature):
            self.T[64256] = 'ff'
            self.T[64258] = 'fl'
            self.T[64259] = 'ffi'
            self.T[64259] = 'ffl'

    def translate(self):
        """Use self.t to translate all unicode sequences through
LaTeX-equivalents."""
        cnt=open(self.args[0]).read()
        cnt = cnt.translate(self.T)
        open(self.output,'w').write( cnt )

if __name__ == '__main__':
    p = wholeProgram()
    p.setup_table()
    p.translate()
