# Counts lb per cb/pb.
# Input: Document in XML format.
# Output: lb count statistics (PB CB LB#) appended to output file.
# Created: 1 October 2019, Violeta Seretan
# Usage: python transcription-lb.py -i <inputFile> -o <outputFile>
# Example:
# python3 transcription-lb.py -i ~/Documents/data/2019-08-latin/BHL983/Berne111.xml -o temp

import os, sys, getopt
import fnmatch
import string
import re
from io import open

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
        number = "No number"
    else:
        number = res.group(1)
        # get n as the first captured group
    return number

def count_lb(xmllines, inputfname, outputfname):

    outContent = ""
    tags = ["pb", "cb", "lb"]

    pbCounter, cbCounter, lbCounter = (0, 0, 0)
    for line in xmllines:
        for m in tagsearch(tags, line):
            if m[0] == "pb":
                pbCounter += 1
            elif m[0] == "cb":
                cbCounter += 1
            elif m[0] == "lb":
                lbCounter += 1
    outContent += os.path.basename(inputfname) # write file name without path
    outContent += "\t(PB: " + str(pbCounter)
    outContent += "\tCB: " + str(cbCounter)
    outContent += "\tLB: " + str(lbCounter) + ")"

    folios = []
    lbs = []
    lbCounter = 0
    for idxl, line in enumerate(xmllines):
        match = tagsearch(tags, line)
        thisFolioAppendix = ""
        for idxm, m in enumerate(match):
            if (m[0] == "pb") or (m[0] == "cb"):
                if (m[0] == "pb"):
                    thisFolio = getNumber(m[1])
                if (m[0] == "cb"):
                    thisFolioAppendix = "/" + getNumber(m[1])

                # avoid cutting twice on pb cb
                if (m[0] == "cb") or (m[0] == "pb" and \
                        not ((idxm + 1 < len(match)) and (match[idxm + 1][0] == 'cb')) and \
                        not ((idxl < len(xmllines) - 1 ) \
                            and (len(tagsearch(tags, xmllines[idxl + 1])) > 0) \
                            and tagsearch(tags, xmllines[idxl + 1])[0][0] == 'cb')): # no cb on next line either
                     # print("Cutting point: " + str(m) + " in line: " + line)
                    folios.append(thisFolio + thisFolioAppendix)
                    lbs.append(lbCounter)
                    lbCounter = 0
            elif m[0] == "lb":
                lbCounter += 1
        if idxl == len(xmllines) - 1:
            lbs.append(lbCounter)

    # print(folios)
    # print(lbs)
    for (x, y) in zip(folios, lbs[1:]):
        outContent += "\n\t" + x + "\t" + str(y)

    if (len(set(lbs[2:-1])) > 1):
         outContent += "\n\t\t!!! (suspicious number of lines)"

    outContent += "\n"
    if outputfname:
        outFile = open(outputfname, "a")
        outFile.write(outContent)
        outFile.close()
    else:
        print (outContent)

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
            print ('transcription-lb.py -i <inputFile> -o <outputFile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    if (inputfile == ""):
        # print("Command line error.")
        # print("Usage:" + 'transcription-lb.py -i <inputFile> -o <outputFile>')
        print("No arguments found; processing current directory")
        for infile in fnmatch.filter(os.listdir (os.getcwd()), '*.xml'):
            with open (infile, encoding='utf-8') as f:
                fl =f.readlines()
                count_lb(fl, infile, infile + "_lb.txt")
        sys.exit(0)
    if not(os.path.exists(inputfile)):
        print("Check input file.")
        sys.exit(2)
    if not(os.path.isfile(inputfile) and os.path.getsize(inputfile) > 0):
        print("Empty input file.")
        sys.exit(2)


    with open (inputfile, encoding='utf-8') as f:
        fl =f.readlines()
        count_lb(fl, inputfile, outputfile)

if __name__ == "__main__":
    main(sys.argv[1:])
