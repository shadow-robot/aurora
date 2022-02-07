#!/usr/bin/env python3
import sys
import requests
import argparse
import json

POLHEMUS_BIN="https://5bo8nfkjk0.execute-api.eu-west-2.amazonaws.com/prod"
HAPTX_BIN="https://5hmltg5th3.execute-api.eu-west-2.amazonaws.com/prod"
DEVELOPMENT="https://wogk2adb24.execute-api.eu-west-2.amazonaws.com/prod"


def gather_customer_key():
    description = 'This script is used to gather the Access Key and Secret Key.'
    parser = argparse.ArgumentParser(description=description)
    help = "This is the CustomerKey that will be used in the API call."
    parser.add_argument('--customerkey', '-ck', type=str, required=True, help=help)
    help = "This is the image to be pulled."
    parser.add_argument('--image', '-i', type=str, required=True, help=help)
    args = parser.parse_args()
    return args.customerkey, args.image


def get_api_response(api_call, key):
    r = requests.get(api_call, headers={'x-api-key':key})
    if r.ok == False:
        sys.stderr.write("You do not have the rights to access this image.")
        exit(1)
    response_json = r.json()
    ak = response_json['body']['access_key']
    sk = response_json['body']['secret_key']
    return (ak, sk)
    

def main():
    customer_key, image = gather_customer_key()
    if "binary" in image and "haptx" in image:
        ak, sk = get_api_response(HAPTX_BIN, customer_key)
    elif "binary" in image and "polhemus" in image:
        ak, sk = get_api_response(POLHEMUS_BIN, customer_key)
    else:
        ak, sk = get_api_response(DEVELOPMENT, customer_key)
    data = {
        "access_key": ak,
        "secret_key": sk
    }
    sys.stdout.write(json.dumps(data))

if __name__ == "__main__":
    main()