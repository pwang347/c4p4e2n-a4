import miner
import requests
import time

from multiprocessing import Event, Process

miner_id = b"a99e8327258aec476f8434b78c9242e8"
hash_of_preceding_coin = b"2e3a8e88a060cedcd9ac7b74fadd58e0"
num_workers = 3
offset_amt = 7729510772
jobs = []
event = Event()

def get_last_coin():
    resp = requests.get("http://cpen442coin.ece.ubc.ca/last_coin")
    if resp.status_code != 200 or "coin_id" not in resp.json():
        raise Exception("Couldn't get last coin")
    return resp.json()["coin_id"].encode()

def f(event, i):
    res = miner.mine(hash_of_preceding_coin, miner_id, i*offset_amt)
    event.set()
    print("event set")

def create_workers(hash_of_preceding_coin, miner_id):
    print("Creating workers")
    for i in range(num_workers):
        p = Process(
            target=f,
            args=(event, i,))
        p.start()
        jobs.append(p)

def terminate_workers():
    print("Terminating workers")
    for p in jobs:
        p.terminate()
    jobs.clear()

dont_switch_preceding_hash = True

if dont_switch_preceding_hash:
    print("Using %s" % hash_of_preceding_coin)
    create_workers(hash_of_preceding_coin, miner_id)

while True:
    if event.is_set():
        terminate_workers()
        print("Quitting")
        break
    if not dont_switch_preceding_hash:
        new_hash_of_preceding_coin = get_last_coin()
        if new_hash_of_preceding_coin != hash_of_preceding_coin:
            hash_of_preceding_coin = new_hash_of_preceding_coin
            print("Head changed: %s" % hash_of_preceding_coin)
            terminate_workers()
            create_workers(hash_of_preceding_coin, miner_id)
    time.sleep(60)
