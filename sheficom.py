#!/usr/bin/python2
#
# This file is part of the sheficom distribution (https://github.com/mikedorin/sheficom).
# Copyright (c) 2022 Michael Dorin.
# 
# This program is free software: you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import os
import re
from collections import defaultdict
import sys

#
# The code for removing comments is all from other people.
# I have done my best to make sure links to their work are included.
#
# Thank you Kev NoNo, arita37
# https://gist.github.com/arita37/762ba3c5263a7bdcec92bc1c5fe1
# Remove C Style Comments
#
def removeCommentsxx(text):
    """ remove c-style comments.
        text: blob of text with comments (can include newlines)
        returns: text with comments removed
    """
    pattern = r"""
                            ##  --------- COMMENT ---------
           //.*?$           ##  Start of // .... comment
         |                  ##
           /\*              ##  Start of /* ... */ comment
           [^*]*\*+         ##  Non-* followed by 1-or-more *'s
           (                ##
             [^/*][^*]*\*+  ##
           )*               ##  0-or-more things which don't start with /
                            ##    but do end with '*'
           /                ##  End of /* ... */ comment
         |                  ##  -OR-  various things which aren't comments:
           (                ##
                            ##  ------ " ... " STRING ------
             "              ##  Start of " ... " string
             (              ##
               \\.          ##  Escaped char
             |              ##  -OR-
               [^"\\]       ##  Non "\ characters
             )*             ##
             "              ##  End of " ... " string
           |                ##  -OR-
                            ##
                            ##  ------ ' ... ' STRING ------
             '              ##  Start of ' ... ' string
             (              ##
               \\.          ##  Escaped char
             |              ##  -OR-
               [^'\\]       ##  Non '\ characters
             )*             ##
             '              ##  End of ' ... ' string
           |                ##  -OR-
                            ##
                            ##  ------ ANYTHING ELSE -------
             .              ##  Anything other char
             [^/"'\\]*      ##  Chars which doesn't start a comment, string
           )                ##    or escape
    """
    regex = re.compile(pattern, re.VERBOSE|re.MULTILINE|re.DOTALL)
    noncomments = [m.group(2) for m in regex.finditer(text) if m.group(2)]

    return "".join(noncomments)

def commentRemover(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return " " # note: a space and not an empty string
        else:
            return s
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, text)

#
# https://stackoverflow.com/questions/241327/python-snippet-to-remove-c-and-c-comments
#
def removeCommentsFromLine(text):
    return re.sub('//.*?(\r\n?|\n)|/\*.*?\*/', '', text, flags=re.S)



#https://gist.github.com/ChunMinChang/88bfa5842396c1fbbc5b
#Chun-Min Chang
#github
#With help from kossboss, on stackoverflow
#https://stackoverflow.com/questions/1140958/whats-a-quick-one-liner-to-remove-empty-lines-from-a-python-string
def removeCommentsFromFile(filename):

    filtered = []
    try:
      theFile = open(filename, "r")
    except:
      return "" 
    #with open(filename) as theFile:
    uncommentedFile = commentRemover(theFile.read())
    filtered = "".join([s for s in uncommentedFile.strip().splitlines(True) if s.strip()])
    return filtered


def countFileLines(filename):
      try:
        fileText = removeCommentsFromFile(filename)
        thelines = fileText.splitlines()
      except:
        return -1
      return(len(thelines))

def findSameName(name, includelist):

    head, tail = os.path.split(name)
    head, sep, tail =tail.partition(".")
    head = head + ".h"
    for includeName in includelist:
        include_head, include_tail = os.path.split(includeName)
        # print include_tail
        if include_tail == head:
            return head
    return None

def findCheaters(path, cheater_file_list):
    cheating = False
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.c') or file.endswith('.h') or file.endswith('.cpp') or file.endswith('.cc'):
                fullpath = os.path.join(root, file)
                fileText = removeCommentsFromFile(fullpath)
                includeCount = 0
                lines = fileText.splitlines()
                if len(lines) > 0:
                   cheating = True
                for line in lines:
                    line = line.strip()
                    line = line.replace(" ","")
                    if len(line) == 0:
                        continue
                    if "#include" in line:
                        includeCount = includeCount + 1
                    elif "#if" in line:
                        includeCount = includeCount + 1
                    else:
                        cheating = False

                
                if cheating:
                    fullpath = fullpath.replace(path,'',1)
                    #print ("Cheater:  "+ fullpath+"  "+file)
                    cheater_file_list.append(file)







def findfiles(path, extension):
    res = []
    for root, dirs, fnames in os.walk(path):
        for fname in fnames:
            tempname = fname.lower()
            if tempname.endswith(extension):
                name = os.path.join(root, fname)
                name = name.replace(path, '',1)
                if name not in res:
                    res.append(name)
                else:
                    continue
                    #print ("Duplicated name "+ name)
    return res


def findinclude(rootdir, database):
    quote = False
    for folder, dirs, files in os.walk(rootdir):
        for file in files:
            if file.endswith('.c') or file.endswith('.h') or file.endswith('.cpp') or file.endswith('.cc'):
                fullpath = os.path.join(folder, file)
                localfolder = folder.replace(rootdir,'')
                try:
                    f = open(fullpath,'r')
                except:
                    continue
                for line in f:
                        head = None
                        line = line.replace(" ","")
                        if "#include" in line:
                            if line.find('"'):
                                quotes = True
                            newline = removeCommentsFromLine(line)
                            newline = newline.translate(None, '<>#\"')
                            newline = newline.translate(None, ' ')
                            newline = newline.replace("include", '')
                            fullpath = fullpath.replace(rootdir, '',1)

                            if  ".h" in newline:
                                head, sep, tail = newline.partition(".h")
                            elif ".c" in newline:
                                head, sep, tail = newline.partition(".c")
                            elif ".cpp" in newline:
                                head, sep, tail = newline.partition(".cpp")
                            elif ".cc" in newline:
                                head, sep, tail = newline.partition(".cc")

                            if head == None:
                                # print "head is none"
                                name = newline
                            else:
                                name = head + sep


                            if name not in database[fullpath]:
                                if file.endswith('.h'):
                                    if name not in database[file]:
                                        database[file].append(name)

                                else:
                                    database[fullpath].append(name)
                                #if sep != ".h":
                                #    database[fullpath].append(name)
                                #else:
                                #    database[file].append(name)


def cheatingCounter(filename, path1, path2):

    myFile = path1+filename
    exists = os.path.isfile(myFile)
    if not exists:
        myFile = path2+filename
        exists = os.path.isfile(myFile)
    if not exists:
       # print "NO SUCH FILE "+myFile
        return -1
    # print "Searching "+myFile
    fileText = removeCommentsFromFile(myFile)
    includeCount = 0
    cheating = True

    lines = fileText.splitlines()
    for line in lines:
        if "#include" in line:
            includeCount=includeCount+1
        else:
            cheating=False

    if not cheating:
        includeCount = -1;
    return includeCount


def Intersection(lst1, lst2):
    return set(lst1).intersection(lst2)

def shefield(c_file_list, cheaters_list, mainpath):
    print ("filename,local,samename,cheaters,total,loc")
    for filename in c_file_list:
        sameNameIncludes = 0;
        cheaterIncludes = 0;
        localIncludes = 0;
        shortname = os.path.basename(filename)
        thename = findSameName(shortname, data[filename])
        included_cheaters = Intersection(data[filename], cheaters_list)
        if len(included_cheaters) > 0:
            for cheater in included_cheaters:
                cheaterIncludes = cheaterIncludes + len(data[cheater])


        localIncludes = len(data[filename])
        if thename != None:
            # if thename in data[filename]:
            #if thename=="plugin.h":
            #    print (data[thename])
            sameNameIncludes = len(data[thename])
            # print("SAME NAME", filename, sameNameIncludes)

        totalIncludes = localIncludes+sameNameIncludes+cheaterIncludes
        try:
           encoded_filename = filename.encode("ascii","ignore");
           decoded_filename = encoded_filename.decode()
        except:
           decoded_filename = "invalid_characters"

        fileLength =  countFileLines(mainpath+filename)


        print (decoded_filename+ ","+ str(localIncludes)\
              +","+str(sameNameIncludes)\
              +","+str(cheaterIncludes)\
              +","+str(totalIncludes) \
              +","+str(fileLength)  \
        )



data = defaultdict(list)
file_list = []
cheater_list = []
includePath = []
sourcePath = []

if len(sys.argv) == 2:
    sourcePath.append(sys.argv[1])
    includePath.append(sys.argv[1])
elif len(sys.argv) != 1:
    print ("One argument, the path OR")
    print ("this file should be treated like a script")
    print ("Create a list of include directories in the source file")
    print ("Look for build list here!")
    sys.exit()
else:
    ### BUILD LIST HERE
    sourcePath = ['/Users/michaeldorin/phd/complicated_paper/httpd']
    includePath = ['//Users/michaeldorin/phd/complicated_paper/httpd']

# Step 1, build a list of #includes
for path in includePath:
    findinclude(path, data)

for path in sourcePath:
    findinclude(path, data)

# Step 2, make a list of c and cpp files

for path in sourcePath:
    c_file_list = findfiles(path,'.c')
for path in sourcePath:
    c_file_list = c_file_list + findfiles(path, ".cpp")
for path in sourcePath:
    c_file_list = c_file_list + findfiles(path, ".cc")
for path in sourcePath:
    c_file_list = c_file_list + findfiles(path, ".cxx")

# Step 3, make a list of inclues

for path in includePath:
    h_file_list = findfiles(path,'.h')
for path in includePath:
    h_file_list = h_file_list + findfiles(path,'.hxx')

#print(h_file_list)
# Step 4, make a list of cheaters
for path in includePath:
    # print(path)
    findCheaters(path, cheater_list)

shefield(c_file_list, cheater_list, includePath[0])

