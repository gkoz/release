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

has_changed_something = False
for path in manifests():
	manifest = open(os.path.join(path, CARGO_TOML), 'r')
	has_change_something = False
	with open(os.path.join(path, CARGO_TOML_NEW), 'w') as new_manifest:
		for line in manifest:
			if re_git_or_path.match(line):
				has_change_something = True
				continue
			new_manifest.write(line)
		if has_change_something:
			print("Updating '%s'" % os.path.join(path, CARGO_TOML))
			has_changed_something = True
	manifest.close()
	if has_change_something:
		os.remove(os.path.join(path, CARGO_TOML))
		os.rename(
			os.path.join(path, CARGO_TOML_NEW),
			os.path.join(path, CARGO_TOML))
	else:
		os.remove(os.path.join(path, CARGO_TOML_NEW))
if not has_changed_something:
	print("Everything was already up-to-date")
