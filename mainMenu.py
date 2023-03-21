print('\nWelcome to 2205 Applied Crypto!')
while(1):
	print('\nThe following options are available to the user: ')
	print('1. Do this ')
	print('2. Do that ')
	print('3. Exit ')
	
	option = int(input('Enter your choice: '))
	
	if(option == 1):
		print("\nYou did this")
	elif(option == 2):
		print("\nYou did that")
	elif(option == 3):
		print('\nThank you for using our program. Have a nice day!')
		break
	else:
		print('This is an invalid option.')
