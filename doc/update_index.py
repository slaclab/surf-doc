import os
import sys

#Script to update hte index page for a repositories documentation
#For each new release, it adds the link to the most recent documentation to index.html

name = sys.argv[1]
release = sys.argv[2]
index = open("index.html".format(name),'r')
index_lines = index.readlines()
index.close()

insert_line = "<a href='{}_{}_documentation/html/index.html'>Release {}</a></br>".format(name, release, release)

if insert_line not in index_lines:
	index_lines.insert(7, insert_line)



index = open("index.html".format(name),'w')
new_lines = "".join(index_lines)
index.write(new_lines)							
index.close()