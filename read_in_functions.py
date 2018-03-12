# Assume main function is at the end
# Assume tabs

# For now assume no function definitions inside loops

import sys
import re


def parser(read_data, funcs):
	line_num = 0	#init counter
	#funcs = {}	#init list for storing functions

	while line_num < len(read_data):
		m = re.search("^(\t*)def\s+(\w+)\s*\((.*)\)\s*:\s*$", read_data[line_num])
		
		if m:
			indent = len(m.group(1))
			fname = m.group(2)
			params = m.group(3).replace(" ","").replace("\t","").split(",")
			print(indent)
			print (fname)
			print (params)

			body = []

			while True:
				line_num += 1
				#print(read_data[line_num])
				if re.match("^\s*\n$", read_data[line_num]): #Skip empty lines 
					continue
				if re.match("^\s*#.*$", read_data[line_num]): #Skip comment lines
					continue	
				
				m2 = re.search("^(\t*).*$",read_data[line_num])
				indent2 = len(m2.group(1))

				if indent2 > indent: #All lines in the functions will be indented more than the function def line
					body.append(read_data[line_num])
				else: # We are outside the function (i.e. done)
					line_num -= 1 # Corrective
					break

			f_code = {"fname": fname, "params": params, "fcode": body}
			funcs[fname] = f_code

			parser(body, funcs) # We want to parse body of function recursively
								# Funcs we have already found will be available to funcs defined inside current function



		############################
		# CODE HERE TO CATCH LOOPS # (assumes no function definition inside loops. FIX LATER)
		############################

		line_num += 1

	print(funcs)


def main():
	filename = sys.argv[1]
	with open(filename, 'r') as f:
		read_data = f.readlines()

	print(read_data)
	print (len(read_data))

	parser(read_data, {}) 


if __name__ == "__main__":
    main()

