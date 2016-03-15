#!/usr/bin/env python3

# Remove any 'git = ...' and 'path = ...' lines from all Cargo.tomls

import json
import os
import re
import urllib.request

CARGO_TOML = 'Cargo.toml'
CARGO_TOML_NEW = 'Cargo.toml.new'

def manifests():
	for path, _, names in os.walk('.'):
		if CARGO_TOML in names:
			yield path

re_git_or_path = re.compile('^\s*(git|path)\s*=.*$')

for path in manifests():
	manifest = open(os.path.join(path, CARGO_TOML), 'r')
	with open(os.path.join(path, CARGO_TOML_NEW), 'w') as new_manifest:
		for line in manifest:
			if re_git_or_path.match(line):
				continue
			new_manifest.write(line)
	manifest.close()
	os.remove(os.path.join(path, CARGO_TOML))
	os.rename(
		os.path.join(path, CARGO_TOML_NEW),
		os.path.join(path, CARGO_TOML))
