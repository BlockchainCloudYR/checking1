from flask import Flask, render_template, jsonify, request, session
import asyncio
import websockets
import json
import threading
import requests
import subprocess
import os
from web3 import Web3
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal
import time
import datetime
from solders.keypair import Keypair
from solana.rpc.api import Client
import psycopg2
from bit import PrivateKeyTestnet
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
app.secret_key = 'yeah buddy'

# Your Infura Project ID
INFURA_PROJECT_ID = '38898b105ab04267a0acd987a4d82d9a'

# Set up Infura as the provider for Sepolia (Ethereum testnet)
infura_url_sepolia = f"https://sepolia.infura.io/v3/{INFURA_PROJECT_ID}"
web3_sepolia = Web3(Web3.HTTPProvider(infura_url_sepolia))
sep_chain_id = 11155111

# Set up Infura as the provider for Polygon using the provided URL
infura_url_polygon = f"https://polygon-amoy.infura.io/v3/{INFURA_PROJECT_ID}"
web3_polygon = Web3(Web3.HTTPProvider(infura_url_polygon))

# Set up Infura as the provider for Binance Smart Chain (BSC) Testnet
infura_url_bsc = f"https://bsc-testnet.infura.io/v3/{INFURA_PROJECT_ID}"
web3_bsc = Web3(Web3.HTTPProvider(infura_url_bsc))


# Ensure connection to Infura for each network
if not web3_sepolia.is_connected():
    raise Exception("Could not connect to Sepolia Infura")

if not web3_polygon.is_connected():
    raise Exception("Could not connect to Polygon Infura")

if not web3_bsc.is_connected():
    raise Exception("Could not connect to BSC Infura")

# BlockCypher API token
BLOCKCYPHER_API_TOKEN = 'a42a4321ffd140c080e35afe8c8c5bb4'

# SQLAlchemy configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test_owner:KFs7JlxGtmh5@ep-fragrant-rice-a4uz3q1a.us-east-1.aws.neon.tech/test?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wallet_name = db.Column(db.String(255), unique=True, nullable=False)
    eth_public_address = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    eth_private_address = db.Column(db.String(255), unique=True, nullable=False)
    wallet_created = db.Column(db.Boolean, default=False)
    solana_public_address = db.Column(db.String(255), nullable=False)
    solana_private_address = db.Column(db.String(255), nullable=False)
    bitcoin_public_address = db.Column(db.String(255), unique=True, nullable=False)
    bitcoin_private_address = db.Column(db.String(255), unique=True, nullable=False)
    

# Create tables when the application starts
with app.app_context():
    db.create_all()

# Global variables for real-time data on major cryptocurrencies
btc_price = btc_change = None
eth_price = eth_change = None
sol_price = sol_change = None
bnb_price = bnb_change = None
avax_price = avax_change = None
opt_price = opt_change = None
arb_price = arb_change = None
ftm_price = ftm_change = None
cfx_price = cfx_change = None
kava_price = kava_change = None
moon_price = moon_change = None



async def fetch_data():
    global bitcoin_price, bitcoin_price_change_percent
    global ethereum_price, ethereum_price_change_percent
    global solana_price, solana_price_change_percent
    global bnb_price, bnb_price_change_percent
    global avalanche_price, avalanche_price_change_percent
    global optimism_price, optimism_price_change_percent
    global arbitrum_price, arbitrum_price_change_percent
    global fantom_price, fantom_price_change_percent
    global conflux_price, conflux_price_change_percent
    global kava_price, kava_price_change_percent
    global moonbeam_price, moonbeam_price_change_percent


    # WebSocket endpoint for multiple tickers
    uri = "wss://stream.binance.com:9443/ws"
    subscribe_message = {
        "method": "SUBSCRIBE",
        "params": [
            "btcusdt@ticker",
            "ethusdt@ticker",
            "solusdt@ticker",
            "bnbusdt@ticker",
            "avaxusdt@ticker",
            "opusdt@ticker",
            "arbusdt@ticker",
            "ftmusdt@ticker",
            "cfxusdt@ticker",
            "kavausdt@ticker",
            "glmrusdt@ticker"
        ],
        "id": 1
    }

    while True:
        try:
            async with websockets.connect(uri) as websocket:
                await websocket.send(json.dumps(subscribe_message))
                while True:
                    try:
                        data = json.loads(await websocket.recv())
                        symbol = data.get('s', '').lower()


                        if symbol == 'btcusdt':
                            bitcoin_price = float(data.get('c', 0))
                            bitcoin_price_change_percent = data.get('P', 'N/A')

                        elif symbol == 'ethusdt':
                            ethereum_price = float(data.get('c', 0))
                            ethereum_price_change_percent = data.get('P', 'N/A')


                        elif symbol == 'solusdt':
                            solana_price = float(data.get('c', 0))
                            solana_price_change_percent = data.get('P', 'N/A')


                        elif symbol == 'bnbusdt':
                            bnb_price = float(data.get('c', 0))
                            bnb_price_change_percent = data.get('P', 'N/A')


                        elif symbol == 'avaxusdt':
                            avalanche_price = float(data.get('c', 0))
                            avalanche_price_change_percent = data.get('P', 'N/A')

                        elif symbol == 'opusdt':
                            optimism_price = float(data.get('c', 0))
                            optimism_price_change_percent = data.get('P', 'N/A')

                        elif symbol == 'arbusdt':
                            arbitrum_price = float(data.get('c', 0))
                            arbitrum_price_change_percent = data.get('P', 'N/A')

                        elif symbol == 'ftmusdt':
                            fantom_price = float(data.get('c', 0))
                            fantom_price_change_percent = data.get('P', 'N/A')

                        elif symbol == 'cfxusdt':
                            conflux_price = float(data.get('c', 0))
                            conflux_price_change_percent = data.get('P', 'N/A')

                        elif symbol == 'kavausdt':
                            kava_price = float(data.get('c', 0))
                            kava_price_change_percent = data.get('P', 'N/A')

                        elif symbol == 'glmrusdt':
                            moonbeam_price = float(data.get('c', 0))
                            moonbeam_price_change_percent = data.get('P', 'N/A')


                    except websockets.ConnectionClosed as e:
                        print(f"WebSocket connection closed with error: {e}")
                        break
                    except Exception as e:
                        print(f"Error receiving or processing data: {e}")

        except (websockets.ConnectionClosedError, websockets.InvalidStatusCode) as e:
            print(f"Error connecting to WebSocket: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        print("Reconnecting in 5 seconds...")
        await asyncio.sleep(5)




@app.route('/')
async def index():
    return render_template('index.html'
                           )

@app.route('/price')
def price():
    return jsonify({
        'price_btc': bitcoin_price,
        '24hr_change_btc': bitcoin_price_change_percent,
        'price_eth': ethereum_price,
        '24hr_change_eth': ethereum_price_change_percent,
        'price_sol': solana_price,
        '24hr_change_sol': solana_price_change_percent,
        'price_bnb': bnb_price,
        '24hr_change_bnb': bnb_price_change_percent,
        'price_avalanche': avalanche_price,
        '24hr_change_avalanche': avalanche_price_change_percent,
        'price_optimism': optimism_price,
        '24hr_change_optimism': optimism_price_change_percent,
        'price_arbitrum': arbitrum_price,
        '24hr_change_arbitrum': arbitrum_price_change_percent,
        'price_fantom': fantom_price,
        '24hr_change_fantom': fantom_price_change_percent,
        'price_conflux': conflux_price,
        '24hr_change_conflux': conflux_price_change_percent,
        'price_kava': kava_price,
        '24hr_change_kava': kava_price_change_percent,
        'price_moonbeam': moonbeam_price,
        '24hr_change_moonbeam': moonbeam_price_change_percent
    })


# Example API URL for CoinGecko
COIN_GECKO_API_URL = 'https://api.coingecko.com/api/v3/coins/'

# Helper function to get price data from CoinGecko
def fetch_coin_prices(coin_id):
    try:
        response = requests.get(f'{COIN_GECKO_API_URL}{coin_id}/market_chart', params={
            'vs_currency': 'usd',
            'days': '7'
        })
        data = response.json()
        prices = [
            {'date': datetime.utcfromtimestamp(price[0] / 1000), 'price': price[1]}
            for price in data['prices']
        ]
        return prices
    except Exception as e:
        print(f'Error fetching {coin_id} prices: {e}')
        return []



@app.route('/api/bitcoin-prices')
def bitcoin_prices():
    prices = fetch_coin_prices('bitcoin')
    return jsonify(prices)

@app.route('/api/ethereum-prices')
def ethereum_prices():
    prices = fetch_coin_prices('ethereum')
    return jsonify(prices)

@app.route('/api/solana-prices')
def solana_prices():
    prices = fetch_coin_prices('solana')
    return jsonify(prices)

@app.route('/api/bnb-prices')
def bnb_prices():
    prices = fetch_coin_prices('binancecoin')
    return jsonify(prices)

@app.route('/api/avax-prices')
def avax_prices():
    prices = fetch_coin_prices('avalanche-2')
    return jsonify(prices)

@app.route('/api/optimism-prices')
def optimism_prices():
    prices = fetch_coin_prices('optimism')
    return jsonify(prices)

@app.route('/api/arbitrum-prices')
def arbitrum_prices():
    prices = fetch_coin_prices('arbitrum')
    return jsonify(prices)

@app.route('/api/fantom-prices')
def fantom_prices():
    prices = fetch_coin_prices('fantom')
    return jsonify(prices)

@app.route('/api/conflux-prices')
def conflux_prices():
    prices = fetch_coin_prices('conflux-token')
    return jsonify(prices)

@app.route('/api/kava-prices')
def kava_prices():
    prices = fetch_coin_prices('kava')
    return jsonify(prices)

@app.route('/api/moonbeam-prices')
def moonbeam_prices():
    prices = fetch_coin_prices('moonbeam')
    return jsonify(prices)




def get_ist_time():
    """Returns the current time in IST (Indian Standard Time)"""
    utc_time = datetime.datetime.utcnow()
    ist_offset = datetime.timedelta(hours=5, minutes=30)
    ist_time = utc_time + ist_offset
    return ist_time.isoformat()  # Return in ISO format


@app.route('/account', methods=['GET', 'POST'])
def account():
    user_id = session.get('user_id')
    existing_wallet = User.query.filter_by(id=user_id).first() if user_id else None

    if request.method == 'POST':

        if 'check_balance' in request.form:
            address = request.form.get('address')
            network = request.form.get('network')

            if not address or not network:
                return render_template('account.html', error="Address and Network are required.")

            try:
                if network == 'sepolia':
                    web3 = web3_sepolia
                    unit = "sepoliaETH"
                    balance_wei = web3.eth.get_balance(address)
                    balance = Decimal(balance_wei) / Decimal(10 ** 18)

                elif network == 'polygon':
                    web3 = web3_polygon
                    balance_wei = web3.eth.get_balance(address)
                    balance = Decimal(balance_wei) / Decimal(10 ** 18)

                elif network == 'bsc':
                    web3 = web3_bsc
                    unit = "bsc"
                    balance_wei = web3.eth.get_balance(address)
                    balance = Decimal(balance_wei) / Decimal(10 ** 18)

                elif network == 'test3':
                    url = f"https://api.blockcypher.com/v1/btc/test3/addrs/{address}/balance"
                    params = {'token': BLOCKCYPHER_API_TOKEN}
                    response = requests.get(url, params=params)
                    response_data = response.json()

                    # Handle case when the API returns an error
                    if response.status_code != 200:
                        raise Exception(f"API Error: {response_data.get('error', 'Unknown error')}")

                    balance_satoshis = response_data.get('balance', 0)
                    balance = Decimal(balance_satoshis) / Decimal(10 ** 8)  # Convert from satoshis to BTC
                    unit = "tBTC"

                else:
                    return render_template('account.html', error="Invalid network selected.")

                # Log the address being queried
                print(f"Querying balance for address: {address} on {network}")

                # Log the balance
                print(f"Balance in {unit}: {balance}")

                # Return the balance
                return render_template('account.html', public_key=address, balance=balance, network=network, unit=unit)

            except Exception as e:
                # Log the exception message
                print(f"Exception occurred: {str(e)}")
                return render_template('account.html', error=f"Error retrieving balance: {str(e)}")

        else:
            if existing_wallet:
                print(f"Existing wallet public address: {existing_wallet.eth_public_address}")  # Debug print
                return jsonify({"error": "A wallet already exists. You cannot create another wallet."}), 400

            wallet_name = request.form.get('wallet-name')
            password = request.form.get('wallet-password')

            if not wallet_name or not password:
                return jsonify({"error": "Wallet name and password are required"}), 400

            # Connect to Infura
            infura_url = 'https://sepolia.infura.io/v3/38898b105ab04267a0acd987a4d82d9a'  # Replace with your Infura project ID
            web3 = Web3(Web3.HTTPProvider(infura_url))

            # Check connection
            if not web3.is_connected():
                return jsonify({"error": "Failed to connect to Infura"}), 500

            # Create a new Ethereum wallet
            account = web3.eth.account.create()

            # Output the wallet details
            eth_public_address = account.address
            eth_private_address = account._private_key.hex()

            print("Address:", eth_public_address)
            print("Private Key:", eth_private_address)

		    # Solana Wallet Creation (using solders)
            try:
                solana_testnet_url = "https://api.testnet.solana.com"
                client = Client(solana_testnet_url)
                keypair = Keypair()

                # Correct method to get the public key
                print("Solana Testnet Address:", keypair.pubkey())
                print("Private Key:", keypair.secret())  # You may want to store this securely

                solana_public_address = keypair.pubkey()
                solana_private_address = keypair.secret()

            except Exception as e:
                return jsonify({"error": f"Solana wallet generation failed: {str(e)}"}), 500
        

            try:
                # Generate a new Bitcoin testnet address
                key = PrivateKeyTestnet()
                print("Bitcoin Testnet Address:", key.address)
                print("Private Key:", key.to_wif())  # Export private key
                bitcoin_public_address = key.address
                bitcoin_private_address = key.to_wif()

            except Exception as e:
                return jsonify({"error": f"Bitcoin address generation failed: {str(e)}"}), 500

            # Store the wallet details in the database
            try:
                print(f"Creating user: {wallet_name}, {eth_public_address}, {eth_private_address}, {solana_public_address}, {solana_private_address}, {bitcoin_public_address}, {bitcoin_private_address}")
                new_user = User(
                    wallet_name=wallet_name,
                    eth_public_address=eth_public_address,
                    eth_private_address = eth_private_address,
                    password_hash=password,
                    wallet_created=True,
                    solana_public_address=str(solana_public_address),
                    solana_private_address = solana_private_address,
                    bitcoin_public_address=bitcoin_public_address,
                    bitcoin_private_address = bitcoin_private_address
                )
                db.session.add(new_user)
                db.session.commit()
                print(
                    f"Ethereum Wallet created: {eth_public_address}, Solana Wallet created: {solana_public_address}, Bitcoin Wallet created: {bitcoin_public_address}")  # Debug print
                # Store the public address in the session
                session['eth_public_address'] = eth_public_address
                session['solana_public_address'] = str(solana_public_address)
                session['bitcoin_public_address'] = bitcoin_public_address

            except SQLAlchemyError as e:
                return jsonify({"error": f"Database error: {e}"}), 500
                db.session.rollback()

            # Return a valid response after wallet creation
            return render_template('account.html', public_key=eth_public_address, solana_public_address=solana_public_address,bitcoin_public_address=bitcoin_public_address,
                                   wallet_created=True)
        

    # Handle GET requests or after POST
    eth_public_address = session.get('eth_public_address') or (existing_wallet.eth_public_address if existing_wallet else None)
    return render_template('account.html', public_key=eth_public_address, wallet_created=bool(existing_wallet), balance=None)



@app.route('/send', methods=['GET'])
def send():

    return render_template('send.html')


@app.route('/send_transaction', methods=['POST'])
def send_transaction():
    try:
        recipient_address = request.form['recipient']
        amount_in_eth = float(request.form['amount'])

        # Get the sender's account (private key)
        sender_address = '0x611bE7CEf487408a25037E90cd4cde57D4D3Cd38'  # Replace with your sender address
        private_key = '1a91a1ac7d03d29cd1b7fd05906796a75fe8e076f8c0f93f32999a8c789f53ba'  # Replace with your private key

        # Ensure the inputs are valid
        if not recipient_address or not amount_in_eth:
            return jsonify({"error": "Missing Ethereum address or amount"}), 400

        # Get nonce (number of transactions from this address)
        nonce = web3_sepolia.eth.get_transaction_count(sender_address)

        tx = {
            'to': recipient_address,
            'value': Web3.to_wei(amount_in_eth, 'ether'),
            'gas': 21000,
            'gasPrice': web3_sepolia.eth.gas_price,
            'nonce': nonce,
            'chainId': 11155111
        }

        # Sign the transaction
        signed_tx = web3_sepolia.eth.account.sign_transaction(tx, private_key)

        # Send the transaction
        tx_hash = web3_sepolia.eth.send_raw_transaction(signed_tx.raw_transaction)

        return tx_hash.hex()

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_public_key_from_session(coin_type):
    # Retrieve the public key from the session based on the coin type
    if coin_type in ['ethereum (eth)', 'binance coin (bnb)', 'avalanche (avax)', 'optimism (opm)', 'arbitrum (arb)', 'fantom (ftm)', 'conflux (cfx)', 'kava (kava)', 'moonbeam (glmr)']:
        return session.get('eth_public_address')
    elif coin_type == 'solana (sol)':
        return session.get('solana_public_address')
    elif coin_type == 'bitcoin (btc)':
        return session.get('bitcoin_public_address')
    
    return None

@app.route('/receive', methods=['GET'])
def receive():
    coin_type = request.args.get('coin_type', '').lower()
    public_key = get_public_key_from_session(coin_type)
    qr_code_url = f'https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={public_key}' if public_key else None

    # Determine explorer URL based on coin type
    if coin_type == 'ethereum (eth)':
        explorer_url = f'https://etherscan.io/address/{public_key}'
    elif coin_type == 'bitcoin (btc)':
        explorer_url = f'https://mempool.space/testnet/address/{public_key}'
    elif coin_type == 'solana (sol)':
        explorer_url = f'https://solscan.io/account/{public_key}?cluster=testnet'
    elif coin_type == 'binance coin (bnb)':
        explorer_url = f'https://testnet.bscscan.com/address/{public_key}'
    elif coin_type == 'avalanche (avax)':
        explorer_url = f'https://testnet.avascan.info/blockchain/all/address/{public_key}'
    elif coin_type == 'optimism (opm)':
        explorer_url = f'https://sepolia-optimism.etherscan.io/address/{public_key}'
    elif coin_type == 'arbitrum (arb)':
        explorer_url = f'https://sepolia.arbiscan.io/address/{public_key}'
    elif coin_type == 'fantom (ftm)':
        explorer_url = f'https://testnet.ftmscan.com/address/{public_key}'
    elif coin_type == 'conflux (cfx)':
        explorer_url = f'https://evmtestnet.confluxscan.net/address/{public_key}'
    elif coin_type == 'kava (kava)':
        explorer_url = f'https://testnet.kavascan.com/address/{public_key}'
    elif coin_type == 'moonbeam (glmr)':
        explorer_url = f'https://moonbase.moonscan.io/address/{public_key}'
    else:
        explorer_url = '#'  # Default or error page if coin_type is not supported

    return render_template('receive.html', public_key=public_key, qr_code_url=qr_code_url, coin_type=coin_type, explorer_url=explorer_url)






def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(fetch_data())



if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    t = threading.Thread(target=start_background_loop, args=(loop,))
    t.start()
    app.run(host='0.0.0.0', port=5000,debug=True)
