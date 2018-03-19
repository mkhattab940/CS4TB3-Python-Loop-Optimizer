# Assume main function is at the end
# Assume tabs

# For now assume no function definitions inside loops

import sys
import re


def parser(read_data, funcs, inner_loop):
	line_num = 0	#init counter
	#funcs = {}	#init list for storing functions

	opt_code = []

	while line_num < len(read_data):
		def_found = re.search("^(\t*)def\s+(\w+)\s*\((.*)\)\s*:\s*$", read_data[line_num])
		for_loop_found = re.search("^(\t*)for\s+.*:\s*$", read_data[line_num])
		while_loop_found = re.search("^(\t*)while\s+.*:\s*$", read_data[line_num])
		
		if def_found:
			indent = len(def_found.group(1))
			fname = def_found.group(2)
			params = def_found.group(3).replace(" ","").replace("\t","").split(",")
			#print(indent)
			#print (fname)
			#print (params)

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

			opt_body = parser(body, funcs, 0) # We want to parse body of function recursively
								# Funcs we have already found will be available to funcs defined inside current function
		elif for_loop_found or while_loop_found:
			inner_loop = 0 # If we just found a loop, this can't the body of an inner loop

			if for_loop_found:
				indent = len(for_loop_found.group(1))
			else:
				indent = len(while_loop_found.group(1))

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

			opt_body = parser(body, funcs, 1) # We want to parse body of function recursively
									# Set flag inner_loop to say 

		line_num += 1
		opt_code = opt_code + opt_body
	
		############################
		# CODE HERE TO CATCH LOOPS # (assumes no function definition inside loops. FIX LATER)
		############################
		
	if inner_loop:
		tab_counter = 0 
		RHS = "0"

		#check for for
		for string in read_data:
			if (re.search("^(\t*)for*",string)):
				#counts number of tabs
				m =string.count("\t")
				#print "M: ",m
				#print "Found for"
				index = read_data.index(string)
				#print "Index: ",read_data.index(string)

				#try to match function inside loop
				i = index+1
				for function in read_data[i:len(read_data)]:

					#print "funciton ",function
					#check for number of tabs
					m_new =function.count("\t")
					#print "M_new ",m_new

					#not a function if tabs are less than or equal to line before
					if (m_new <= m):
						print "inner loop not"
						break

					#otherwise it is a function so replace it
					else:
						#check if string matches in our dictionary
						temp = function.split("(")
						func_name = temp[0].split()
						#print "NEW NAME" ,func_name
						#look in dictionary for key == num_function
						for name,values in funcs.items():
							#print "NAME in FCODE:", name
							#match key to name 
							if (name == func_name[0]):
								print "Matches"
								#remove function call
								read_data.pop(i)
								#if function is found in dictionary put body in list
								read_data[i:i] = values['fcode']
								print "READ DATA", read_data 
							else:
								print "No match"



			#check for while
			elif (re.search("^(\t*)while*",string)):
				#counts number of tabs
				m =string.count("\t")
				#print "M: ",m
				#print "Found while"
				#print "Index: ",read_data.index(string)
				#print "M: ",m
				#print "Found for"
				index = read_data.index(string)
				#print "Index: ",read_data.index(string)

				#try to match function inside loop
				i = index+1
				for function in read_data[i:len(read_data)]:

					#print "funciton ",function
					#check for number of tabs
					m_new =function.count("\t")
					#print "M_new ",m_new

					#not a function if tabs are less than or equal to line before
					if (m_new <= m):
						print "inner loop not"
						break

					#otherwise it is a function so replace it
					else:
						#check if string matches in our dictionary
						temp = function.split("(")
						func_name = temp[0].split()
						print ("func_name:",func_name)
						if ("=" in func_name):
							RHS = "1"
							print ("there is an equal")
						#print "NEW NAME" ,func_name
						#look in dictionary for key == num_function
						for name,values in funcs.items():
							#print "NAME in FCODE:", name
							#match key to name 
							if (name == func_name[0]):
								if(RHS == "0"):
									print "Matches"
									#remove function call
									#do more work to figure out right i all the time
									read_data.pop(i)
									#if function is found in dictionary put body in list
									read_data[i:i] = values['fcode']
									print "READ DATA", read_data 
							elif (name == func_name[2]):
								if(RHS == "1"):
									print "RHS Matches"
									#remove function call
									#do more work to figure out right i all the time
									#print read_data
									read_data.pop(i)
									#print(values['fcode'][2])
									tabs =values['fcode'][-1].count("\t")
									temp_value = values['fcode'][-1].split('return')
									return_value = temp_value[1]
									#print(return_value)
									new_value = "x ="+ (return_value)
									#print(new_value)
									#print(tabs)
									tabscount = tabs * "\t"
									values['fcode'][-1] = tabscount + new_value
									#if function is found in dictionary put body in list
									read_data[i:i] = values['fcode']
									print "READ DATA", read_data 
							else:
								print "No match"

		
	return opt_code
	

def main():
	filename = sys.argv[1]
	with open(filename, 'r') as f:
		read_data = f.readlines()

	print(read_data)
	print (len(read_data))


	opt_code = parser(read_data, {}, 0) 

	#print(funcs)
	new_file = open('generated.py', 'w')
	for item in opt_code:
		new_file.write(item)



if __name__ == "__main__":
    main()
