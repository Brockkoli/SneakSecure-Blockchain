import hashlib
import datetime
import json
import ecdsa
import base64
import os
import mysql.connector
import csv
import colorama
from pyfiglet import Figlet
from termcolor import colored

# Initialize colorama
colorama.init()

class Block:
    def __init__(self, index, timestamp, data, previous_hash, nonce):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        sha = hashlib.sha256()
        sha.update(str(self.index).encode('utf-8') +
                   str(self.timestamp).encode('utf-8') +
                   str(self.data).encode('utf-8') +
                   str(self.previous_hash).encode('utf-8') +
                   str(self.nonce).encode('utf-8'))
        return sha.hexdigest()

def create_genesis_block(difficulty):
    now_timestamp = datetime.datetime.now()
    formatted_time = now_timestamp.strftime("%d-%m-%Y %H:%M:%S")
    nonce = 0
    new_hash = ""
    while not new_hash.startswith("0" * difficulty):
        nonce += 1
        block = Block(0, formatted_time, "Genesis Block", "nil", nonce)
        new_hash = block.calculate_hash()

    return block

def read_transaction_elements():
    # Load the signed transaction from the JSON file
    with open('signed_transaction.json', 'r') as f:
        signed_transaction = json.load(f)

    # convert dictionary to string
    json_str = json.dumps(signed_transaction)
    # Parse the JSON string into a Python object
    json_obj = json.loads(json_str)
    # Access the elements of the object using indexing
    transaction_details = json.loads(json_obj['transaction_details'][0])
    trans_str = json.dumps(transaction_details)
    trans_obj = json.loads(trans_str)
    model = trans_obj['shoe_model']
    price = trans_obj['price']
    buyer_address = json_obj['transaction_details'][1]['buyer_address']
    UTXO = json_obj['transaction_details'][1]['UTXO']
    signature = json_obj['signature']

    return model, price, buyer_address, UTXO

def mine_block(difficulty):
    now_timestamp = datetime.datetime.now()
    formatted_time = now_timestamp.strftime("%d-%m-%Y %H:%M:%S")
    nonce = 0
    new_hash = ""

    with open('blockchain.csv', mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        previous_hash = ""
        for row in reader:
            current_hash = row['Hash']
            if previous_hash != "":
                previous_hash = row['Previous_hash']
            # Set previous_hash to the current hash value for the next iteration
            previous_hash = current_hash


    while not new_hash.startswith("0" * difficulty):
        nonce += 1
        # Load the signed transaction from the JSON file
        print(colorama.Fore.YELLOW + "Running POW consensus algorithm to mine block..." + colorama.Style.RESET_ALL)
        with open('signed_transaction.json', 'r') as f:
            signed_transaction = json.load(f)
            with open('blockchain.csv', mode='r') as csv_file:
                csv_reader = csv.reader(csv_file)
                for i, row in enumerate(csv_reader):
                    rowno = i
            mblock = Block(rowno, formatted_time, signed_transaction, previous_hash, nonce)
            # for index in csv
            new_hash = mblock.calculate_hash()
    print(colorama.Fore.GREEN + "\n[+] Block mined successfully." + colorama.Style.RESET_ALL)

    return mblock

def save_genblock_to_csv(block):
    with open('blockchain.csv', mode='w', newline='') as csv_file:
        fieldnames = ['Index', 'Timestamp', 'Data', 'Previous_hash', 'Nonce', 'Hash']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'Index': block.index,
                         'Timestamp': block.timestamp,
                         'Data': block.data,
                         'Previous_hash': block.previous_hash,
                         'Nonce': block.nonce,
                         'Hash': block.hash})

def store_mined_block(mblock):
    with open('blockchain.csv', mode='a', newline='') as csv_file:
        fieldnames = ['Index', 'Timestamp', 'Data', 'Previous_hash', 'Nonce', 'Hash']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Check if the file is empty, and write the header if it is
        if csv_file.tell() == 0:
            writer.writeheader()

        writer.writerow({'Index': mblock.index,
                         'Timestamp': mblock.timestamp,
                         'Data': mblock.data,
                         'Previous_hash': mblock.previous_hash,
                         'Nonce': mblock.nonce,
                         'Hash': mblock.hash})

def verify_transaction_mine_block():

    # Load the signed transaction from the JSON file
    with open('signed_transaction.json', 'r') as f:
        signed_transaction = json.load(f)

    # Load the buyer's public key from the file
    with open('buyer_public_key.pem', 'rb') as f:
        vk_pem = f.read()

    # Create a new verifying key object from the public key
    vk = ecdsa.VerifyingKey.from_pem(vk_pem)

    # Extract the transaction details and signature from the signed transaction
    transaction_details = signed_transaction['transaction_details']
    encoded_signature = signed_transaction['signature']

    # Decode the signature from base64
    signature = base64.b64decode(encoded_signature.encode())

    # Convert the transaction details dictionary to a JSON string
    transaction_details_json = json.dumps(transaction_details)

    # Verify sufficient utxo
    _, transaction_px, _, _ = read_transaction_elements()
    _, _, _, utxo = read_transaction_elements()
    _, _, buyer_address, _ = read_transaction_elements()
    try:
        if int(utxo) > int(transaction_px):
            # Verify the signature using the buyer's public key
            if vk.verify(signature, transaction_details_json.encode()):
                print(colorama.Fore.GREEN + "Transaction verified successfully." + colorama.Style.RESET_ALL)
                # delete transaction json file to prevent reusing of transaction
                os.remove("signed_transaction.json")

                # update coins in database
                # Open a connection to the database
                mydb = mysql.connector.connect(
                    host="localhost",
                    port=3306,
                    user="root",
                    password="toor",
                    database="sneaksecure"
                )

                # check if the database connection is open
                if mydb.is_connected():
                    print(colorama.Fore.CYAN + "Database connection is open" + colorama.Style.RESET_ALL)
                else:
                    print(colorama.Fore.RED + "Database connection is closed" + colorama.Style.RESET_ALL)

                # create cursor object to execute queries
                mycursor = mydb.cursor()

                # Query the database for the buyer's name
                new_buyer_coins = int(utxo) - int(transaction_px)

                try:
                    mycursor.execute("UPDATE buyer SET Coins=%s WHERE Address=%s", (new_buyer_coins, buyer_address))
                    mydb.commit()
                    print(colorama.Fore.GREEN + "Buyer coins updated successfully." + colorama.Style.RESET_ALL) 
                except Exception as e:
                    print(colorama.Fore.RED + f"Error updating buyer coins: {e}" + colorama.Style.RESET_ALL)

                try:
                    mycursor.execute("UPDATE manufacturers SET Coins=Coins+%s WHERE Name='syndicate'", (transaction_px,))
                    mydb.commit()
                    print(colorama.Fore.GREEN + "Manufacturer coins updated successfully." + colorama.Style.RESET_ALL)
                except Exception as e:
                    print(colorama.Fore.RED + f"Error updating manufacturer coins: {e}" + colorama.Style.RESET_ALL)

                # Close the database connection
                mycursor.close()
                mydb.close()

            else:
                print(colorama.Fore.RED + "[!] Transaction discarded." + colorama.Style.RESET_ALL)
        else:
            print(colorama.Fore.RED + "[!] Insufficient coins. Transaction discarded." + colorama.Style.RESET_ALL)
    except:
         print(colorama.Fore.RED + "No verified transactions available at the moment." + colorama.Style.RESET_ALL)

# Create the genesis block and save it to CSV file
def blockchain_checker():
    # Check if file exists
    csv_file_path = 'blockchain.csv'
    if os.path.exists(csv_file_path):
        # Check if file is empty
        if os.path.getsize(csv_file_path) > 0:
            print(colorama.Fore.YELLOW + "\nRetrieving blockchain..." + colorama.Style.RESET_ALL)
            mined_block = mine_block(3)
            store_mined_block(mined_block)
    else:
        try:
            genesis_block = create_genesis_block(3)
            print(colorama.Fore.GREEN + "Genesis Block generated." + colorama.Style.RESET_ALL)
            save_genblock_to_csv(genesis_block)
            print(colorama.Fore.CYAN + "[+] Genesis Block saved to blockchain.\n" + colorama.Style.RESET_ALL)
        except Exception as e:
            print(colorama.Fore.RED + "[!] Error generating Genesis Block." + colorama.Style.RESET_ALL)
            print(e)

def view_blockchain():
    try:
        with open('blockchain.csv', newline='') as csvfile:
            # Check if the CSV file is empty
            if not csvfile.read(1):
                print(colorama.Fore.RED + "\n[!] Mine a block to start creating blockchain." + colorama.Style.RESET_ALL)
            else:
                # Reset the file pointer
                csvfile.seek(0)

                # Create a CSV reader object
                reader = csv.reader(csvfile)

                # Skip the first row
                next(reader)

                # Iterate over each row
                for row in reader:
                    print(colorama.Fore.YELLOW + "-" * 70 + colorama.Style.RESET_ALL)
                    # Iterate over each column in the row and print its value in a separate row
                    for column in row:
                        print(column)
                    print(colorama.Fore.YELLOW + "-" * 70 + colorama.Style.RESET_ALL)
                    print("\n")
    except:
        print(colorama.Fore.RED + "\n[!] Mine a block to start creating blockchain." + colorama.Style.RESET_ALL)
                
import csv
import colorama

def verify_blockchain():
    # Define the file name and column name to check
    file_name = "blockchain.csv"
    Previous_hash = "Previous_hash"
    Hash = "Hash"
    
    # Open the CSV file
    with open(file_name, 'r') as csv_file:
        # Create a CSV reader object
        reader = csv.reader(csv_file)
        # Get the header row
        header_row = next(reader)
        # Get the last block
        rows = list(reader)
        last_row = rows[-1]
        # Get the value of the cell in the last block of the specified column
        last_value = last_row[header_row.index(Previous_hash)]
        # Get the block before the last block
        prev_row = rows[-2]
        # Get the value of the cell in the previous block of the specified column
        prev_value = prev_row[header_row.index(Hash)]
        # Compare the two values and print out the result
        if last_value == prev_value:
            print(colorama.Fore.YELLOW + "\nVerifying the blocks in the blockchain..." + colorama.Style.RESET_ALL)
            print(colorama.Fore.GREEN + "\n\t[+] All blocks in blockchain verified." + colorama.Style.RESET_ALL)
        else:
            print(colorama.Fore.YELLOW + "\nVerifying the blocks in the blockchain..." + colorama.Style.RESET_ALL)
            # Remove the last block from the blockchain
            with open(file_name, 'w', newline='') as new_csv_file:
                writer = csv.writer(new_csv_file)
                writer.writerow(header_row)
                for row in rows[:-1]:
                    writer.writerow(row)
            print(colorama.Fore.RED + "\n\t[!] Erroneous block detected and removed." + colorama.Style.RESET_ALL)

# Menu 
while(1):
    # Load logo and welcome msg
    f = open('sneaksecure.txt', 'r')
    sneaksecureLogo = f.read()
    print(sneaksecureLogo)
    f.close()
    
    g = Figlet(font='standard')
    print(colored(g.renderText('SneakSecure'), 'red'))

    print('\nWELCOME TO SNEAKSECURE!')
    print('\nMiner, please select your course of action: ')
    print('1. View the blockchain. ')
    print('2. Mine a block. ')
    print('3. Verify the blockchain. ')
    print('4. Exit.')
	
    choice = int(input('Enter your choice: '))
	
    if(choice == 1):
        view_blockchain()
    elif(choice == 2):
        try:
            blockchain_checker()
        except:
            print(colorama.Fore.RED + "No verified transactions available at the moment." + colorama.Style.RESET_ALL)
            exit(1)
        try:
            verify_transaction_mine_block()
        except:
            print(colorama.Fore.CYAN + "Consensus algorithm of difficulty 4 established.\n" + colorama.Style.RESET_ALL)
    elif(choice == 3):
        verify_blockchain()
    elif(choice == 4):
        print(colorama.Fore.GREEN + "\nThank you for using our program.")
        print("\nDon't be sneaky. Use SneakSecure!" + colorama.Style.RESET_ALL)      
        break
    else:
        print('This is an invalid option.')
        continue


