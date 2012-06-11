#!/usr/bin/env python
# Parse KIDS files (.KID)
#
#
#---------------------------------------------------------------------------
# Copyright 2011 The Open Source Electronic Health Record Agent
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#---------------------------------------------------------------------------
import sys
import os

def unpack(kid, routineDir):
    # method variables
    routineLines = 0
    routineName = ""
    routine = None
    output = sys.stdout

    with open(kid, 'r') as f:
        for line in f:
            # identifier is the line preceding the data (RTN,BLD,KRN,RPC,etc) that provides processing information
            # actual data is always on the next line
            # Handle Routines Block
            if line.startswith('''"RTN"'''):
                if '''"RTN")''' in line:
                    # Next line contains the number of routines in the build
                    line = f.next()
                    numberOfRoutines = line
                    output.write('Number of routines:  ' + numberOfRoutines)
                    line = f.next()
                    #output.write("line before while:  " + line)
                # Loop over RTN section
                while line.startswith('''"RTN",'''):
                    identifier = line.split(',')
                    if len(identifier) == 2:
                        # Beginning of Routine Header
                        # "RTN","RoutineName")
                        # Data (line+1): Unknown^Unknown^ChecksumAfter^ChecksumBefore
                        line = f.next()
                        routineHeader = line.strip()
                        routineName = identifier[1].strip()
                        routineName = routineName.strip(')\"')
                        output.write('Routine Header:  ' + routineHeader + "\n")
                        output.write('Routine Name:  ' + routineName + "\n")
                        if routine:
                            routine.close()
                            routine = None
                        routine = open(routineDir + "/" + routineName + ".m", 'w')
                        if identifier[1].strip(' \n\")') != routineName:
                            output.write('identifier:  ' + identifier[1] + "\n")
                            output.write('Number of lines in routine: ' + str(routineLines) + "\n")
                            routineLines = 0
                    if len(identifier) == 4:
                        routineLines += 1
                        # Actual Routine Data
                        # "RTN","RoutineName",LineNumber,0)
                        # Data (line+1): Line of M code
                        line = f.next()
                        code = line
                        routine.write(code)
                    line=f.next()

def checksum(routine):
    checksum = 0
    lineNumber = 0
    characterPosition = 0
    savedcharater=""
    with open(routine, 'r') as f:
        for line in f:
            lineNumber += 1
            # ignore the second line
            if lineNumber == 2:
                continue
            lengthOfLine = mFind(line," ")
            if mExtract(line,lengthOfLine) != ";":
                lengthOfLine = line.__len__()-1
            elif mExtract(line, 1+lengthOfLine) == ";":
                lengthOfLine = line.__len__()-1
            else:
                lengthOfLine = lengthOfLine - 1
            for character in xrange(lengthOfLine):
                characterPosition +=1
                # normal code
                temp = lineNumber+characterPosition
                checksum += ord(mExtract(line,character))*temp
            characterPosition = 0
            
    sys.stdout.write("Checksum is: "+str(checksum)+"\n")


def splitDataDictionary(DataDictionary,FileNumber):
    #
    # File Subscripts
    #
    # Unable to find definition of ^DD(filenumber,0), current assumption is that it is the same as files
    # ^DD(filenumber,0)
    #   Piece 1 = file name
    #   Piece 2 = file number witcharacteristics code
    #   Piece 3 = most recently assigned internal entry number (highest field number in file)
    #   Piece 4 = current total number of entries
    #
    #^DD(filenumber,0,"ACT")                                            Post-Action
    #^DD(filenumber,0,"DDA")                                            Data Dictionary Audit
    #^DD(filenumber,0,"DIC")                                            Special Lookup
    #^DD(filenumber,0,"ID",field)                                       Field identifiers
    #^DD(filenumber,0,"ID","WRITE")                                     Write identifiers
    #^DD(filenumber,0,"IX",cross-reference name,(sub)filenumber,field)  Cross-references
    #^DD(filenumber,0,"SCR")                                            File Screen
    #^DD(filenumber,0,"VR")                                             Version Number
    #^DD(filenumber,0,"VRPK")                                           Distribution Package
    #^DD(filenumber,0,"VRRV")                                           Package Revision Data
    ##################################################################################################
    # Field Subscripts
    #
    #^DD(filenumber,fieldnumber,0)                                      Field Definition 0 node
    #   Piece 1 = Field label
    #   Piece 2 = Field attributes (can have multiple) - definitions Page 479 fm22_0pm.pdf
    #   Piece 3 = Pointer/Set of Codes flag
    #   Piece 4 = Storage location
    #   Piece 5 = Field validation
    #
    #^DD(filenumber,fieldnumber,.1)                                     Contains the full-length title of the field.
    #
    #^DD(filenumber,fieldnumber,1)                                      Contains, at lower subscript levels, executable
    #                                                                   M code to SET and KILL cross-references based
    #                                                                   on the value of the field (in the variable X).
    #
    #^DD(filenumber,fieldnumber,2)                                      Contains the OUTPUT transform: M code to
    #                                                                   display the field value in a format that differs
    #                                                                   from the format in which it is stored. (See the
    #                                                                   "Advanced File Definition" chapter in this manual.)
    #
    #^DD(filenumber,fieldnumber,3)                                      Contains the help prompt message that is displayed
    #                                                                   when the user types a question mark.
    #
    #^DD(filenumber,fieldnumber,4)                                      Contains M code that will be executed when the user
    #                                                                   types one or two question marks. (Other help messages
    #                                                                   are also displayed.)
    #
    #^DD(filenumber,fieldnumber,5)                                      Contains, at lower subscript levels, pointers to
    #                                                                   trigger cross-references to this field.
    #
    #^DD(filenumber,fieldnumber,7.5)                                    Is valid only on .01 fields. It contains M code that
    #                                                                   will be executed to check the user input (in the
    #                                                                   variable X). This code is executed at the start of
    #                                                                   the ^DIC routine before the lookup on X has begun.
    #                                                                   If X is KILLed, the lookup will terminate. Special
    #                                                                   lookup programs naturally have a way to look at X.
    #
    #^DD(filenumber,fieldnumber,8)                                      Read access for the field.
    #
    #^DD(filenumber,fieldnumber,8.5)                                    Delete access for the field.
    #
    #^DD(filenumber,fieldnumber,9)                                      Write access for the field.
    #
    #^DD(filenumber,fieldnumber,9.01)                                   The fields used if the field is a computed field.
    #
    #^DD(filenumber,fieldnumber,9.1)                                    The expression entered by the user to create the
    #                                                                   computed field.
    #
    #^DD(filenumber,fieldnumber,9.2 to 9.9)                             The overflow executable M code that may be part
    #                                                                   of the specification of a field definition, INPUT
    #                                                                   transform, or cross-reference.
    #
    #^DD(filenumber,fieldnumber,10)                                     Contains the source of the data.
    #
    #^DD(filenumber,fieldnumber,11)                                     Contains the destination of the data.
    #
    #^DD(filenumber,fieldnumber,12)                                     Contains the explanation of the screen on node 12.1.
    #
    #^DD(filenumber,fieldnumber,12.1)                                   Contains the code which sets DIC("S") if a screen has
    #                                                                   been written for a pointer or a set of codes.
    #
    #^DD(filenumber,fieldnumber,20)                                     A multiple that lists the fields that belong to certain groups.
    #
    #^DD(filenumber,fieldnumber,21)                                     A word-processing field that holds the field description.

    DDfile = open(FileNumber + ".DD", 'w')
    with open(DataDictionary, 'r') as DD:
        for line in DD:
            sys.stdout.write(DataDictionary + "\r")
            sys.stdout.write(FileNumber + "\r")
            # find the file number in the DD
            if line.startswith('^DD(' + FileNumber + ','):
                sys.stdout.write("line")
                DDfile.write(line)
    DDfile.close()

################################
# Utility Functions
# TODO: put this in an Mfunctions class
################################

def mExtract(string,position):
    chars = list(string)
    return chars[--position]

def mFind(string,substring):
    f = string.index(substring)
    return f +1

def main():
    #unpack(sys.argv[1], sys.argv[2])
    #checksum(sys.argv[1])
    splitDataDictionary(sys.argv[1],sys.argv[2])
         
if __name__ == '__main__':
    main()
