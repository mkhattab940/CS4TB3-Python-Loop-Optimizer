# Assume main function is at the end
# Assume tabs

import sys
import re
import random

# For now assume no function definitions inside loops

# TOKENS
IDENTITY = 0; VARIABLE = 1; FCALL = 2; STRLIT = 3; NUMLIT = 4; EOL = 5; KEYWORD = 6; 
LP = 7; RP = 8; ASSIGN = 9; OTHER = 10; COMMA = 11; COLON = 12; LB = 13; RB = 14;


keywords = [ "and",       "del",       "from",      "not",       "while",
"as",        "elif",      "global",    "or",        "with",
"assert",    "else",      "if",        "pass",      "yield",
"break",     "except",    "import",    "#print",		"True",		 "False",
"class",     "exec",      "in",        "raise",
"continue",  "finally",   "is",        "return",
"def",       "for",       "lambda",    "try" ]

# GLOBAL VARIABLES
genvarcnt = -1	#Used in variable name generation

line2lex = ""	# Variables used in lexical analysis
lnidx = 0
token = 0
text = ""

s_line2lex = ""	#Variables for stashing lex() state
s_lnidx = 0
s_token = 0
s_text = ""

def genRandomVarName():
	global genvarcnt
	varName = "Var_"
	for i in range(5):
		uppercase = random.randrange(2)
		letter = random.randrange(26)
		if uppercase:
			varName += chr(65 + letter)
		else:
			varName += chr(97 + letter)
	genvarcnt += 1
	return varName + '_' + str(genvarcnt)

##############################
# LEXICAL ANALYZER FUNCTIONS #
##############################

# These functions allow us to stash lexical analysis progress so we can use lex() for in-lining while in the middle
# of using to find functions to in-line
def stashLex():
	global s_line2lex
	global s_lnidx
	global s_token
	global s_text
	s_line2lex = line2lex
	s_lnidx = lnidx
	s_token = token
	s_text = text

def restoreLex():
	global line2lex
	global lnidx
	global token
	global text
	line2lex = s_line2lex
	lnidx = s_lnidx
	token = s_token
	text = s_text


# get the input str set up for lexical analysis
def loadLex(string):
	global line2lex
	global lnidx

	line2lex = string
	lnidx = 0

# get the next token
def lex():
	global lnidx
	global token
	global text

	if lnidx >= len(line2lex):
		token, text = EOL, "\n"
		return

	eol_found = re.search("^\s*(\n)", line2lex[lnidx:])
	lp_found = re.search("^\s*(\()", line2lex[lnidx:])
	rp_found = re.search("^\s*(\))", line2lex[lnidx:])
	lb_found = re.search("^\s*(\[)", line2lex[lnidx:])
	rb_found = re.search("^\s*(\])", line2lex[lnidx:])
	comma_found = re.search("^\s*(,)", line2lex[lnidx:])
	colon_found = re.search("^\s*(:)", line2lex[lnidx:])

	if lnidx > 0:
		assign_found = re.search("^\s*(=)", line2lex[lnidx:])
	else:
		assign_found = False
	ident_found = re.search("^\s*([A-Za-z_][\w]*)", line2lex[lnidx:]) #match next identifier
	
	strlit_dq_found = re.search("^\s*(\".*\")", line2lex[lnidx:])
	strlit_sq_found = re.search("^\s*('.*')", line2lex[lnidx:])
	
	numlit_found = re.search("^\s*(-?[0-9]+)", line2lex[lnidx:])
	#numlit_found = re.search("^\s*(-?[0-9]*\.?[0-9]*[eE]?-?[0-9]*[jJ]?)", line2lex[lnidx:]) #always matches
																					#check if contains digit later
	if eol_found:
		#print("HEYHEYE")
		lnidx += eol_found.end()
		token, text = EOL, "\n"
	
	elif lp_found:
		lnidx += lp_found.end()
		token, text = LP, "("
	elif rp_found:
		lnidx += rp_found.end()
		token, text = RP, ")"
	elif lb_found:
		lnidx += lb_found.end()
		token, text = LB, "["
	elif rb_found:
		lnidx += rb_found.end()
		token, text = RB, "]"
	elif comma_found:
		lnidx += comma_found.end()
		token, text = COMMA, ","
	elif colon_found:
		lnidx += colon_found.end()
		token, text = COLON, ":"
	elif assign_found:
		if line2lex[lnidx+assign_found.start()-1] not in "<>=!+\-*/%&|\^":
			if line2lex[lnidx+assign_found.end()] != '=':
				#print("ASSIGN!")
				token, text = ASSIGN, "="
			else:
				token, text = OTHER, "="
		else:
			token, text = OTHER, "="
		lnidx += assign_found.end()
	elif ident_found:
		lnidx += ident_found.end()
		if ident_found.group(1) in keywords:
			token, text = KEYWORD, ident_found.group(1)
		else:
			token, text = IDENTITY, ident_found.group(1)
	elif strlit_dq_found:
		lnidx += strlit_dq_found.end()
		token, text = STRLIT, strlit_dq_found.group(1)
	elif strlit_sq_found:
		lnidx += strlit_sq_found.end()
		token, text = STRLIT, strlit_sq_found.group(1)
	elif numlit_found:
		lnidx += numlit_found.end()
		token, text = NUMLIT, numlit_found.group(1)
	else:
		#print(len(line2lex))
		#print(lnidx)
		lnidx += 1
		token, text = OTHER, line2lex[lnidx-1]

######################
# SYNTACTIC ANALYSIS #
######################

# target_list     ::=  target ("," target)* [","]
def Target_List():
	ids = Target()
	while True:
		if token == COMMA:
			lex()
			ids +=  Target()
		else:
			break
	return ids

# target          ::=  identifier
#                      | "(" target_list ")"
#                      | "[" [target_list] "]"
def Target():
	if token == LP or token == LB:
		lex()
		targets = Target_List()
	elif token == IDENTITY:
		idty = text
		lex()
		return [idty]


def replace_params(func_def, call_params, indentation, vars_in_scope):
	stashLex()

	fname = func_def["fname"]
	fparams = func_def["params"]
	fcode = func_def["fcode"]
	fvars = func_def["fvars"]

	returnVar = genRandomVarName()
	fcode_inlined = []
	for line in fcode:
		tabs = re.search("^(\t*)", line).group(1)
		line_inlined = indentation + tabs

		loadLex(line)
		while True:
			lex()
			if token == EOL:
				break
			elif token == IDENTITY:
				print("IDENTITY: " + text)
				ident = text 
				lex()
				print("CHECK NEXT:" + text)
				if token != LP:
					if token == KEYWORD or token == IDENTITY:
						wspace = " "
					else:
						wspace = ""

					if (ident in vars_in_scope or ident in call_params) and ident not in fparams:
						fparams.append(ident)
						call_params.append(genRandomVarName())

					if ident in fparams:
						line_inlined += call_params[fparams.index(ident)] + " " + text + wspace
					elif ident in vars_in_scope: 
						line_inlined += genRandomVarName() + " " + text + wspace
					else:
						line_inlined += ident + " " + text + wspace
				else:
					line_inlined += ident + " " + text
			elif token == KEYWORD:
				print("KEYWORD: " + text)
				if text == "return":
					line_inlined += returnVar + " = "
				else:
					line_inlined += text + " "
			else:
				print("MISC: " + text)
				line_inlined += text
		fcode_inlined.append(line_inlined + "\n")
	restoreLex()
	return fcode_inlined, returnVar


def func_def(line_num, read_data, funcs):

	def_found = re.search("^(\t*)def\s+(\w+)\s*\((.*)\)\s*:\s*(.*)\n$", read_data[line_num])
	#print("FOUND A DEF!!")
	indent = len(def_found.group(1))
	fname = def_found.group(2)
	params_plus = def_found.group(3).replace(" ","").replace("\t","").split(",")
	func_head = read_data[line_num][:-len(def_found.group(4))-1] + "\n"

	params = []
	if params_plus[0] != '':
		##print(params_plus)
		for param in params_plus:
			loadLex(param)
			lex()
			params.append(text)

	##print(len(def_found.group(4)))
	if len(def_found.group(4)) > 0 and not re.match("^\s*$", def_found.group(4)):
		body = [def_found.group(1) + def_found.group(4) + "\n"]
	else:
		body = []
		while line_num < len(read_data)-1:
			line_num += 1	
			
			m2 = re.search("^(\t*).*$",read_data[line_num])
			indent2 = len(m2.group(1))

			if indent2 > indent: #All lines in the functions will be indented more than the function def line
				indentless = re.match("^(\t*)(.*\n)$",read_data[line_num])
				#print("INDENTLESS: " + indentless.group(2))
				tabs = ""
				for i in range(indent2-indent-1):
					tabs += "\t"
				body.append(tabs + indentless.group(2))
			else: # We are outside the function (i.e. done)
				line_num -= 1 # Corrective
				break

	f_code = {"fname": fname, "params": params, "fcode": body}

	funcs[fname] = f_code

	opt_body, fvars = parser(f_code["fcode"], funcs, params, 0, def_found.group(1) + "\t") # We want to parse body of function recursively
								# Funcs we have already found will be available to funcs defined inside current function
	opt_code = [func_head] + opt_body
	funcs[fname]["fvars"] = fvars
	return opt_code, line_num, funcs

def loops(line_num, read_data, funcs, vars_in_scope):
	#print("FOUND A LOOP!")
	##print(read_data[line_num])

	for_loop_found = re.search("^(\t*)for\s+.*:\s*(.*)\n$", read_data[line_num])
	while_loop_found = re.search("^(\t*)while\s+.*:\s*(.*)\n$", read_data[line_num])

	if for_loop_found:
		loop_found = for_loop_found
		lex()
		vars_in_scope += Target_List()

	else:
		loop_found = while_loop_found

	indent = len(loop_found.group(1))
	first_line = loop_found.group(2)

	loop_head = read_data[line_num][:-len(loop_found.group(2))-1] + "\n"

	# #print (len(first_line))
	# #print(first_line)
	if len(first_line) > 0 and not re.match("^\s*$", first_line):
		body = [loop_found.group(1) + first_line + "\n"]
	else:
		body = []
		while line_num < len(read_data)-1:
			line_num += 1
			##print(read_data[line_num])

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

	opt_body, vars_in_scope = parser(body, funcs, vars_in_scope, 2, loop_found.group(1)+"\t") # We want to parse body of function recursively
									# Set flag inner_loop to say 
	opt_code = [loop_head] + opt_body
	return opt_code, line_num, vars_in_scope

# NOTE ABOUT inner_loop
# 0 = not in a loop
# 1 = in a loop, but not the inner loop
# 2 = in the inner loop
def parser(read_data, funcs = {}, vars_in_scope = [], inner_loop = 0, scope_indentation = ""):
	line_num = 0	#init counter
	#funcs = {}	#init list for storing functions

	opt_code = []

	while line_num < len(read_data):

		if re.match("^\s*\n$", read_data[line_num]): #Skip empty lines 
			line_num += 1
			continue
		#Clean out comments
		if re.match("^\s*#.*$", read_data[line_num]): #Skip comment lines
			line_num += 1
			continue	
		comment_found = re.search("^(.*)\s*#.*", read_data[line_num])
		if comment_found:	
			read_data[line_num] = comment_found.group(1) + "\n"


		#opt_code.append(read_data[line_num])
		loadLex(read_data[line_num])
		lex()

		if token == KEYWORD:
			if text == "def":
				opt_body, line_num, funcs = func_def(line_num, read_data, funcs)
				opt_code = opt_code + opt_body

				#print("VARSINSCOPE: ")
				#print(vars_in_scope)
			elif text == "for" or text == "while":
				if inner_loop == 2:
					inner_loop = 1 # If we just found a loop, this can't the body of an inner loop

				opt_body, line_num, vars_in_scope = loops(line_num, read_data, funcs, vars_in_scope)

				opt_code = opt_code + opt_body

				#print("VARSINSCOPE: ")
				#print(vars_in_scope)

			elif text == "global":
				opt_code.append(read_data[line_num])
				lex()
				vars_in_scope += Target_List()
				vars_in_scope = list(set(vars_in_scope))
			else:
				opt_code.append(read_data[line_num])
		elif token == IDENTITY:
			#print("This line starts with an id!")
			opt_code.append(read_data[line_num])
			new_ids = Target_List()
			if token == ASSIGN:
				vars_in_scope = vars_in_scope + new_ids
				vars_in_scope = list(set(vars_in_scope))
		else:
			opt_code.append(read_data[line_num])

		line_num += 1
		
	#print(opt_code)
	############################
	# CODE HERE TO CATCH LOOPS # (assumes no function definition inside loops. FIX LATER)
	############################
	if(inner_loop == 2):
		#print("INNER LOOP")
		##print (opt_code)
		##print (funcs)
		inlined_code = []
		for line in opt_code:

			indent_match = re.search("^(\t*).*", line)
			indentation = indent_match.group(1)

			i = 0
			line_rewrite = scope_indentation + indentation

			params_found = []
			loadLex(line)
			#print(line)
			while True:
				lex()
				if token == EOL:
					break
				elif token == IDENTITY:
					#print("ID: " + text)
					the_id = text
					lex()
					after_id = text
					if token == LP:
						#print("LP")
						params_found = []
						lit_to_var = []
						old_params = ""
						while token != RP:
							lex()
							if token == IDENTITY:
								params_found.append(text)
							elif token == STRLIT or token == NUMLIT:
								varName = genRandomVarName()
								params_found.append(varName)
								lit_to_var.append(scope_indentation + indentation + varName + " = " + text + "\n")
							elif token == RP:
								break
							old_params += text

						if the_id in funcs.keys():
							#print("func defined")
							inlined_code += lit_to_var
							inline_it, returnVar = replace_params(funcs[the_id], params_found, scope_indentation + indentation, vars_in_scope)
							inlined_code = inlined_code + inline_it
							line_rewrite += returnVar + " "
						else:
							#print ("This one")
							line_rewrite += the_id + "(" + old_params + ")"
					elif token == EOL:
						break
					else:
						#print("NOT RP")
						#print(text)
						line_rewrite += the_id + " " + after_id
				elif token == KEYWORD:
					line_rewrite += text + " "
				else:
					line_rewrite += text
				#print(line_rewrite)

			inlined_code.append(line_rewrite + "\n")

		return inlined_code, vars_in_scope
	else:
		indented_opt_code = []
		#print("NOT INNER LOOP")
		for line in opt_code:
			indented_opt_code.append(scope_indentation + line)
		return indented_opt_code, vars_in_scope
	

def main():
	filename = sys.argv[1]
	with open(filename, 'r') as f:
		read_data = f.readlines()

	##print(read_data)
	##print (len(read_data))


	opt_code, _ = parser(read_data) 

	##print(opt_code)
	new_file = open('generated.py', 'w')
	for item in opt_code:
		##print(opt_code)
		new_file.write(item)



if __name__ == "__main__":
    main()
