import os
import sys
import xml.etree.ElementTree as ET

#This script creates doxygen files for insantiating a dot graph for each module
#Prerequisites:
#Doxygen must have been run with GENERATE_XML set to YES
#There must exist a gaphs folder in the present directory
#
#Command Line ARguments: 1: startpath where library and documentation is housed

if len(sys.argv) < 3:
       print("Usage: python create_groups.py REPO_NAME XML_PATH\n")
       sys.exit(1)

repository_name = sys.argv[1]
xml_path = sys.argv[2]
startpath = os.path.dirname(xml_path)

modules = []		 #list of modules (strings)
pkgs = []			 #list of packages
module_subdirectories = {} #map of modules (strings) to their submodules (strings)
module_contents = {} #dictionary to map modules (String) to arrays of files (strings)
class_inheritances = {}    #dictionary to map class names (strings) to the classes they inherit from, returns id (string)
inheritances = {}	#dictionary to map inheritances between file names (strings)
package_inheritances = {} #dictionary to map package name (string) to the file and package names (Strings) that inherit from them
file_modules = {}    #dictionary to map file ids (Strings) to the module name (string) they are in

dir_ids = {} #map directory ids to directory 
file_ids = {} #map of file ids to corresponding file names
file_names = {} #map of file names to corresponding file ids
class_names = {} #map of class names to corresponding class ids
file_to_class = {} #map of file to the classes they contain
class_to_file = {} #map of classes to the files they are in
class_members = {} #map class compounddef ids to memberdef ids

try:
	tree = ET.parse("{}/xml/all.xml".format(xml_path)) #tree of doxygen xml
	root = tree.getroot()

except (IOError, ET.ParseError):
	print("Error: Failed to open or parse file all.xml\n")

else:
	print("Generating graphs...\n")

	def check_groups(root):
	#function to recursively check if a group contains an rtl folder
	#root is the string corresponding to the base folder that is being searched
	#iterates through the xml tree to find nodes that inherit from root
	#returns True if rtl subdirectory found, false otherwise

		contains_rtl = False

		#if it has an rtl folder
		if "rtl" or "hdl" in root:

			contains_rtl = True

		else:
			for inner_dir in module_subdirectories[root]:

				if check_groups(inner_dir):
					contains_rtl = True


		return contains_rtl


	#create group, file, and class mappings
	for compound in root.findall("compounddef"):
		#map directories to their ids and to their immediate subdirectories
		#look for dir tags
		if compound.attrib['kind'] == "dir":

			name = compound.find('compoundname').text

			dir_ids[name] = compound.get('id')
			
			module_subdirectories[name] = []
			module_contents[name] = []

			modules.append(name)

			#look for subfolders of current folder
			for inner_dir in compound.findall("innerdir"):

				module_subdirectories[name].append(inner_dir.text)

			#map files to their directory
			for inner_file in compound.findall("innerfile"):
				file_modules[inner_file.get("refid")] = name
				module_contents[name].append(os.path.join(name, inner_file.text))

		#map classes to their ids, classes to inherited classes, and memberdef ids to class ids
		#look for classes
		if compound.attrib['kind'] == "class":

			compound_id = compound.get("id")

			class_name = compound.find('compoundname').text
			class_names[class_name] = compound_id
			class_members[compound_id] = []
			class_inheritances[class_name] = []

			#look for inherited classes
			for basecompound in compound.findall("basecompoundref"):
				class_inheritances[class_name].append(basecompound.get("refid")) #basecompound is a class
			
			compound_section = compound.find("sectiondef")
			if compound_section is not None:
				#look for members inside of class, map their ids to class's id
				for member in compound_section.findall("memberdef"):
					member_name = member.find('name').text

					if "Pkg" in member_name:

						if member_name not in package_inheritances:
							package_inheritances[member_name] = []

						package_inheritances[member_name].append(class_name)

				class_members[compound_id].append(member.get('refid'))

		#look for classes
		#map file ids to file names, file ids to their class ids, class ids to the file ids they are in
		if compound.attrib['kind'] == "file":

			file_name = compound.find("compoundname").text
			file_ids[compound.get("id")] = file_name 
			file_names[file_name] = compound.get("id")
			file_to_class[file_name] = []

			for inner_class in compound.findall("innerclass"):

				class_id = inner_class.get("refid")
				file_to_class[file_name].append(inner_class.text)
				class_to_file[class_id] = compound.get("id")



	#create inheritance mappings
	for group in modules:
		#look through all files
		for file in module_contents[group]:
			inheritances[file] = []
			file_name = os.path.basename(file)

			#find inner classes in files
			for inner_class in file_to_class[file_name]:

				#take classes inner_class inherits from
				for inherit_class in class_inheritances[inner_class]:

					inherit_file_name = file_ids[class_to_file[inherit_class]]
					inherit_file = os.path.join(file_modules[class_to_file[inherit_class]], inherit_file_name)
					inheritances[file].append(inherit_file)


	def replace_groups(name, groups, new_groups):
		#function to find if a specific string is continaed in an array
		#and if so, remove it and append it to a new array
		#name is the string be checked for
		#modules is a list of strings
		#new_modules is the list strings are appended to
		if name in groups:
			new_groups.append(name)
			groups.remove(name)

		return new_groups

	#reorder module listing to be: 
		#base
		#general
		#sync
		#ram
		#fifo
		#axi
		#protocols 
		#ethernet 
		#devices


	new_modules =[]

	new_modules = replace_groups("base", modules, new_modules)
	new_modules = replace_groups("axi", modules, new_modules)
	new_modules = replace_groups("protocols", modules, new_modules)
	new_modules = replace_groups("ethernet", modules, new_modules)
	new_modules = replace_groups("devices", modules, new_modules)
	new_modules = replace_groups("base/general", modules, new_modules)
	new_modules = replace_groups("base/sync", modules, new_modules)
	new_modules = replace_groups("base/ram", modules, new_modules)
	new_modules = replace_groups("base/fifo", modules, new_modules)

	
	modules = new_modules + modules


	#create modules
	try:
		main_page = open("doc/mainpage.txt", 'w')

	except IOError:
		print("Error: File mainpage does not appear to exist.\n")

	else:	
		#open mainpage.txt
		main_page.write( "/** \n @brief Documentation file to be used in Doxygen mainpage. \n @author Steven McDonald\n @file\n */\n /**\n @mainpage {}\n Welcome to the {} repository documentation page\n".format(repository_name,repository_name))

		#make module groupings, create declarations
		for group in modules:

			group_title = os.path.basename(group)
			group_name = group.replace("/", "_")


			#if this group has an rtl folder, create a module
			if check_groups(group) and group_title != "rtl" and group_title != "hdl":

				#take this group's parent directory
				parent_group = os.path.dirname(group).replace("/","_")

				main_page.write("@defgroup {} {}\n".format(group_name, group_title)) 
				main_page.write("@brief The {} page\n".format(group_name))
				main_page.write("@ingroup {} \n".format(parent_group)) 



		main_page.write( "**/")
		main_page.close


	def in_group(group,file):
		#funciton to check if a file is in a group of one of its subdirectories
		#group is the name (string) of the group being checked
		#file is the name (file) of the file

		is_in = False;
		if file in module_contents[group]:
			is_in = True
		else:
			for sub_group in module_subdirectories[group]:
				if in_group(sub_group, file):
					is_in = True

		return is_in

	def in_pkg_group(group,file):
		#funciton to check if a file is in the same module as a package
		#group is the name (string) of the group being checked
		#file is the name (file) of the file

		is_in = False;

		for f in module_contents[group]:
			if file in f:
				is_in = True

		if not is_in:
			for sub_group in module_subdirectories[group]:
				if in_group(sub_group, file):
					is_in = True

		return is_in


	def find_sub_files(insert_line, group, sub_group, module_lines):
		#function to search files in a directory and create dot labels for each file
		#insert_line contains the existing dot labels the new ones are being appended to, a string
		#group is the parent group that files are being searched for inside of, a string 
		#sub_group is the the group being searched, a string
		#module lines is the lines from a file being written to, an array of strings

		#create labels
		for sub_file in module_contents[sub_group]:

			sub_file_name = os.path.basename(sub_file).replace(".vhd","")
			label_line = '{}[label="{}" URL="\\ref {}.vhd"];'.format(sub_file_name, sub_file_name, sub_file_name)
			
			if label_line not in module_lines  and "Pkg" not in sub_file:
				insert_line =  "{}{}\n".format(insert_line, label_line)

			#if its a package, write to packages page isntead
			elif "Pkg" in sub_file:
				if sub_file not in pkgs:
					pkgs.append(sub_file)
		
		#create inheritances
		for sub_file in module_contents[sub_group]:
			for inherit_file in inheritances[sub_file]:
				if in_group(group, inherit_file): 
					label_line = "{}->{}".format(os.path.basename(sub_file).replace(".vhd",""), os.path.basename(inherit_file).replace(".vhd",""))
					insert_line =  "{}{}\n".format(insert_line, label_line)

		return insert_line



	#Function to add files to groups
	def add_to_modules(group):
		#function to add files to groups
		#appends tags to all vhdl files in rtl folders. assigning them to groups
		#group is the root directory it is being run from

		#recurse through subdirectories
		for m in module_subdirectories[group]:

			add_to_modules(m)		

		#add files in group by writing doxygen tags
		for f in module_contents[group]:
			if ("rtl" in f or "hdl" in f) and (".vhd" in f or ".vhdl" in f):

				location = 0 #locatin of entity declaration
				already_added = False #check if line is already in file
				page_type = "" #entity or package
				parent = os.path.dirname(group).replace("/","_")

				if "Pkg" in f:
					#add to parent group of rtl folder
					insert = "--! @file \n --! @ingroup {}\n".format(parent)       
					page_type = "package"

				else:
					insert = "--! @see entity \n --! @ingroup {}\n".format(parent) 
					page_type = "entity"


				in_file = open(os.path.join(f), "r")
				contents = in_file.readlines()
				in_file.close()

				found = False
				for line in contents:
					if "--! @see entity" in line or "--! @ingroup" in line:
						already_added = True
						break
						
					if page_type in line or "ENTITY" in line and "--" not in line:
						found = True

					elif not found:
						location = location + 1
					
				#move package tags after package declaration
				if page_type == "package":
					location = location + 1

				if not already_added:
					contents.insert(location, insert)

					in_file = open(os.path.join(f), "w")
					contents = "".join(contents)
					in_file.write(contents)
					in_file.close()

	#write group tags to files
	for group_name in modules:
		add_to_modules(group_name)


	#create and write tags for group graphs
	for group in modules:

		if check_groups(group):


			graph_name = group.replace("/rtl","")   #rtl groups are combined with their parents
			graph_name = graph_name.replace("/hdl","")
			graph_name = graph_name.replace("/","_")

			try:
				module_graph = open("{}/doc/graphs/{}_graph.txt".format(startpath, graph_name),'w')
				module_graph.write("/** \n\page {} \n\ingroup {}".format(graph_name, graph_name))
				module_graph.write("\n\dot \ndigraph G{ \nnode [shape=record, fontname=Helvetica, fontsize=10];\nrankdir=\"RL\"; \n")
				module_graph.write("\n} \n\enddot \n */")
				module_graph.close()

				module_graph = open("{}/doc/graphs/{}_graph.txt".format(startpath, graph_name),'r')
				module_lines = module_graph.readlines()
				module_graph.close()
			except IOError:
				print("Error: Graphs directory does not appear to exist.\n")

			else:


				location = len(module_lines)-4 #insert before end of digraph


				#iterate over groups in the module
				for sub_group in module_subdirectories[group]:

					insert_line = ""

					sub_group_name = sub_group.replace("/rtl","")
					sub_group_name = sub_group_name.replace("/hdl","")
					sub_group_name = sub_group_name.replace("/","_")

					#create a subgraph if subgraph not for rtl group
					if "rtl" not in sub_group and "hdl" not in sub_group:
						insert_line = "{}subgraph cluster_{} {}\n".format(insert_line, sub_group_name, "{")
					else:
						#list sub files
						insert_line = find_sub_files(insert_line, group, sub_group, module_lines)


					#list sub directories inside of subfolder
					for base_group in module_subdirectories[sub_group]:

						base_group_name = base_group.replace("/rtl", "")
						base_group_name = base_group_name.replace("/hdl", "")
						base_group_name = base_group_name.replace("/","_")

						label_line = '{}[label="{}" URL="\\ref {}"];'.format(base_group_name, os.path.basename(base_group.replace("/rtl", "")), base_group_name)
						
						if label_line not in module_lines:
							insert_line = "{}{}\n".format(insert_line, label_line)

						#add files from rtl folder
						if "rtl" in base_group or "hdl" in base_group:
							#if a base group is an rtl folder, list files inside of it
							insert_line = find_sub_files(insert_line, group, base_group, module_lines)

					insert_line = "{}\ncolor=blue;\nlabel={}; \n{}\n".format(insert_line, sub_group_name, "}")
					module_lines.insert(location, insert_line)

				#if looking in an rtl group
				if "rtl" in group or "hdl" in group:

					insert_line = ""
					insert_line = find_sub_files(insert_line, group, group, module_lines)

					module_lines.insert(location, insert_line)

				module_graph = open("{}/doc/graphs/{}_graph.txt".format(startpath, graph_name),'w')
				new_lines = "".join(module_lines)
				module_graph.write(new_lines)							
				module_graph.close()


	#create package graphs
	for pkg in package_inheritances:

		try:
			pkg_graph = open("{}/doc/graphs/{}_graph.txt".format(startpath, pkg),'w')
			pkg_graph.write("/** \n\\file {}.vhd \n\details\n \n \n".format(pkg))
			pkg_graph.write("\dot \ndigraph T{ \n A [style=invis] \nB [style=invis] \n} \n \enddot\n")
			pkg_graph.write("\dot \ndigraph G{ \nnode [shape=record, fontname=Helvetica, fontsize=10];\n")
			pkg_graph.write('label={}; \n{}[label="{}" URL="\\ref {}.vhd"];\n'.format(pkg, pkg, pkg, pkg))
		except IOError:
			print("Graphs directory does not appear to exist.\n")

		else:
			#only create inheritance if inherited file exists
			if "{}.vhd".format(pkg) in file_names:
				pkg_id = file_names["{}.vhd".format(pkg)]
				group = file_modules[pkg_id]

				counter = 0 #track how many nodes are on a line
				level = "{rank=same" #write lank to keep rankings
				#loop through files that inherited from pkg
				for inherited in package_inheritances[pkg]:

					#check if inherited is in the same group as pkg
					if in_pkg_group(group, inherited):
						if counter > 4:
							level = " {}{} -> {}rank=same ".format(level, "}","{")
							counter = 0
						else:
							level = "{} {}".format(level, inherited)

						pkg_graph.write('{}[label="{}" URL="\\ref {}.vhd"];\n'.format(inherited, inherited, inherited))
						pkg_graph.write("{}->{};\n".format(inherited, pkg))
						counter = counter + 1

				#strip trialing "->: from level
				if level.endswith("e"):
					level = level[:-14]
				pkg_graph.write("{}{} [style=invis]\n".format(level,"}")) #write rankings
			pkg_graph.write("}\n")  #close digraph
			pkg_graph.write("\enddot \n") #end grap description
			group = group.replace("/rtl","")
			group = group.replace("/hdl","")
			group = group.replace("/","_")
			pkg_graph.write("\page {} \n\ingroup {} \n\copydetails {}.vhd \n */".format(group, group, pkg))
			pkg_graph.close()




