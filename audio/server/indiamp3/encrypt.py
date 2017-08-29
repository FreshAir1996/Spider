

def myencrypt(string):
	num = 0
	for c in string:
		num += ord(c)

	return num

url = 'https://www.indiamp3.com/haji-fsaji-fhmp3-songs/fsajlk falFk ab'
print myencrypt(url)
