# Automatically number 'lb' tags in file.
# Existing numbering is replaced with new numbering starting either with 1 or with the n value of the first 'lb' tag.
# After each 'pb' and 'cb' tag, numbering restarts with 1.
# Input: XML file.
# Output: A copy of the file with automatically numbered 'lb' tags.
# Created: 2 October 2019, Violeta Seretan
# Usage: python transcription-lbnumber.py -i <inputFile> -o <outputFile>
# Example:
# python3 transcription-lbnumber.py -i ~/Documents/data/2019-08-latin/BHL983/Berne111.xml -o temp

import os, sys, getopt
import fnmatch
import string
import re
from io import open

lbCounter = 1

def tagsearch(tags, line):
    exp = "("
    for idx, t in enumerate(tags):
        exp += t.lower()
        if idx < len(tags) - 1:
            exp += "|"
    exp += ")"
    return re.findall("<" + exp + "(\s*?|\sn=.*?)/>", line.lower())

def getNumber(string):
    # extract the value of n
    res = re.search("n=[\"\'](.*?)[\"\']", string)
    # ? means non greedy
    if res is None:
        number = ""
    else:
        number = res.group(1)
        # get n as the first captured group
    return number

# this function is called for each matching object
def nrepl(matchobj):
    global lbCounter
    string = "<lb n=\"{}\"/>".format(int(lbCounter))
    lbCounter += 1
    return string

def number_lb(xmllines, inputfname, outputfname):
    global lbCounter

    filecontent = ''
    tags = ['lb', 'cb', 'pb']
    flagNumberChecked = False
    for line in xmllines:
        for m in tagsearch(tags, line):
            # go to first lb and read n attribute
            if m[0] == "lb" and not(flagNumberChecked):
                flagNumberChecked = True
                number = getNumber(m[1])
                if number != "" :
                    lbCounter = int(number)

            # reset counter each new page and column
            elif m[0] in ["pb", "cb"]:
                lbCounter = 1

        # incrementally number all lb starting with lbCounter
        line = re.sub(r'<lb(\s*|\sn=.*?)/>', nrepl, line, flags=re.IGNORECASE)
        # '?' is used for non-greedy match
        filecontent += line

    outFile = open(outputfname, "w")
    outFile.write(filecontent)
    outFile.close()

def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:o:",["ifile=","ofile="])
    except getopt.GetoptError as err:
        print("Command line error.")
        # print help information and exit:
        print(str(err))  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('transcription-lbnumber.py -i <inputFile> -o <outputFile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    if (outputfile == ""): # write to same file
        outputfile = inputfile;

    if (inputfile == "") and (outputfile == ""): # empty arguments: process current folder
        for infile in fnmatch.filter(os.listdir (os.getcwd()), '*.xml'):
            with open (infile, encoding='utf-8') as f:
                number_lb(f.readlines(), infile, infile) # write to the same file
                print(infile) # print file name
        sys.exit(0)

    if not(os.path.exists(inputfile)):
        print("Check input file.")
        sys.exit(2)
    if not(os.path.isfile(inputfile) and os.path.getsize(inputfile) > 0):
        print("Empty input file.")
        sys.exit(2)

    with open (inputfile, encoding='utf-8') as f:
        number_lb(f.readlines(), inputfile, outputfile)

if __name__ == "__main__":
    main(sys.argv[1:])
