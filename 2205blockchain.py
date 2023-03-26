import server
import client
import threading

server_thread = threading.Thread(target=server.start_server)
server_thread.start()

client.send_message()

import hashlib as hasher
import datetime as date

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Signature import pkcs1_15

import random
import time

# global variables
supply_blockchain = []
utxo_array = []
manufacturerList = []
buyerList = []
global_index = 0
pow_proof = int(0)

class Supply_Block:
	# represents a block in a blockchain
	# The initialisation function allows the setting up of a block, is called when a new block is created
	def __init__(self, index, timestamp, supply_data, previous_hash):
		self.index = index
		self.timestamp = timestamp
		self.supply_data = supply_data
		self.previous_hash = previous_hash
		self.proof_of_work = int(generate_pow())
		
		# compute the hash of the block, set it as the `hash` attribute
		self.hash = self.hash_block()
		
	# The hashing function for the block using SHA 256
	def hash_block(self):
		sha = hasher.sha256()
		
		sha.update((str(self.index) + 
               str(self.timestamp) + 
               str(self.supply_data) + 
               str(self.previous_hash)).encode('utf-8'))
               
		# returns the hexadecimal representation of the resulting hash using the hexdigest method
		return sha.hexdigest()
		
# Algorithm for generating a proof-of-work (based on bitcoin PoW)
# proof of work is a value that satisfies a certain condition, eg. having a certain number of leading zeros in its hash 
# This function uses a brute-force approach to find a value that satisfies this condition
# The algorithm requires to find SHA256 of a natural number (string) such that has the first three positions as '000' and ends with '00'
def generate_pow():
	start_time = time.time()
	global pow_proof
	initial_start = pow_proof + 1
	
	while(1):
		sha = hasher.sha256()
		sha.update(str(initial_start).encode('utf-8'))
		hash_value = sha.hexdigest()
		initial_start = int(initial_start) + 1
		
		# check if the hash value satisfies the proof-of-work condition by checking the first three and last two characters of the hash value
		if(hash_value[0] == '0' and hash_value[1] == '0' and hash_value[2] == '0' and hash_value[-1] == '0' and hash_value[-2] == '0'):
			
			# calculates the time taken to find the proof of work and sets the pow_proof variable to the integer value that satisfied the condition
			end_time = time.time()
			pow_proof = initial_start - 1
			print('\nThe required hash value is: ' + hash_value)
			print('The PoW number is: ' + str(pow_proof))
			print('The total time taken is: ' + str((end_time - start_time)))
			
			break
	
	return pow_proof

class Transaction:
	
	# The initialisation function for a single (NEW) transaction
	# defines a basic transaction structure that can be used in a blockchain system
	def __init__(self, supplier_puk, receiver_puk, item_id, timestamp, signature):
		self.supplier_puk = supplier_puk
		self.receiver_puk = receiver_puk
		self.item_id = item_id
		self.timestamp = timestamp
		self.signature = signature

# This function is used to create genesis block
def create_genesisBlock():
	global global_index 
	global_index = global_index + 1
	print('\n\nThe genesis block is being created.')
	
	# This block serves as the first block in the blockchain and is used to initialize the chain
	# date.datetime.now() means the current date and time
	return Supply_Block(0, date.datetime.now(), "GENESIS BLOCK", "0")

# This function is used for viewing all the blocks and the transactions in the blockchain
def view_blockchain():
	print('\n\nThe list of blocks are: \n')
	for block in supply_blockchain:
		print('\n------------------------------------------------------------------------------------------------------------------------')
		print(block.index)
		print(block.timestamp)
		print(block.supply_data)
		print(block.proof_of_work)
		print(block.hash)
		print(block.previous_hash)
	print('------------------------------------------------------------------------------------------------------------------------')
	print('\n\n')
	
# This function is used to view all the Unspend Transaction Outputs
def view_UTXO():
	print('\n\nThe list of UTXO are: \n')
	for transaction in utxo_array:
		print('\n------------------------------------------------------------------------------------------------------------------------')
		print(transaction.supplier_puk.exportKey("PEM").decode('utf-8'))
		print(transaction.receiver_puk)
		print(transaction.item_id)
		print(transaction.timestamp)
		print(transaction.signature)
	print('------------------------------------------------------------------------------------------------------------------------')
	print('\n\n')

# This function is used to generate a transaction
def make_transaction(supplier_key, receiver_key, item_id):
	
	while True:
		print('\nList of manufacturers:')
		print('\n1. Nike')
		print('2. Adidas')
		print('3. Puma')
		print('4. Under Armour')
		selection = input('\nChoose a manufacturer by inputting its number (1-4): ')
		
		if selection not in ['1', '2', '3', '4']:
			print('\nInvalid input. Please enter a number from 1 to 4')
			continue

		index = int(selection)
		
		if index == 1:
			print('Nike')
		elif index == 2:
			print('Adidas')
		elif index == 3:
			print('Puma')
		elif index == 4:
			print('Under Armour')
			
		# in an array, first index/selection start from 0, eg. the 5th selection is index 4
		supplier_key = manufacturerList[index-1]
		break

	# enter a specific buyer for the manufacturer
	while True:
		print('There are a total of ' + str(len(buyerList)) + ' buyers.')
		index = input('Choose a buyer to assign this transaction to. (1-' + str(len(buyerList)) + '): ')
		# if the input is in the range of 1 to the number of buyers input upon running the program
		if index.isdigit() and int(index) in range(1, len(buyerList)+1):
			index = int(index) - 1
			receiver_key = buyerList[index]
			break
		else:
			print('\nInvalid input. Please enter a number from 1 to', len(buyerList), '\n')
			continue
	
	# exports the public key of the receiver in the PEM format and stores it in the receiver_puk variable as a string
	receiver_puk = receiver_key.publickey().exportKey("PEM").decode('utf-8')
	item_id = input('Enter the ID of the tracked item: ')
	
	# retrieves the PUBLIC key component of the supplier's key pair
	supplier_puk = supplier_key.publickey()
	timestamp = date.datetime.now()
	
	# Generating the message text and the signature, concatenates the 4 things
	message = str(supplier_puk.exportKey("PEM").decode('utf-8')) + str(receiver_puk) + item_id + str(timestamp)
	hash_message = SHA256.new(message.encode('utf-8'))
	
	# retrieves the PRIVATE key component of the supplier's key pair
	supplier_prk = RSA.import_key(supplier_key.exportKey("DER"))

	# generates a digital signature of the hashed message using the PKCS#1 v1.5 padding scheme and the supplier private key
	signature = pkcs1_15.new(supplier_prk).sign(hash_message)
	
	# Creating a new transaction
	new_transaction = Transaction(supplier_puk, receiver_puk, item_id, timestamp, signature)
	utxo_array.append(new_transaction)

# The function for mining the block in the supply blockchain
def mine_block():
	global global_index
	max_range = len(utxo_array)
	transaction_amount = random.randint(0, max_range)
	transaction_array = []
	
	print('\nThe number of selected transactions for the block is: ' + str(transaction_amount))
	
	# If transaction_amount is not equal to 0, a for loop iterates over transaction_amount
	if(transaction_amount):
		for index in range(0, transaction_amount):
			
			# All verifications for the transactions
			
			# if this function returns true
			if(verify_transaction(utxo_array[0])):
				print('\nThe sign verification for transaction #' + str(index + 1) + ' was true!')
				if(check_item_code(utxo_array[0])):
					print('The item code has been found. Checking the previous owner details.')
					if(check_previous_owner(utxo_array[0])):
						print('Verification of previous owner has been done!')
						transaction_array.append(utxo_array[0])
					else:
						print('Verification of previous owner has failed!')
				else:
					print('The item code was not found on blockchain. Checking for manufacturer credentials.')
					if(check_manufacturer_credentials(utxo_array[0])):
						print('The new item has been added under the manufacturer.')
						transaction_array.append(utxo_array[0])
					else:
						print('The transaction key is not authorised as a manufacturer!')
			else:
				print('The sign verification for transaction #' + str(index + 1) + ' was false!')
			utxo_array.pop(0)
		
		if(len(transaction_array) != 0):
			new_block = Supply_Block(global_index, date.datetime.now(), transaction_array, supply_blockchain[global_index - 1].hash)
			global_index = global_index + 1
			supply_blockchain.append(new_block)
		
	# if transaction array is empty
	else:
		# Prevent addition of blocks with no transactions
		print('No transactions have been selected and therefore no block has been added!')

# This function is used for the verifying the signature of the transaction
def verify_transaction(self):
	# convert supplier_puk to a RSA public key with the import_key method
	# then passing it the DER encoded version of the key
	supplier_puk = RSA.import_key(self.supplier_puk.exportKey("DER"))
	
	# concatenate the PEM encoded version of the four attributes into a single string
	message = str(self.supplier_puk.exportKey("PEM").decode('utf-8')) + str(self.receiver_puk) + self.item_id + str(self.timestamp)
	hash_message = SHA256.new(message.encode('utf-8'))
	
	try:
		# verify the digital signature
		pkcs1_15.new(supplier_puk).verify(hash_message, self.signature)
		return True
	except (ValueError, TypeError):
		return False
	
# Smart contract for checking if the input item code is avaiable on the blockchain & checking the previous owner of the consignment
def check_item_code(self):
	found_flag = False
	temp_blockchain = supply_blockchain[::-1]
	
	for block in temp_blockchain[:-1:]:
		for transaction in block.supply_data:
			if(transaction.item_id == self.item_id):
				found_flag = True
	
	return found_flag
	
# Smart contract for checking the previous owner of the commodity
def check_previous_owner(self):
	found_flag = False
	temp_blockchain = supply_blockchain[::-1]
	
	for block in temp_blockchain[:-1:]:
		for transaction in block.supply_data:
			if(transaction.item_id == self.item_id):
				if(transaction.receiver_puk == self.supplier_puk.exportKey("PEM").decode('utf-8')):
					return True
				else:
					return False

# Smart contract for checking if the user is an authorised manufacturer
def check_manufacturer_credentials(self):
	for item in manufacturerList:
		if str(self.supplier_puk.exportKey("PEM").decode('utf-8')) == str(item.publickey().exportKey("PEM").decode('utf-8')):
			return True
	
	return False

# The function would verify all the blocks in the given blockchain
def verify_blockchain():
	previous_block = supply_blockchain[0]
	count = 1
	
	for block in supply_blockchain[1:]:
		print('\nFor the block #' + str(count) + ': ')
		for transaction in block.supply_data:
			print('The item ID is ' + str(transaction.item_id) + ' and the associated timestamp is ' + str(transaction.timestamp))
		
		if(str(previous_block.hash) == str(block.previous_hash)):
			print('The hash values have been verified.')
		
		sha = hasher.sha256()
		sha.update(str(int(block.proof_of_work)).encode('utf-8'))
		hash_value = sha.hexdigest()
		print('The PoW number is ' + str(block.proof_of_work) + ' and the associated hash is ' + hash_value)
		
	print('------------------------------------------------------------------------------------------------------------------------')
	print('\n\n')

# Function for generating manufacturer keys
# def generate_manufacturerKeys(number):
# 	for item in range(0, int(number)):
# 		manufacturerList.append(RSA.generate(1024, Random.new().read))
	#print(manufacturerList)
	#print('\nThe manufacturer keys have been generated.')
	
# Function for generating buyer keys
def generate_buyerKeys(number):
	for item in range(0, int(number)):
		buyerList.append(RSA.generate(1024, Random.new().read))
	print("Buyer Listtttttttttttttttttttt: ", buyerList)
	print('\nThe buyer keys have been generated.')
	
# Function for tracking an item
def track_item(itemCode):
	notFoundFlag = True
	
	# iterate starts from second block(index 1) as the first block was the genesis block (no transactions)
	for block in supply_blockchain[1:]:
		for transaction in block.supply_data:

			# if the code matches the id of a transaction
			if(itemCode == transaction.item_id):
				if(notFoundFlag):
					print('\nThe item (' + itemCode + ') has been found and the tracking details are: ')
					notFoundFlag = False
				
				manufacturer_suppplier = False
				manufacturer_receiver = False
				
				supplierCount = 0
				supplierNotFoundFlag = True
				
				for item in manufacturerList:
					supplierCount = supplierCount + 1
					
					# if supplier_puk matches the public key of any of the manufacturers in manufacturerList
					if str(transaction.supplier_puk.exportKey("PEM").decode('utf-8')) == str(item.publickey().exportKey("PEM").decode('utf-8')):
							supplierNotFoundFlag = False
							manufacturer_suppplier = True
							break
				
				if(supplierNotFoundFlag):
					supplierCount = 0
					
					for item in buyerList:
						supplierCount = supplierCount + 1

						# if supplier_puk matches the public key of any of the manufacturers in buyerList
						if str(transaction.supplier_puk.exportKey("PEM").decode('utf-8')) == str(item.publickey().exportKey("PEM").decode('utf-8')):
							supplierNotFoundFlag = False
							break
				
				receiverCount = 0
				receiverNotFoundFlag = True
				
				for item in manufacturerList:
					receiverCount = receiverCount + 1
					
					# if receiver_puk matches the public key of any of the manufacturers in manufacturerList
					if str(transaction.receiver_puk) == str(item.publickey().exportKey("PEM").decode('utf-8')):
							receiverNotFoundFlag = False
							manufacturer_receiver = True
							break
				
				if(receiverNotFoundFlag):
					receiverCount = 0
					
					for item in buyerList:
						receiverCount = receiverCount + 1

						# if receiver_puk matches the public key of any of the manufacturers in buyerList
						if str(transaction.receiver_puk) == str(item.publickey().exportKey("PEM").decode('utf-8')):
							receiverNotFoundFlag = False
							break
				
				finalResult = ""
				
				if(manufacturer_suppplier):
					finalResult = finalResult + "Manufacturer #" + str(supplierCount) + " transferred the asset to "
				else:
					finalResult = finalResult + "buyer #" + str(supplierCount) + " transferred the asset to "

				if(manufacturer_receiver):
					finalResult = finalResult + "Manufacturer #" + str(receiverCount) + " at " + str(transaction.timestamp)
				else:
					finalResult = finalResult + "buyer #" + str(receiverCount) + " at " + str(transaction.timestamp)
				
				print(finalResult)
				
	if(notFoundFlag):
		print('\nThe item code was not found in the blockchain.')

# f = open('C:\\Users\\Jevan\\OneDrive\\Desktop\\FraudFence-main\\sneaksecure.txt', 'r')
f = open('sneaksecure.txt', 'r')
sneaksecureLogo = f.read()
print(sneaksecureLogo)
f.close()
print('\nWelcome to Supply Blockchain 2205!')

# Generating keys for manufactures
# Nike, Adidas, Puma, Under Armour
numManufacturers = 4
# generate_manufacturerKeys(numManufacturers)
for item in range(0, numManufacturers):
	manufacturerList.append(RSA.generate(1024, Random.new().read))
	print("RSA key generated for manufacturer", item+1)

while True:
	numBuyers = input('\nEnter the number of buyers: ')
	if not numBuyers.isdigit() or int(numBuyers) <= 0:
		print("Invalid input! Please enter a number.")
		continue
	numBuyers = int(numBuyers)
	generate_buyerKeys(numBuyers)
	break

# Inserting a genesis block into blockchain
supply_blockchain.append(create_genesisBlock())

print('\n\nNumber of manufacturers and buyers successfully recorded!')

# Menu driven program for the supply blockchain
while(1):
	print('\nThe following options are available to the user: ')
	print('1. View the blockchain. ')
	print('2. Enter a transaction. ')
	print('3. View the UTXO array. ')
	print('4. Mine a block. ')
	print('5. Verify the blockchain. ')
	print('6. Generate RSA keys. ')
	print('7. Track an item.')
	print('8. Exit.')
	
	choice = int(input('Enter your choice: '))
	
	if(choice == 1):
		view_blockchain()
	elif(choice == 2):
		make_transaction('','','')
	elif(choice == 3):
		view_UTXO()
	elif(choice == 4):
		mine_block()
	elif(choice == 5):
		verify_blockchain()
	elif(choice == 6):
		numManufacturers = int(input('\nEnter the number of manufacturers: '))
		generate_manufacturerKeys(numManufacturers)
		numBuyers = int(input('Enter the number of buyers: '))
		generate_buyerKeys(numBuyers)
	elif(choice == 7):
		itemCode = input('Enter the item code: ')
		track_item(itemCode)
	elif(choice == 8):
		print('\nThank you for using our program. Remember to keep your kicks real!')
		break
	else:
		print('This is an invalid option.')
		continue