import base64
import hashlib
import math
import requests
import time

def num_to_bytes(n):
    """
    Credits: https://stackoverflow.com/a/51446863
    """
    num_bytes = int(math.ceil(n.bit_length() / 8))
    n_bytes = n.to_bytes(num_bytes, byteorder='big')
    return n_bytes

def mine_coin(hash_of_preceding_coin, id_of_miner, offset=0):
    coin_blob_ctr = offset
    while True:
        m = hashlib.md5()
        m.update(b"CPEN 442 Coin")
        m.update(b"2019")
        m.update(hash_of_preceding_coin)
        coin_blob = num_to_bytes(coin_blob_ctr)
        m.update(coin_blob)
        m.update(id_of_miner)
        cpen442coin = m.hexdigest()
        if cpen442coin.startswith("00000000"):
            return cpen442coin, coin_blob_ctr, coin_blob, str(base64.b64encode(coin_blob), "utf-8")
        coin_blob_ctr += 1

def verify_coin_blob(coin_blob, id_of_miner):
    data = {
        "coin_blob": coin_blob,
        "id_of_miner": id_of_miner,        
    }
    return requests.post("http://cpen442coin.ece.ubc.ca/verify_example_coin", json=data)

def claim_coin_blob(coin_blob, id_of_miner):
    data = {
        "coin_blob": coin_blob,
        "id_of_miner": id_of_miner,        
    }
    return requests.post("http://cpen442coin.ece.ubc.ca/claim_coin", json=data)

def mine(hash_of_preceding_coin, id_of_miner, offset=0):
    start = time.time()
    cpen442coin, mined_coin_blob_ctr, _, mined_coin_blob_b64 = mine_coin(hash_of_preceding_coin, id_of_miner, offset)
    end = time.time()
    elapsed = end - start
    print("Found coin: %s in %.2f seconds\nCoin blob (numeric): %s\nCoin blob (b64): %s\n" % (cpen442coin, elapsed, mined_coin_blob_ctr, mined_coin_blob_b64))

    resp = claim_coin_blob(mined_coin_blob_b64, id_of_miner.decode()) # don't forget to decode into str here
    if resp.status_code != 200 or "success" not in resp.json():
        print("Mined coin claiming failed.")

    resp = verify_coin_blob(mined_coin_blob_b64, id_of_miner.decode())
    if resp.status_code != 200 or "success" not in resp.json():
        print("Mined coin failed verification.")

    print("Done.")
    return True
