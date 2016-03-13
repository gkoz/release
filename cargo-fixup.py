#!/usr/bin/env python3

import os
import re

CARGO_TOML = 'Cargo.toml'
CARGO_TOML_NEW = 'Cargo.toml.new'

def manifests():
	for path, _, names in os.walk('.'):
		if CARGO_TOML in names:
			yield path

crates = {}
re_group = re.compile('^\s*\[(.*)\]\s*$')
re_name = re.compile('^\s*name\s*=\s*"(.*)"\s*$')
re_crate = re.compile('^\s*([a-z0-9_-]+)\s*=\s*"(.*)"\s*$')

for path in manifests():
	manifest = open(os.path.join(path, CARGO_TOML), 'r')
	group = None
	for line in manifest:
		match = re_group.match(line)
		if match:
			group = match.group(1)
			continue
		if group != 'package':
			continue
		match = re_name.match(line)
		if match:
			crates[match.group(1)] = path

for path in crates.values():
	manifest = open(os.path.join(path, CARGO_TOML), 'r')
	with open(os.path.join(path, CARGO_TOML_NEW), 'w') as new_manifest:
			group = None
			for line in manifest:
				match = re_group.match(line)
				if match:
					group = match.group(1)
				if group == 'dependencies':
					match = re_crate.match(line)
					if match and match.group(1) in crates:
						name = match.group(1)
						ver = match.group(2)
						rel_path = os.path.relpath(crates[name], path) \
										.replace(os.path.sep, '/')
						new_manifest.write(
							'%s = { version = "%s", path = "%s" }\n' % (
								name,
								ver,
								rel_path
							))
						continue
				new_manifest.write(line)
	manifest.close()
	os.remove(os.path.join(path, CARGO_TOML))
	os.rename(
		os.path.join(path, CARGO_TOML_NEW),
		os.path.join(path, CARGO_TOML))
