#!/bin/bash

if [[ $# -ne 2 ]]; then
   printf "Usage: $0 NAME DOC_REPO_URL\n"
   exit 1
fi

NAME=$1
DOC_REPO=$2

COMMIT_USER="StevenRob1958"
COMMIT_EMAIL="gobrecht1856@gmail.com"

COMMIT=$(git rev-parse --verify HEAD | cut -c1-7)
MAYBE_TAG=$(git describe --exact-match --tags $1 2> /dev/null | sed 's/tags\///')

if [[ -n $MAYBE_TAG ]] ; then
    printf "Found tag: $MAYBE_TAG\n"
    COMMITISH=$MAYBE_TAG
else
    # Prepend with a "g" so it's clear this is a git commit
    COMMITISH="g${COMMIT}"
fi

RELEASE=$COMMITISH
PUBLISH=1

DOC_DIR="doc"
BUILD_DIR="build"
DOC_BUILD_DIR="build/doc"
RELEASE_DIR_NAME="${NAME}_${RELEASE}_documentation"

GRAPHS_PATH=$DOC_BUILD_DIR/graphs
XML_PATH=$DOC_BUILD_DIR/xml
HTML_PATH=$DOC_BUILD_DIR/html

mkdir -p $BUILD_DIR

# Clean DOC_BUILD_DIR before we make it
rm -rf $DOC_BUILD_DIR

mkdir -p $DOC_BUILD_DIR
mkdir -p $DOC_BUILD_DIR/html
mkdir -p $DOC_BUILD_DIR/doc
mkdir -p $GRAPHS_PATH
mkdir -p $XML_PATH
mkdir -p $HTML_PATH

doxygen ${DOC_DIR}/Doxyfile_1
$(cd ${XML_PATH} && xsltproc combine.xslt index.xml > all.xml)

#create the graphs for doxygen

python ${DOC_DIR}/create_groups.py ${BUILD_DIR} ${DOC_BUILD_DIR}
doxygen ${DOC_DIR}/Doxyfile_2

if [[ -n $PUBLISH ]] ; then
    # FIXME: This could just reset the state of the repo if it exists
    # e.g. Check to see if surf-doc exists
    # If not, clone, if it does, do a pull
    $(cd $BUILD_DIR && git clone ${DOC_REPO})

    mkdir $BUILD_DIR/${DOC_REPO_DIR}/${RELEASE_DIR_NAME}
    cp -r ${DOC_BUILD_DIR}/html ${BUILD_DIR}/${DOC_REPO_DIR}/${RELEASE_DIR_NAME}/.
    python ${DOC_DIR}/update_index.py ${NAME} ${RELEASE} ${BUILD_DIR}/${DOC_REPO_DIR}/index.html

    cd ${BUILD_DIR}/${DOC_REPO_DIR}
    # Only commit/push if there's actually a tag
    if [[ -n "$MAYBE_TAG" ]] ; then
        git add .
        git commit -m "Automated documentation build for changeset ${COMMIT}."
        git push
    fi
fi
