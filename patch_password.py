import argparse
import hashlib

parser = argparse.ArgumentParser(description='Patch a password within a program')
parser.add_argument("--program", default="24407158.program2.exe", help="The program to patch")
parser.add_argument("--address", type=int, default=0x1e003, help="The address to modify")
parser.add_argument("--hash-fn", default="sha1", help="The hashlib module to use")
parser.add_argument("password", help="The password to add")

args = parser.parse_args()

def replace_password(new_pwd):
    """
    Generates a hash from the password and inserts it into the specified
    program and address.
    """
    s = getattr(hashlib, args.hash_fn)()
    s.update(new_pwd.encode())
    new_pwd_hash = s.digest()
    replace_len = len(new_pwd_hash)
    with open(args.program, "r+b") as f:
        program_bytes = bytearray(f.read())
        print(program_bytes[args.address:args.address+replace_len].hex())
        for idx in range(replace_len):
            program_bytes[idx+args.address] = new_pwd_hash[idx]
        print(program_bytes[args.address:args.address+replace_len].hex())
        f.seek(0)
        f.write(program_bytes)
        f.truncate()
        print("Saved to %s" % args.program)

replace_password(args.password)
