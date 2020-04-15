GAME_ID = '0x240e634ba82fa510c7e25243cc95d456bb1b6c11ef8c695ddd555eb5cd443f74'
PRICE = 100000000000000  # 0.0001 ETH


def test_add_game_success(contract, owner):
    receipt = contract.add_game(GAME_ID, PRICE, from_addr=owner)
    assert receipt['status'] == 1


def test_game_id_already_taken(contract, owner):
    receipt = contract.add_game(GAME_ID, PRICE, from_addr=owner)
    assert receipt['status'] == 1
    receipt = contract.add_game(GAME_ID, PRICE, from_addr=owner)
    assert receipt['status'] == 0


def test_free_game(contract, owner):
    price = 0
    receipt = contract.add_game(GAME_ID, price, from_addr=owner)
    assert receipt['status'] == 0
