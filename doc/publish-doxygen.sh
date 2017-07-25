REPO_PATH=git@github.com:StevenRob1958/surf.git
DIR_PATH="/users/Steven/SLAC/surf"
HTML_PATH=doc/html
GRAPHS_PATH=doc/graphs
XML_PATH=doc/xml
COMMIT_USER="StevenRob1958"
COMMIT_EMAIL="gobrecht1856@gmail.com"
CHANGESET=$(git rev-parse --verify HEAD)

doxygen doc/Doxyfile_1

cd ${XML_PATH}
xsltproc combine.xslt index.xml > all.xml
cd -

rm -rf ${GRAPHS_PATH}
mkdir -p ${GRAPHS_PATH}

python doc/create_groups.py ${DIR_PATH}

rm -rf ${HTML_PATH}
mkdir -p ${HTML_PATH}
git clone -b gh-pages "${REPO_PATH}" --single-branch ${HTML_PATH}
cd ${HTML_PATH}
git rm -rf .
cd -
echo " DOXY  Doxygen"
doxygen doc/Doxyfile_2
cd ${HTML_PATH}
git add .
git config user.name "${COMMIT_USER}"
git config user.email "${COMMIT_EMAIL}"
git commit -m "Automated documentation build for changeset ${CHANGESET}."
git push origin gh-pages
cd -