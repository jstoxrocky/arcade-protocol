from arcade_protocol.crypto import (
    sign_score,
    random_32bytes,
)


class Arcade():

    def __init__(self, contract, game, player):
        self.contract = contract
        self.player = player
        self.game = game

    @staticmethod
    def new_payment_code():
        payment_code = random_32bytes()
        return payment_code

    def confirm_payment(self, payment_code):
        error = self.contract.confirm_payment(
            self.game.id,
            self.player,
            payment_code,
        )
        return error

    def sign(self, key, score):
        vrs = sign_score(
            key,
            self.contract.address,
            self.game.id,
            self.player,
            score,
        )
        return vrs
