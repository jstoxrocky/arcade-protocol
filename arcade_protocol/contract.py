from web3 import (
    Web3,
)
from hexbytes import (
    HexBytes,
)


class Base():

    def __init__(self, provider):
        self.web3 = Web3(provider)

    def options(self, from_addr):
        # eth gas station fast price in gwei 01/10/2020
        recommended_gas_price_gwei = 8
        recommended_gas_price = Web3.toWei(recommended_gas_price_gwei, 'gwei')
        options = {
            'gas': 3000000,
            'gasPrice': recommended_gas_price,
            'nonce': self.web3.eth.getTransactionCount(from_addr.address),
            'from': from_addr.address,
        }
        return options

    def send_raw_transaction(self, function_call, options, from_addr):
        unsigned_tx = function_call.buildTransaction(options)
        signed_tx = self.web3.eth.account.sign_transaction(
            unsigned_tx,
            from_addr.key,
        )
        tx_hash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print('transaction hash:', tx_hash.hex())
        receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        transaction = self.web3.eth.getTransaction(tx_hash)
        return {**receipt, 'gasPrice': transaction['gasPrice']}


class Deployer(Base):

    def __init__(self, provider):
        super().__init__(provider)

    def deploy(self, abi, bytecode, from_addr):
        contract = self.web3.eth.contract(abi=abi, bytecode=bytecode)
        function_call = contract.constructor()
        options = self.options(from_addr)
        receipt = self.send_raw_transaction(function_call, options, from_addr)
        return receipt


class Contract(Base):

    def __init__(self, provider, address, abi):
        super().__init__(provider)
        self.contract = self.web3.eth.contract(address, abi=abi)
        self.address = address

    def set_contract(self, abi, address):
        self.contract = self.web3.eth.contract(abi=abi, address=address)

    def get_price(self, game_id):
        price = self.contract.functions.getPrice(game_id).call()
        return price

    def get_highscore(self, game_id):
        highscore = self.contract.functions.getHighscore(game_id).call()
        return highscore

    def get_jackpot(self, game_id):
        jackpot = self.contract.functions.getJackpot(game_id).call()
        return jackpot

    def get_owner(self, game_id):
        owner = self.contract.functions.getOwner(game_id).call()
        return owner

    def get_percent_fee(self, game_id):
        percent_fee = self.contract.functions.getPercentFee(game_id).call()
        return percent_fee

    def get_payment_code(self, game_id, user):
        bytes_payment_code = self.contract.functions.getPaymentCode(
            game_id,
            user,
        ).call()
        payment_code = HexBytes(bytes_payment_code).hex()
        return payment_code

    def add_game(self, game_id, price, percent_fee, from_addr):
        function_call = self.contract.functions.addGame(
            game_id,
            price,
            percent_fee,
        )
        options = self.options(from_addr)
        receipt = self.send_raw_transaction(function_call, options, from_addr)
        return receipt

    def pay(self, game_id, payment_code, value, from_addr):
        function_call = self.contract.functions.pay(game_id, payment_code)
        options = {**self.options(from_addr), 'value': value}
        receipt = self.send_raw_transaction(function_call, options, from_addr)
        return receipt

    def claim_highscore(self, game_id, score, vrs, from_addr):
        function_call = self.contract.functions.claimHighscore(
            game_id,
            score,
            *vrs,
        )
        options = self.options(from_addr)
        receipt = self.send_raw_transaction(function_call, options, from_addr)
        return receipt
