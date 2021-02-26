#Initial Imports
import subprocess
import json
import os
import bit

from constants import *

from bit import wif_to_key
from bit import PrivateKeyTestnet
from web3 import Web3
from eth_account import Account
from web3.middleware import geth_poa_middleware

#Connecting to local server
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

#Storing mnemonic phrase
mnemonic = os.getenv('MNEMONIC')

#Function to derive addresses and keys from mnemonic
def derive_wallets(password, coin):
    
    command = f'php hd-wallet-derive.php -g --mnemonic="{password}" --cols=path,address,privkey,pubkey --coin={coin} --numderive=3 --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output,err = p.communicate()
    p_status = p.wait()
    keys = json.loads(output)
    
    return keys

#Creating a dictionary of these addresses/keys for each coin
coins = {}
coins["ETH"] = derive_wallets(mnemonic, ETH)
coins["BTCTEST"] = derive_wallets(mnemonic, BTCTEST)

print(coins)


#Function to fetch account from private key
def priv_key_to_account(coin, priv_key):
    
    if coin == 'eth':
        
        return Account.privateKeyToAccount(priv_key)
    
    elif coin == "btc-test":
        
        return bit.PrivateKeyTestnet(priv_key)

#Function to create raw transaction to be passed to be signed and sent
def create_tx(coin, account, to, amount):
    
    if coin == 'eth':
        
        gasEstimate = w3.eth.estimateGas({'from': account.address, 
                       'to': to, 'value': amount})
        
        transaction = {'nonce': w3.eth.getTransactionCount(account.address), 
                       'gasPrice': w3.eth.gasPrice, 
                       'gas': gasEstimate,
                       'to':to, 
                       'from': account.address, 
                       'value':amount}
        
        return transaction
        
    elif coin == "btc-test":
        
        transaction = bit.PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])
        
        return transaction

#Function to sign and send raw transaction to the network
def send_tx(coin, account, to, amount, priv_key):

        if coin == 'eth':
            
            raw_tx = create_tx(coin, account, to, amount)
            signed_tx = w3.eth.account.sign_transaction(raw_tx, priv_key)
            
            return w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        
        elif coin == "btc-test":
            
            raw_tx = create_tx(coin, account, to, amount)
            signed_tx = account.sign_transaction(raw_tx)
            
            return bit.network.NetworkAPI.broadcast_tx_testnet(signed_tx)

            


    
