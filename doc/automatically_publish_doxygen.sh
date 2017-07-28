#! /bin/bash
#! /bin/sh

#This is a script to take a github release for a vhdl project, create a new documentation 
#folder for it, and generate documentation for it using Doxygen
#Arguments: the project repository, the documentation repository, the release, and the project name
#pass in repo path= $1
#pass in documentation path= $2
#pass in release = $3
#pass in project name = $4

#make path to directory


REPO_PATH=$1
DOC_PATH=$2
RELEASE=$3
NAME=$4
COMMIT_USER="StevenRob1958"
COMMIT_EMAIL="gobrecht1856@gmail.com"
CHANGESET=$(git rev-parse --verify HEAD)

echo ${REPO_PATH}
echo ${DOC_PATH}
echo ${RELEASE}
echo ${NAME}


if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then

	echo "One or more variables not set"
	
else
	#create new folders for release
	rm -rf ~/"${NAME}"-doc
	mkdir ~/"${NAME}"-doc/

	rm -rf ~/"${NAME}"-doc/"${NAME}"_"${RELEASE}"
	mkdir -p ~/"${NAME}"-doc/"${NAME}"_"${RELEASE}"

	rm -rf ~/"${NAME}"-doc/"${NAME}"_"${RELEASE}"_documentation
	mkdir -p ~/"${NAME}"-doc/"${NAME}"_"${RELEASE}"_documentation

	#create html
	HTML_PATH=~/"${NAME}"-doc/"${NAME}"_"${RELEASE}"_documentation/html
	rm -rf ${HTML_PATH}
	mkdir -p ${HTML_PATH}

	#clone repository to local machine
	cd ~/"${NAME}"-doc/
	git commit -m "Staging for pull"
	git init
	git pull ${DOC_PATH}

	git clone ${REPO_PATH} ~/"${NAME}"-doc/"${NAME}"_"${RELEASE}"
	cd ~/"${NAME}"-doc/"${NAME}"_"${RELEASE}"

	#create doc folder
	rm -rf ~/"${NAME}"-doc/"${NAME}"_"${RELEASE}"/doc/
	mkdir -p ~/"${NAME}"-doc/"${NAME}"_"${RELEASE}"/doc/
	cp -a ~/"${NAME}"-doc/doc/. ~/"${NAME}"-doc/"${NAME}"_"${RELEASE}"/doc/


	GRAPHS_PATH=~/"${NAME}"-doc/"${NAME}"_"${RELEASE}"/doc/graphs
	XML_PATH=~/"${NAME}"-doc/"${NAME}"_"${RELEASE}"/doc/xml
	
	#use doxygen to generate xml
	doxygen doc/Doxyfile_1

	cd ${XML_PATH}
	xsltproc combine.xslt index.xml > all.xml
	cd -

	#create the graphs for doxygen
	rm -rf ${GRAPHS_PATH}
	mkdir -p ${GRAPHS_PATH} 

	python doc/create_groups.py ~/"${NAME}"-doc/"${NAME}"_"${RELEASE}" ~/"${NAME}"-doc/"${NAME}"_"${RELEASE}/doc"


	#create html
	mkdir -p html
	
	#switch to documentation folder
	cd ~/"${NAME}"-doc/"${NAME}"_"${RELEASE}"_documentation



	#go back to library
	cd ~/"${NAME}"-doc/"${NAME}"_"${RELEASE}"

	#generate documentation
	echo " DOXY  Doxygen"
	doxygen doc/Doxyfile_2

	#move documentation to docs folder
	cd ..
	cp -rf ~/"${NAME}"-doc/"${NAME}"_"${RELEASE}"/html/. "${HTML_PATH}"

	rm -rf ~/"${NAME}"-doc/"${NAME}"_"${RELEASE}"

	#add release link to index for documentation
	python ~/"${NAME}"-doc/doc/update_index.py "${NAME}" "${RELEASE}"

	#push to github
	git add .
	git commit -m "Automated documentation build for changeset ${CHANGESET}."
	git remote add origin ${DOC_PATH}
	git push origin master

	
fi