#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Builds a proper QR code from a ~/.google_authenticator file that can be
# scanned properly by a mobile phone.
#
# https://github.com/google/google-authenticator/wiki/Key-Uri-Format
#
'''
Files generated typically have the following structure:
G5QBC4WC42ID5TY6         # secret
"RATE_LIMIT 10 15        # n/a
" WINDOW_SIZE 5          # n/a
" TOTP_AUTH              # type
39081046                 # recovery codes ...
79232545
64524431
55543567
95315641
'''
from urllib.parse import urlencode, quote
import os
import sys
import base64
import subprocess

URL = "otpauth://{type}/{issuer}:{label}?secret={secret}"
# URL = "otpauth://{type}/{label}?secret={secret}"
OPTIONALS = {
    'issuer': None,
    'algorithm': None,
    'digits': None,
    'period': None
}


def read_file(input):
    """Reads input .google_authenticator file and extracts secret and type."""
    input_dict = {}
    with open(input, 'r') as f:
        i = 0
        for line in f:
            if i == 0:
                input_dict['secret'] = line
            elif 'TOTP' in line:
                input_dict['type'] = 'totp'
            elif 'HOTP' in line:
                input_dict['type'] = 'hotp'
            i = i + 1

    return input_dict


def create_qr_string(args, **kwargs):
    input_dict = read_file(args.input_file)
    raw_url = URL.format(
        type=input_dict['type'],
        issuer=args.issuer,
        label=args.user,
        secret=input_dict['secret']
    ).strip()
    usable_dict = {}
    for i in OPTIONALS:
        if args.__dict__.get(i, None):
            usable_dict[i] = args.__dict__[i]
        elif kwargs.get(i, None):
            usable_dict[i] = kwargs[i]
    if len(usable_dict) > 0:
        options = '&{0}'.format(urlencode(usable_dict))
    else:
        options = None
    final_url = f"{raw_url}{options if options else ''}"
    return final_url


def create_qr_code(string, output):
    params = ['qrencode', '-s', '6', '-m', '5', '-t', 'PNG', '-o', output, string]
    subprocess.call(params, shell=False)


if __name__ == '__main__':
    import argparse
    response = None

    parser = argparse.ArgumentParser(description='Commandline settings')

    parser.add_argument('-i', '--input-file', required=True, help='~/.google_authenticator file to process')
    parser.add_argument('-u', '--user', required=True,
                        help='username to add as the label')
    parser.add_argument('--issuer', required=True,
                        help='issuer to add as the label')
    parser.add_argument('-o', '--output-file', required=True,
                        help='output file')
    args = parser.parse_args()

    if not os.path.isfile(args.input_file):
        sys.exit('Error. Unable to find input file.')
    
    response = create_qr_string(args)

    print(response.strip('" \t\n'))  # remove ",{space},{tab},{newline}
    create_qr_code(response.strip('" \t\n'), args.output_file)