# Python program to check if the input number is prime or not

import math

# prime numbers are greater than 1
def prime (num):
   	for j in range (2,int(math.sqrt(num))+1):
   		if (num % j) == 0:
   			return False
	return True


   # check for factors
for num in range(2,100000):
	if prime(num):
		print(num)



