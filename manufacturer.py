import socket
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import ecdsa
import base64
import mysql.connector
import json
import colorama
import os
import pyfiglet

title = pyfiglet.figlet_format("Manufacturer")
print(title)

# Status to check whether shoe model is in db (1)
status = 0

# Initialize colorama
colorama.init()

class Transaction_to_buyer:
    def __init__(self, shoe_model, price):
        self.shoe_model = shoe_model
        self.price = price
        
    def __str__(self):
        return f"Transaction(shoe_model={self.shoe_model}, price={self.price})"


# Get the database credentials from environment variables
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME')

# Open a connection to the database
mydb = mysql.connector.connect(
  host=DB_HOST,
  port=DB_PORT,
  user=DB_USER,
  password=DB_PASSWORD,
  database=DB_NAME
)

# Set up AES encryption key and initialization vector (IV)
key = b'Sixteen byte key'
iv = b'InitializationVe'

# Set up socket for listening for incoming connections
HOST = '127.0.0.1'
PORT = 65432
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("Manufacturer is now listening for incoming connections at " + colorama.Fore.YELLOW + f"{HOST}:{PORT}..." + colorama.Style.RESET_ALL)
    conn, addr = s.accept()
    with conn:
        print(colorama.Fore.GREEN + f"Connected by {addr}" + colorama.Style.RESET_ALL)
        while True:
            # Receive transaction_request from buyer
            
            try:
                transaction_request = conn.recv(1024)
            # do something with the received data
            except socket.error as e:
                print(f"Socket error: {str(e)}")
                # do something to handle the error
            except Exception as e:
                print(f"Error: {str(e)}")
                # do something to handle the error
            if not transaction_request:
                break

            # Decrypt received reansaction request using AES
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted_req = unpad(cipher.decrypt(transaction_request), AES.block_size)
            # Process received request
            print(colorama.Fore.CYAN + f"\nReceived transaction request from Buyer: " + colorama.Style.RESET_ALL)
            print(f"\n\t[+] {decrypted_req.decode('utf-8')}\n")

            # Encrypt and send acknowledgement to buyer
            response = "Transaction request received and is being processed.\n".encode('utf-8')
            cipher = AES.new(key, AES.MODE_CBC, iv)
            encrypted_response = cipher.encrypt(pad(response, AES.block_size))
            conn.sendall(encrypted_response)

            # Receive transaction details from Buyer
            model = conn.recv(1024)
            # Decrypt transaction details from Buyer
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted_model = unpad(cipher.decrypt(model), AES.block_size)
            print(colorama.Fore.CYAN + f"Received Buyer's request for model: " + colorama.Style.RESET_ALL)
            model_requested = decrypted_model.decode('utf-8')
            print(f"\n\t[+] {model_requested}")

            # create cursor object to execute queries
            mycursor = mydb.cursor()

            # Query the database for the buyer's name
            mycursor.execute("SELECT * FROM `shoe` WHERE Model=%s", (model_requested,))

            # Fetch the results of the query
            result = mycursor.fetchall()
            # result = [(2, 'adidas', 20)], need to split into 3 elements
            res_id, res_model, res_px = result[0]

            # Check if the requested model was found in the database
            if len(result) != 0:
                status = 1
                msg = f"\n{model_requested} is available."
                print(colorama.Fore.GREEN + msg + colorama.Style.RESET_ALL)
                # create a new transaction to buyer
                transaction_send_to_buyer = Transaction_to_buyer(shoe_model=f"{res_model}", price=f"{res_px}")
                # convert to JSON string
                transaction_json = json.dumps(transaction_send_to_buyer.__dict__)
            else:
                msg = f"\n{model_requested} is not available."
                print(colorama.Fore.RED + msg + colorama.Style.RESET_ALL)
                break
    
            # Close the database connection
            mycursor.close()
            mydb.close()

            if status == 1:
                # Encrypt and send confirmation to buyer
                confirmation = f"Transaction processed for model: {decrypted_model.decode('utf-8')}."
                cipher = AES.new(key, AES.MODE_CBC, iv)
                encrypted_transaction_confirmation = cipher.encrypt(pad(transaction_json.encode('utf-8'), AES.block_size))
                conn.sendall(encrypted_transaction_confirmation)
            else:
                break

            # Accept a connection and receive the .pem bytes
            pem_bytes = conn.recv(1024)

            # Save the .pem bytes to a file
            with open("received_pubkey.pem", "wb") as f:
                f.write(pem_bytes)

            # load the signed transaction from the socket
            signed_transaction_json = conn.recv(1024)

            # Load the buyer's public key from the file
            with open('received_pubkey.pem', 'rb') as f:
                vk_pem = f.read()

            # Create a new verifying key object from the public key
            vk = ecdsa.VerifyingKey.from_pem(vk_pem)

            # Load the signed transaction data as a JSON string
            signed_transaction = json.loads(signed_transaction_json.decode())

            # Extract the transaction details and signature from the signed transaction
            transaction_details = signed_transaction['transaction_details']
            encoded_signature = signed_transaction['signature']

            # Decode the signature from base64
            signature = base64.b64decode(encoded_signature.encode())

            # Convert the transaction details dictionary to a JSON string
            transaction_details_json = json.dumps(transaction_details)

            # Verify the signature using the buyer's public key
            if vk.verify(signature, transaction_details_json.encode()):
                print(colorama.Fore.GREEN + "\nTransaction verified successfully." + colorama.Style.RESET_ALL)
            else:
                print(colorama.Fore.RED + "\n[!] Transaction discarded." + colorama.Style.RESET_ALL)

            # Close the connection
            conn.close()
            s.close()
