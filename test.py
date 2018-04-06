import random

def test(x,y):
	A=3
	if True:
		x = ord('a')
	else:
		x = 0
	y=4
	for i in range(3):
		j = 0
		if i <= 2:
			print("THESTH" + str(i))
	return x+y
#HERE
def genRandomVarName(uppercase): #HEER
	varName = "Var_"
	for j in range(1000):
		for i in range(1000):
			test(5,10)
		return varName + str(random.randrange(100))

genRandomVarName(1)

