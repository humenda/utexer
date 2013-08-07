#!/usr/bin/env python3
import sys, os
from optparse import OptionParser
import xml.etree.ElementTree as ET

"""uTeXer -- replace unicode signs through LaTeX equivalents."""

# A dictionary of unicode signs which one can get when using pdftotext."

PDFTOTEXT = {0xFF:'ß', 0x1C:'fi'}

################################################################################

class WholeProgram():
    """The whole program in a class. The program is too small for more classes
;-)."""
    def __init__(self):
        """Set up cmd parser."""
        usage = "usage: %prog [options] INPUTFILE"
        parser = OptionParser(usage=usage)
        parser.add_option("-o", "--output", dest="output",
                  help="set output file (if unset, overwrite input file)",
                  metavar="FILE")
        parser.add_option("-u", "--userdict", dest="userdict",
                  help="set path to user-defined replacements/additions for "+\
                          "unicode mappings (format described in README)",
                  metavar="FILE", default=None)
        parser.add_option("-l", "--ligature",
                  action="store_true", dest="ligature", default=False,
                  help='replace ligatures through normal letters (at least in'+\
                          ' Latin languages where they are only for better '+\
                          'readibility)')
        parser.add_option("-p", "--pdftotext",
                  action="store_true", dest="pdftotext", default=False,
                  help='Replace some signs generated just by PDFtotext')
        (self.options, self.args) = parser.parse_args()
        if(len(self.args) < 1):
            print("You must at least specify an input file.\n")
            parser.print_help()
            sys.exit(0)
        if(self.options.output == None):
            self.output = self.args[0]
        else:
            self.output = self.options.output

        # translation table
        self.table = {}

    def setup_table(self):
        """Set up unicode translation table by parsing XML file and adding
(Latin) ligatures, if wished."""
        # search unicode.xml in the same directory:
        spath = os.path.dirname(os.path.realpath(__file__))
        if(os.path.exists(os.path.join(spath, 'unicode.xml'))):
            unicodexml = os.path.join(spath, 'unicode.xml')
        elif(os.path.exists(os.path.join(spath, '..', 'share', 'utexer',
                'unicode.xml'))):
            unicodexml = os.path.join(spath, '..', 'share', 'utexer', \
                        'unicode.xml')
        else:
            print("Error: unicode.xml not found!")
            sys.exit(127)

        root = ET.fromstring( open( unicodexml ).read())
        for child in root:
            if(child.tag == 'character'):
                attr = child.attrib
                try:
                    if(attr['mode'] == 'math'):
                        latex = [e for e in child.getchildren() \
                                    if(e.tag == 'latex')][0]
                        i_d = attr['id'][1:]
                        if(i_d.find('-')>0):
                            ids = i_d[1:].split('-')
                        else:
                            ids = [i_d]
                        for i_d in ids:
                            self.table[int(i_d, 16)] = latex.text
                except (KeyError, IndexError):
                    continue
        # translate ligatures?
        if(self.options.ligature):
            self.table[64256] = 'ff'
            self.table[64257] = 'fi'
            self.table[64258] = 'fl'
            self.table[64259] = 'ffi'
            self.table[64260] = 'ffl'
        if(self.options.pdftotext):
            self.table.update(PDFTOTEXT)
        if(self.options.userdict):
            for line in open(self.options.userdict).read().split('\n'):
                try:
                    num, replacement = line.split('\t')
                    self.table[int(num)] = replacement
                except ValueError:
                    continue

    def translate(self):
        """Use self.t to translate all unicode sequences through
LaTeX-equivalents."""
        cnt = open(self.args[0]).read()
        cnt = cnt.translate(self.table)
        if(self.options.pdftotext):
            cnt = self.replace_dieresis(cnt)
        open(self.output,'w').write( cnt )
    
    def replace_dieresis(self, cnt):
        """Replace dieresis occuring when using pdftotext with German texts set
        in LaTeX, inproperly."""
        R = {'\xa8o':'\xf6', '\xa8u':'\xfc', '\xa8a': '\xe4',  \
             '\xa8O':'\xf6', '\xa8U':'\xfc', '\xa8A': '\xe4' }
        for r in R:
            cnt = cnt.replace(r, R[r])
        return cnt


def main():
    prog = WholeProgram()
    prog.setup_table()
    prog.translate()

if __name__ == '__main__':
    main()

