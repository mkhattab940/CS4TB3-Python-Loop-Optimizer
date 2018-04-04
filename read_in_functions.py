# Assume main function is at the end
# Assume tabs

# For now assume no function definitions inside loops

keywords = [ "and",       "del",       "from",      "not",       "while",
"as",        "elif",      "global",    "or",        "with",
"assert",    "else",      "if",        "pass",      "yield",
"break",     "except",    "import",    "print",
"class",     "exec",      "in",        "raise",
"continue",  "finally",   "is",        "return",
"def",       "for",       "lambda",    "try" ]

import sys
import re
import random

def genRandomVarName():
	varName = "Var_"
	for i in range(5):
		uppercase = random.randrange(2)
		letter = random.randrange(26)
		if uppercase:
			varName += chr(65 + letter)
		else:
			varName += chr(97 + letter)
	return varName + str(random.randrange(100))


def replace_params(func_def, call_params, indentation):
	fname = func_def["fname"]
	fparams = func_def["params"]
	fcode = func_def["fcode"]

	#TODO: replace literal values in call_params with variable names
	returnVar = genRandomVarName()
	fcode_inlined = []
	for line in fcode:
		i = 0
		line_inlined = indentation 
		while i < len(line):
			print(len(line))
			print(i)
			ident_found = re.search("[A-Za-z_]\w*", line[i:]) #match next identifier
			if ident_found:
				line_inlined += ident_found.string[:ident_found.start()] #Add chars not associated with identifiers
				
				ident = ident_found.string[ident_found.start():ident_found.end()]
				print(ident)
				if ident not in keywords: # Make sure we're not dealing with a keyword
					func_call_found = re.search("^\s*\(", ident_found.string[ident_found.end():])
					if not func_call_found: # This is a variable
						if ident in fparams: # This variable was passed in
							line_inlined += call_params[fparams.index(ident)]
						else:
							line_inlined += ident
					else:
						line_inlined += ident
				elif ident == "return":
					line_inlined += returnVar + "="
				else:
					line_inlined += ident

				i = i + ident_found.end()
			else:
				line_inlined += line[i:]
				break
		fcode_inlined.append(line_inlined)
	return fcode_inlined, returnVar


def parser(read_data, funcs = {}, inner_loop = 0, scope_indentation = ""):
	line_num = 0	#init counter
	#funcs = {}	#init list for storing functions

	opt_code = []

	while line_num < len(read_data):

		#opt_code.append(read_data[line_num])

		def_found = re.search("^(\t*)def\s+(\w+)\s*\((.*)\)\s*:\s*(.*)\n$", read_data[line_num])
		for_loop_found = re.search("^(\t*)for\s+.*:\s*(.*)\n$", read_data[line_num])
		while_loop_found = re.search("^(\t*)while\s+.*:\s*(.*)\n$", read_data[line_num])
		
		if def_found:
			#print("FOUND A DEF!!")
			indent = len(def_found.group(1))
			indentation = def_found.group(1)
			fname = def_found.group(2)
			params = def_found.group(3).replace(" ","").replace("\t","").split(",")
			
			#print(len(def_found.group(4)))
			opt_code.append(read_data[line_num][:-len(def_found.group(4))-1] + "\n")

			if len(def_found.group(4)) > 0 and not re.match("^\s*$", def_found.group(4)):
				body = [def_found.group(1) + def_found.group(4) + "\n"]
			else:
				body = []
				while line_num < len(read_data)-1:
					line_num += 1
					#print(read_data[line_num])
					if re.match("^\s*\n$", read_data[line_num]): #Skip empty lines 
						continue
					if re.match("^\s*#.*$", read_data[line_num]): #Skip comment lines
						continue	
					
					m2 = re.search("^(\t*).*$",read_data[line_num])
					indent2 = len(m2.group(1))

					if indent2 > indent: #All lines in the functions will be indented more than the function def line
						indentless = re.match("^(\t*)(.*\n)$",read_data[line_num])
						print("INDENTLESS: " + indentless.group(2))
						tabs = ""
						for i in range(indent2-indent-1):
							tabs += "\t"
						body.append(tabs + indentless.group(2))
					else: # We are outside the function (i.e. done)
						line_num -= 1 # Corrective
						break

			f_code = {"fname": fname, "params": params, "fcode": body}
			funcs[fname] = f_code

			#print(body)

			opt_body = parser(body, funcs, 0, indentation + "\t") # We want to parse body of function recursively
								# Funcs we have already found will be available to funcs defined inside current function
			opt_code = opt_code + opt_body
		elif for_loop_found or while_loop_found:

			#print("FOUND A LOOP!")
			#print(read_data[line_num])
			inner_loop = 0 # If we just found a loop, this can't the body of an inner loop

			if for_loop_found:
				indent = len(for_loop_found.group(1))
				indentation = for_loop_found.group(1)
				first_line = for_loop_found.group(2)
				opt_code.append(read_data[line_num][:-len(for_loop_found.group(2))-1] + "\n")
			else:
				indent = len(while_loop_found.group(1))
				indentation = while_loop_found.group(1)
				first_line = while_loop_found.group(2)
				opt_code.append(read_data[line_num][:-len(while_loop_found.group(2))-1] + "\n")

			# print (len(first_line))
			# print(first_line)
			if len(first_line) > 0 and not re.match("^\s*$", first_line):
				body = [indentation + first_line + "\n"]
			else:
				body = []
				while line_num < len(read_data)-1:
					line_num += 1
					#print(read_data[line_num])
					if re.match("^\s*\n$", read_data[line_num]): #Skip empty lines 
						continue
					if re.match("^\s*#.*$", read_data[line_num]): #Skip comment lines
						continue	
					
					m2 = re.search("^(\t*).*$",read_data[line_num])
					indent2 = len(m2.group(1))

					if indent2 > indent: #All lines in the functions will be indented more than the function def line
						indentless = re.match("^(\t*)(.*\n)$",read_data[line_num])
						tabs = ""
						for i in range(indent2-indent-1):
							tabs += "\t"
						body.append(tabs + indentless.group(2))
					else: # We are outside the function (i.e. done)
						line_num -= 1 # Corrective
						break

			#print(body)
			opt_body = parser(body, funcs, 1, indentation+"\t") # We want to parse body of function recursively
									# Set flag inner_loop to say 
			opt_code = opt_code + opt_body
		else:
			print("HERE:" + read_data[line_num])
			opt_code.append(read_data[line_num])
		line_num += 1
		
	print(opt_code)
	############################
	# CODE HERE TO CATCH LOOPS # (assumes no function definition inside loops. FIX LATER)
	############################
	tab_counter = 0 
	RHS = "0"
	if(inner_loop):
		print("INNER LOOP")
		#print (opt_code)
		#print (funcs)
		inlined_code = []
		for line in opt_code:
			i = 0
			line_rewrite = scope_indentation
			ident_match = re.search("^(\t*).*", line)
			indentation = ident_match.group(1)
			while i < len(line):
				print("hurr")
				ident_found = re.search("[A-Za-z_]\w*", line[i:]) #match next identifier
				if ident_found:
					line_rewrite += ident_found.string[:ident_found.start()] #Add chars not associated with identifiers
					
					ident = ident_found.string[ident_found.start():ident_found.end()]
					if ident not in keywords: # Make sure we're not dealing with a keyword
						func_call_found = re.search("^\s*\(", ident_found.string[ident_found.end():])
						if func_call_found: # This is a func call
							params_found = re.search("^(.*)\)", func_call_found.string[func_call_found.end():])
							if ident in funcs.keys(): # If this function is in funcs 
								params = params_found.group(1).replace(" ","").replace("\t","").split(",")
								inline_it, returnVar = replace_params(funcs[ident], params, scope_indentation + indentation)
								inlined_code = inlined_code + inline_it
								line_rewrite += returnVar
							else:
								line_rewrite += ident + "(" + params_found.group(1) + ")"
							i = i + params_found.end() + func_call_found.end() + ident_found.end()
						else:
							line_rewrite += ident
							i = i + ident_found.end()
					else:
						line_rewrite += ident
						i = i + ident_found.end()

				else:
					line_rewrite += line[i:]
					break
			inlined_code.append(line_rewrite)
		return inlined_code

	else:
		indented_opt_code = []
		print("NOT INNER LOOP")
		for line in opt_code:
			indented_opt_code.append(scope_indentation + line)
		return indented_opt_code
	

def main():
	filename = sys.argv[1]
	with open(filename, 'r') as f:
		read_data = f.readlines()

	#print(read_data)
	#print (len(read_data))


	opt_code = parser(read_data) 

	print(opt_code)
	new_file = open('generated.py', 'w')
	for item in opt_code:
		#print(opt_code)
		new_file.write(item)



if __name__ == "__main__":
    main()
