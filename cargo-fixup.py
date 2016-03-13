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
re_dependency = re.compile('^(?:build-|dev-)?dependencies\.(.*)$')
re_name = re.compile('^\s*name\s*=\s*"(.*)"\s*$')
re_git = re.compile('^\s*git\s*=.*$')

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
			crate = None
			for line in manifest:
				match = re_group.match(line)
				if match:
					group = match.group(1)
					match = re_dependency.match(group)
					if match:
							crate = match.group(1)
					else:
							crate = None
				if crate in crates:
					match = re_git.match(line)
					if match:
						rel_path = os.path.relpath(crates[crate], path) \
										.replace(os.path.sep, '/')
						new_manifest.write(
							'path = "%s"\n' % rel_path)
						continue
				new_manifest.write(line)
	manifest.close()
	os.remove(os.path.join(path, CARGO_TOML))
	os.rename(
		os.path.join(path, CARGO_TOML_NEW),
		os.path.join(path, CARGO_TOML))
