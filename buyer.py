import socket
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import ecdsa
import base64
import mysql.connector
import getpass
import json
import colorama
import pyfiglet

title = pyfiglet.figlet_format("Buyer")
print(title)

# Status to check whether buyer is in db (1)
status = 0

# Initialize colorama
colorama.init()

class Transaction:
    def __init__(self, address, shoe_model, price, utxo):
        self.address = address
        self.shoe_model = shoe_model
        self.price = price
        self.utxo = utxo
        
    def __str__(self):
        return f"Transaction(address={self.address}, shoe_model={self.shoe_model}, price={self.price}, utxo={self.utxo})"


# Open a connection to the database
mydb = mysql.connector.connect(
  host="localhost",
  port=3306,
  user="root",
  password="toor",
  database="sneaksecure"
)

# create cursor object to execute queries
mycursor = mydb.cursor()

# Ask for the buyer's name
buyer_name = input(colorama.Fore.YELLOW + "Buyer, please enter your name: " + colorama.Style.RESET_ALL)
password = getpass.getpass(prompt=colorama.Fore.YELLOW + "Buyer, please input your password: " + colorama.Style.RESET_ALL)
hash_object = hashlib.sha256(password.encode())
pwhash = hash_object.hexdigest()

# Query the database for the buyer's name
mycursor.execute("SELECT * FROM `buyer` WHERE Name=%s AND Password=%s", (buyer_name, pwhash))

# Fetch the results of the query
result = mycursor.fetchall()

try:
    # result = [(4, 'Wayang', 'e3aeddf7eebc7730c310a7664a94cfe98c3109cb26c65771bc1ed0c7b201a3ab', 'Jo1G6543oU', 1000)], need to split into seperate elements
    buyer_id, buyer_name, buyer_pw, buyer_addr, buyer_coin = result[0]
except:
    print(colorama.Fore.RED + "Error. Unauthorised." + colorama.Style.RESET_ALL)

# Check if the buyer's name was found in the database
if len(result) != 0:
    status = 1
    msg = f"\n{buyer_name} was found in the database!"
    print(colorama.Fore.GREEN + msg + colorama.Style.RESET_ALL)
else:
    msg = f"\n[!] Access denied for {buyer_name}."
    print(colorama.Fore.RED + msg + colorama.Style.RESET_ALL)
    
# Close the database connection
mycursor.close()
mydb.close()

# Set up AES encryption key and initialization vector (IV)
key = b'Sixteen byte key'
iv = b'InitializationVe'

# Set up socket for connecting to manufacturer
HOST = '127.0.0.1'
PORT = 65432
if status == 1:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        # Encrypt and send transaction request to manufacturer
        transaction_request = "Please process transaction.".encode('utf-8')
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted_request = cipher.encrypt(pad(transaction_request, AES.block_size))
        s.sendall(encrypted_request)

        # Receive acknowledgement from manufacturer
        ack = s.recv(1024)
        # Decrypt received acknowledgement using AES
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_ack = unpad(cipher.decrypt(ack), AES.block_size)
        # Process received acknowledgement
        print(colorama.Fore.CYAN + "\nReceived acknowledgement from manufacturer: " + colorama.Style.RESET_ALL)
        print(f"\n\t[+] {decrypted_ack.decode('utf-8')}")

        # Send transaction details
        model = input(colorama.Fore.YELLOW + "Enter the shoe model you wish to purchase: " + colorama.Style.RESET_ALL)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_model = pad(model.encode(), AES.block_size)
        encrypted_model = cipher.encrypt(padded_model)
        s.sendall(encrypted_model)

        # Receive confirmation from manufacturer
        confirmation = s.recv(1024)
        # Decrypt received confirmation using AES
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_conf = unpad(cipher.decrypt(confirmation), AES.block_size)
        # Process received confirmation
        print(colorama.Fore.CYAN + "Received confirmation from manufacturer: " + colorama.Style.RESET_ALL)
        manu_confirm = {decrypted_conf.decode('utf-8')}
        print(f"\n\t[+] {manu_confirm}")


        # Convert set to list
        manu_confirm_list = list(manu_confirm)

        # add more json objects to the transaction set: {'{"shoe_model": "nike", "price": "10"}'}
        transaction_details = {"buyer_address": f"{buyer_addr}", "UTXO": f"{buyer_coin}"}
        manu_confirm_list.append(transaction_details)

        # convert the list to a json string
        transaction_details_json = json.dumps(manu_confirm_list)

        # Generate a new ECDSA key pair
        sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        vk = sk.get_verifying_key()

        # Save the private key to a file
        private_key_path = "buyerPriv/buyer_private_key.pem"
        with open(private_key_path, "wb") as f:
            f.write(sk.to_pem())

        # Save the public key to a file
        with open("buyer_public_key.pem", "wb") as f:
            f.write(vk.to_pem())

        # Sign the transaction data with the private key
        signature = sk.sign(transaction_details_json.encode())
        
        # Encode the signature in base64
        encoded_signature = base64.b64encode(signature)
        print(colorama.Fore.GREEN + "Transaction signed." + colorama.Style.RESET_ALL)

        # Combine the transaction details and signature into a single dictionary
        signed_transaction = {
            "transaction_details": manu_confirm_list,
            "signature": encoded_signature.decode()
        }

        # Convert the signed transaction to a JSON string
        signed_transaction_json = json.dumps(signed_transaction)

        # Save the JSON file
        with open('signed_transaction.json', 'w') as f:
            f.write(signed_transaction_json)

        # Send the signed transaction data over the socket to the manufacturer
        s.sendall(signed_transaction_json.encode())
        print(colorama.Fore.YELLOW + "Signed transaction propogated and awaiting verification ..." + colorama.Style.RESET_ALL)

        # # Close the connection
        # s.close()
        


