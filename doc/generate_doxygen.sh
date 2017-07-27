#! /bin/bash
#! /bin/sh

#This is a script to run Doxygen on surf (Can be modified to other projects) 
#Should be run from the surf directory
#It takes three arguments:
#	The surf version-number (default to 1)
#	Output Directory (default to surf/doc/surf-versionNumber/)
#	Input directory (default to surf)
# Requires two doxyfiles; one for creating xml and one for creating html

VERSION=${1:-1}
OUTPUT=${2:-doc}
OUTPUT="$OUTPUT/$VERSION"
INPUT=${3:- }
NEW_IN='INPUT                  =' ${INPUT}
NEW_OUT='OUTPUT_DIRECTORY       ='${OUTPUT} 
NEW_PN='PROJECT_NUMBER         ='${VERSION}

python doc/replace_line.py doc/Doxyfile_1 'OUTPUT_DIRECTORY       =' "$NEW_OUT"
python doc/replace_line.py doc/Doxyfile_1 'INPUT                  =' "$NEW_IN"
python doc/replace_line.py doc/Doxyfile_1 'PROJECT_NUMBER         =' "$NEW_PN" 

python doc/replace_line.py doc/Doxyfile_2 'OUTPUT_DIRECTORY       =' "$NEW_OUT"
python doc/replace_line.py doc/Doxyfile_2 'INPUT                  =' "$NEW_IN"
python doc/replace_line.py doc/Doxyfile_2 'PROJECT_NUMBER         =' "$NEW_PN"  


mkdir -p ${OUTPUT}

doxygen doc/Doxyfile_1

cd "${OUTPUT}/xml/"
xsltproc combine.xslt index.xml > all.xml
cd -

rm -rf doc/graphs
mkdir -p doc/graphs

python doc/create_groups.py './' ${OUTPUT}


rm -rf ${OUTPUT}/html
mkdir -p ${OUTPUT}/html

echo " DOXY  Doxygen"
doxygen doc/Doxyfile_2

echo "Finished"