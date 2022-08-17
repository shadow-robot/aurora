#!/usr/bin/env python3

# Copyright 2022 Shadow Robot Company Ltd.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation version 2 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

from base64 import b64encode
from cryptography.fernet import Fernet
import argparse

def gather_args():
    description = 'Decode AWS Login for Docker Login.'
    parser = argparse.ArgumentParser(description=description)
    help = "This is the access key which needs to be decoded."
    parser.add_argument('--access_key', '-a', type=str, required=True, help=help)
    help = "This is the secret key which needs to be decoded."
    parser.add_argument('--secret_key', '-s', type=str, required=True, help=help)
    help = "This is the Customer Key."
    parser.add_argument('--customer_key', '-c', type=str, required=True, help=help)
    args = parser.parse_args()
    return args.access_key, args.secret_key, args.customer_key


def main():
    ak, sk, ck = gather_args()
    ck_encode = b64encode(ck.encode(encoding='UTF-8')[:32])
    cipher_suite = Fernet(ck_encode)
    decrypt_ak = cipher_suite.decrypt(ak.encode(encoding='UTF-8'))
    decrypt_sk = cipher_suite.decrypt(sk.encode(encoding='UTF-8'))
    decode_ak = decrypt_ak.decode(encoding="UTF-8")
    decode_sk = decrypt_sk.decode(encoding="UTF-8")
    details = {"access_key": decode_ak, "secret_key": decode_sk}
    print(details)


if __name__ == "__main__":
    main()
