#file to replace a line in a text file
#It takes three arguments:
	# 1. Path to the file
	# 2. Line to be removed
	# #. Line to be inserted

import sys

file_path = sys.argv[1]
before_line = sys.argv[2]
after_line = sys.argv[3]

file = open(file_path,'r')
file_lines = file.readlines()
file.close()

file = open(file_path,'w')

for line in file_lines:
	if before_line not in line:
		file.write(line)
	else:
		file.write(after_line)
		file.write('\n')
file.close()






