#!/usr/bin/env python3

import argparse
import os
import subprocess

parser = argparse.ArgumentParser(description='Crate overrides manager')
parser.add_argument('command', choices=['checkout', 'update'], help='checkout or update')
parser.add_argument('config_file', help='configuration file')
parser.add_argument('build_dir', help='build directory')
args = parser.parse_args()

build_dir = os.path.realpath(args.build_dir)
config_file = os.path.realpath(args.config_file)
os.makedirs(build_dir, exist_ok=True)

crates = {}
with open(config_file, 'r') as f:
    for line in f.readlines():
        name, url, hash = line.split()
        crates[name] = (url, hash)

if args.command == 'checkout':
    for name, (url, hash) in crates.items():
        path = os.path.join(build_dir, name)
        if not os.path.exists(path):
            subprocess.check_call(['git', 'clone', url, path])
        os.chdir(path)
        subprocess.check_call(['git', 'reset', '--hard'])
        subprocess.check_call(['git', 'checkout', hash])
elif args.command == 'update':
    updated = False
    for name, (url, hash) in crates.items():
        path = os.path.join(build_dir, name)
        if os.path.exists(path):
            os.chdir(path)
            subprocess.check_call(['git', 'reset', '--hard'])
            subprocess.check_call(['git', 'fetch', 'origin'])
            branch = 'pending' if name == 'examples' else 'master'
            subprocess.check_call(['git', 'checkout', 'origin/{}'.format(branch)])
            new_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD'],
                    universal_newlines=True).strip()
            if new_hash != hash:
                updated = True
                crates[name] = (url, new_hash)
    if updated:
        lines = []
        for name, (url, hash) in crates.items():
            lines.append('{} {} {}\n'.format(name, url, hash))
        lines.sort()
        with open(config_file, 'w') as f:
            for line in lines:
                f.write(line)
