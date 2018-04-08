# Assume main function is at the end
# Assume tabs

import sys
import re
import random

# For now assume no function definitions inside loops

# TOKENS
IDENTITY = 0; VARIABLE = 1; FCALL = 2; STRLIT = 3; NUMLIT = 4; EOL = 5; KEYWORD = 6; 
LP = 7; RP = 8; ASSIGN = 9; OTHER = 10; COMMA = 11; COLON = 12; LB = 13; RB = 14;
BOOLLIT = 15;


keywords = [ "and",       "del",       "from",      "not",       "while",
"as",        "elif",      "global",    "or",        "with",
"assert",    "else",      "if",        "pass",      "yield",
"break",     "except",    "import",    "#print",	"True",		 "False",
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

# Function to generate new variable names.
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
	true_found = re.search("^\s*True[^\w]", line2lex[lnidx:])
	false_found = re.search("^\s*False[^\w]", line2lex[lnidx:])

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
	elif true_found:
		token, text = BOOLLIT, "True"
	elif false_found:
		token, text = BOOLLIT, "False"
	else:
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

# Function responsible for inlining code. Replaces parameters where appropriate
# and takes care of indentation
def inline_code(func_def, call_params, indentation, vars_in_scope):
	stashLex() #Save our progress in the inner loop where we are inlining code
	
	# Function info
	fname = func_def["fname"]
	fparams = func_def["params"]
	fcode = func_def["fcode"]
	fvars = func_def["fvars"]

	print("INLINING: " + fname)
	print(func_def["fcode"])
	returnVar = genRandomVarName() #This is the variable we assign the return value to
	fcode_inlined = []
	
	for line in fcode: # For each line in the function body
		tabs = re.search("^(\t*)", line).group(1)

		# Start building up the in-lined code by indenting it appropriately
		line_inlined = indentation + tabs

		# Parse through the line looking for identifiers
		loadLex(line)
		while True:
			lex()
			if token == EOL:
				break
			elif token == IDENTITY: # Found an identity
				print("IDENTITY: " + text)
				ident = text 
				lex()
				print("CHECK NEXT:" + text)
				if token != LP:		# Make sure it's not a function call
					# Ensure's proper spacing between neighboring ids/keywords
					if token == KEYWORD or token == IDENTITY:
						wspace = " "
					else:
						wspace = ""

					# If the ID is in the scope where we want to inline the code but it is not
					# in the parameters of the function, the names will conflict! 
					# To prevent this, we pretend this variable IS a parameter and that the function
					# call passed in an ID which we generate
					if (ident in vars_in_scope or ident in call_params) and ident not in fparams:
						fparams.append(ident)
						call_params.append(genRandomVarName())

					# If the ID is a function parameter, we replace it with the ID passed in
					# from the function call
					if ident in fparams:
						line_inlined += call_params[fparams.index(ident)] + " " + text + wspace
					else:
						line_inlined += ident + wspace + text + wspace
				else: # Leave function calls alone
					line_inlined += ident + text
			elif token == KEYWORD:
				# If we find a return statment, instead assign the return value
				# the return variable we generated at the beginning of in-lining
				if text == "return":
					print("HELLO HI" + returnVar)
					print(line_inlined)
					line_inlined += returnVar + " = "
					print(line_inlined)
				else:
					line_inlined += text + " "
				# NOTE! There is an inherent problem with this.
				# It only works if there is a single return statement in the function.
				# and it appears at the end. We could deal with this easily if python had goto statements
			else: # Otherwise move on. We aren't interesting in replacing anything 
				  # That isn't an identity or a return statement
				print("MISC: " + text)
				line_inlined += text
		# Add the rewritten line to the rewritten code
		fcode_inlined.append(line_inlined + "\n")
	restoreLex() # Restore our progress in the inner loop before returning
	return fcode_inlined, returnVar

# Function to capture the body of function definitions
def func_def(line_num, read_data, funcs):
	# Regex to separate out information from the function definition header
	def_found = re.search("^(\t*)def\s+(\w+)\s*\((.*)\)\s*:\s*(.*)\n$", read_data[line_num])
	
	indent = len(def_found.group(1))
	fname = def_found.group(2)
	params_plus = def_found.group(3).replace(" ","").replace("\t","").split(",")
	func_head = read_data[line_num][:-len(def_found.group(4))-1] + "\n"

	params = []

	# Separate parameters from their default values if they have any
	if params_plus[0] != '':
		for param in params_plus:
			loadLex(param)
			lex()
			params.append(text)

	# Next we want to capture the body of the text and run the parser on that
	if len(def_found.group(4)) > 0 and not re.match("^\s*$", def_found.group(4)):
		# Case of one line function declaration + body
		body = [def_found.group(1) + def_found.group(4) + "\n"]
	else:
		body = []
		while line_num < len(read_data)-1:
			line_num += 1	
			
			m2 = re.search("^(\t*).*$",read_data[line_num])
			indent2 = len(m2.group(1))

			if indent2 > indent: #All lines in the functions will be indented more than the function def line
				# Remove indentation preceding the function definition
				indentless = re.match("^(\t*)(.*\n)$",read_data[line_num])
				tabs = ""
				for i in range(indent2-indent-1):
					tabs += "\t"
				body.append(tabs + indentless.group(2))
			else: # We are outside the function (i.e. done)
				line_num -= 1 # Corrective
				break

	# Run the parser on the body of the function. Get back optimized code and vars in the scope of the function
	opt_body, fvars, inlinable = parser(body, funcs, params, 0, def_found.group(1) + "\t", True) # We want to parse body of function recursively
																						   # Funcs we have already found will be available to funcs defined inside current function
	dedent_body = []
	for i in range(len(opt_body)):
		dedent_body.append(opt_body[i][1:])

	# If inlinable, add this function to our record of functions in this scope
	if inlinable:
		f_code = {"fname": fname, "params": params, "fcode": dedent_body, "fvars": fvars}
		funcs[fname] = f_code

	# Replace the old function definition with the optimized version
	opt_code = [func_head] + opt_body
	return opt_code, line_num, funcs # Pass back up the opt_code, the line we are on in the old code,
									 # and the updated dictionary of functions


def loops(line_num, read_data, funcs, vars_in_scope, inlinable):
	#print("FOUND A LOOP!")
	##print(read_data[line_num])

	for_loop_found = re.search("^(\t*)for\s+.*:\s*(.*)\n$", read_data[line_num])
	while_loop_found = re.search("^(\t*)while\s+.*:\s*(.*)\n$", read_data[line_num])

	if for_loop_found:
		# Add variables declared in for loop header to vars in scope
		loop_found = for_loop_found
		lex()
		vars_in_scope += Target_List()
	else:
		loop_found = while_loop_found

	indent = len(loop_found.group(1))
	first_line = loop_found.group(2)

	loop_head = read_data[line_num][:-len(loop_found.group(2))-1] + "\n"

	if len(first_line) > 0 and not re.match("^\s*$", first_line):
		# Deal with case of 1 line loop definition
		body = [loop_found.group(1) + first_line + "\n"]
	else:
		body = []
		while line_num < len(read_data)-1:
			line_num += 1

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

	opt_body, vars_in_scope, inlinable = parser(body, funcs, vars_in_scope, 2, loop_found.group(1)+"\t", inlinable) # We want to parse body of function recursively
									# Set flag inner_loop to say 
	opt_code = [loop_head] + opt_body
	return opt_code, line_num, vars_in_scope, inlinable

# NOTE ABOUT inner_loop
# 0 = not in a loop
# 1 = in a loop, but not the inner loop
# 2 = in the inner loop
def parser(read_data, funcs = {}, vars_in_scope = [], inner_loop = 0, scope_indentation = "", inlinable = False):
	line_num = 0	#init counter
	opt_code = []
	#inlinable = True #For function bodies, keep track if this can be inlined

	while line_num < len(read_data):
		#Skip empty lines 
		if re.match("^\s*\n$", read_data[line_num]): 
			line_num += 1
			continue

		#Clean out comments
		if re.match("^\s*#.*$", read_data[line_num]): #Skip comment lines
			line_num += 1
			continue	
		comment_found = re.search("^(.*)\s*#.*", read_data[line_num])
		if comment_found:	
			read_data[line_num] = comment_found.group(1) + "\n"


		# Load the line in the lexical analyzer
		loadLex(read_data[line_num])
		lex()

		if token == KEYWORD:
			# Found the start of a function definition!
			if text == "def":
				# Catch its body and run the parser on it
				opt_body, line_num, funcs = func_def(line_num, read_data, funcs)
				opt_code = opt_code + opt_body # Append the optimized function to the new code

			# Found the start of a loop!
			elif text == "for" or text == "while":
				if inner_loop == 2:
					inner_loop = 1 # If we just found a loop, this can't the body of an inner loop
				# Catch its body and run the parser on it
				opt_body, line_num, vars_in_scope, inlinable = loops(line_num, read_data, funcs, vars_in_scope, inlinable)
				opt_code = opt_code + opt_body # Append the optimized loop to the new code

			# We assume functions that have return statements before their last line to not
			# be in-lineable
			elif text == "return" and (line_num < len(read_data) - 1 or inner_loop) > 0:
				inlinable = False
				opt_code.append(read_data[line_num])
			else:
				opt_code.append(read_data[line_num])
		elif token == IDENTITY or token == LP or token == LB: # Lines starting with target lists could be newly assigned vars
			opt_code.append(read_data[line_num]) # Append this line to our optimal code unchanged
			new_ids = Target_List()
			if token == ASSIGN: # If these IDs are on the LHS of an assignment operator, add them to the vars in scope
				vars_in_scope = vars_in_scope + new_ids
				vars_in_scope = list(set(vars_in_scope))
		else: #This line has no information we need
			opt_code.append(read_data[line_num]) # Append line unchanged

		line_num += 1
		
	#print(opt_code)
	############################
	# CODE HERE TO CATCH LOOPS # (assumes no function definition inside loops. FIX LATER)
	############################
	if(inner_loop == 2): # We have found an inner loop!
		inlined_code = []
		for line in opt_code:

			# Get the indentation of the line to use for indenting the inlined code correctly
			indent_match = re.search("^(\t*).*", line)
			indentation = indent_match.group(1)

			i = 0
			line_rewrite = scope_indentation + indentation # Begin line with proper indentation

			params_found = []
			loadLex(line) # Begin lexical analysis of the line

			while True:
				lex()
				if token == EOL:
					break
				elif token == IDENTITY: # We have found an identity!
					the_id = text
					lex()
					after_id = text
					if token == LP: # This identity is a function call!
						params_found = []
						lit_to_var = []
						old_params = ""
						while token != RP: # Grab the parameters!
							# NOTE: It would be better to parse for comma-separated expressions here
							# in order for this to work on a significantly larger portion of the language
							lex()
							if token == IDENTITY:
								params_found.append(text)
							elif token == STRLIT or token == NUMLIT or token == BOOLLIT:
								# Literal values get assigned to variables which we pretend were passed in instead
								varName = genRandomVarName()
								params_found.append(varName)
								lit_to_var.append(scope_indentation + indentation + varName + " = " + text + "\n")
							elif token == RP:
								break
							old_params += text # Save the old parameter string in case we choose not to in-line

						if the_id in funcs.keys(): # If is a function we have the definition of, we in-line it
							inlined_code += lit_to_var # Add the code assigning literal vals to vars first
							inline_it, returnVar = inline_code(funcs[the_id], params_found, scope_indentation + indentation, vars_in_scope)
							inlined_code = inlined_code + inline_it	# Add the in-lined code to the new body of the loop
							line_rewrite += returnVar + " " # Replace function call with returnVar name
						else:	# Function is not in our list of functions
							line_rewrite += the_id + "(" + old_params + ")" # Rewrite the function call as is
					elif token == EOL:
						line_rewrite += the_id + " "
						break
					else:
						line_rewrite += the_id + " " + after_id
				elif token == KEYWORD:
					line_rewrite += text + " "
				else:
					line_rewrite += text
			# Add the rewritten line to the inlined code
			inlined_code.append(line_rewrite + "\n")

		return inlined_code, vars_in_scope, inlinable # Return the new loop body
	else:
		# Otherwise, we need to reindent this code for the next scope up
		indented_opt_code = []
		for line in opt_code:
			indented_opt_code.append(scope_indentation + line)
		return indented_opt_code, vars_in_scope, inlinable
	

def main():
	filename = sys.argv[1]
	if len(sys.argv) > 2:
		outputfile = sys.argv[2]
	else:
		outputfile = filename[:-3] + '_opt.py'
	with open(filename, 'r') as f:
		read_data = f.readlines()
	print outputfile

	opt_code, _, _ = parser(read_data) 

	# Write the new code to a file
	new_file = open(outputfile, 'w')
	for item in opt_code:
		##print(opt_code)
		new_file.write(item)



if __name__ == "__main__":
    main()
