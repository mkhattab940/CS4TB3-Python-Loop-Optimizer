def red(up, down, left, right, i):
	if i < 0:
		return 2, 5
	twelve = up * down
	for e in range(3):
		left = left + right*down
		i -= 1
		right = blue(twelve, left, e, i)
		print("RED: " + str(right))
	return left, twelve

def blue(hip, hop, hooray, i):
	if i < 0:
		return 12
	hiphop = hip + hop + hooray
	for e in range(3):
		down = hip - hop
		i -= 1
		twelve, sweet = red(e, down, hop, hooray, i)
		print ("BLUE: " + str(hiphop))
	return 5 * sweet

blue(12,12,12,5)