#  SneakSecure

![photo_2023-03-21_14-54-15](https://user-images.githubusercontent.com/59412437/228034201-d5a43bee-b9e8-4aa2-9c0f-5acb27705e6a.jpg)


SneakSecure is a proof-of-concept blockchain project that aims to provide secure and private transactions through the use of  cryptography and decentralization.
> **Note:** This is an assignment project for  **ICT 2205 Applied Cryptography** 

> Singapore Institute of Technology Bachelor of Engineering with Honours in Information and Communications Technology majoring in Information Security
##  Installation

FraudFence can be installed locally by following these steps:
1.  Clone the repository to your local machine.
``` git clone https://github.com/Brockkoli/SneakSecure-Blockchain.git```
2.   Install the required dependencies listed in `requirements.txt`.

   ``` cd SneakSecure-Blockchain```

   ```pip install -r requirements.txt```

3.  Run `python manufacturer.py` to start the listening for transaction requests.
4.  Run `python buyer.py` to start transaction.
5.  Run `python miner.py` to mine block

## Features

-   SQL database for buyer, manufacturer and shoes.
-   Encryption of communications channel using Advanced Encryption Standard (AES)
-   Generation of Elliptic Curve Digital Signature Algorithm (ECDSA) key pair  
-   Public key distribution 
-   Private key storage management using the Password-Based Encryption Scheme 2 (PBES2)
-   Consensus Algorithm - Proof of Work (PoW)
  - based on difficulty level: no. of leading 0s  

### Figures
- Communication process between manufacturer and buyer:
![socket_com](https://user-images.githubusercontent.com/59412437/228035697-b38e257a-2faa-42c3-bce1-ec71fdbd4783.png)

- Simplified flowchart:

![flowchart](https://user-images.githubusercontent.com/59412437/228035946-65630182-d1ee-4684-ad82-f4e7d28d1cbc.png)

- manufacturer.py and buyer.py:
![ss1](https://user-images.githubusercontent.com/59412437/228036619-4e27e326-ff8e-4855-9fba-289b84bdb27d.png)

- miner.py:

![menu](https://user-images.githubusercontent.com/59412437/228036691-a0f1abcc-cef8-4eb8-81e8-4d9570db54c0.png)

- Mining of block: 

![mining of block](https://user-images.githubusercontent.com/59412437/228036752-a9fcc56e-cd01-4e14-bbd0-2023b4ffcda3.png)

- View blockchain:
![view bc](https://user-images.githubusercontent.com/59412437/228036805-2c4e22ce-cbb9-4995-95ad-2c15a2ca02b5.png)

- TCP packet capture of transaction in Wireshark:
![tcp](https://user-images.githubusercontent.com/59412437/228037071-8bb69063-5705-4b04-a50b-93bbfd6abfe4.png)
  - All transactions must be visible to everyone in the network to ensure that the blockchain remains decentralized and secure. This transparency also helps to prevent fraud and corruption by allowing all participants to see the details of all transactions. 
  - However, while transaction details are visible to all publicly, the buyer can remain anonymous as only their blockchain address is included in the transaction. This feature helps to ensure the privacy of the buyer while still allowing for transparency and accountability in the blockchain.

- Transaction carried out and coins value updated in SQL database:
![sql](https://user-images.githubusercontent.com/59412437/228037381-f92f88f1-b12d-442e-861c-324cf2ceba4a.png) 

- View blockchain in csv file:
![csv](https://user-images.githubusercontent.com/59412437/228037559-d59fbab6-039b-4787-a737-2357e762019a.png)

