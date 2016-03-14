#!/usr/bin/env python3

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

def check_version(name, version):
	try:
		response = urllib.request.urlopen(
			'https://crates.io/api/v1/crates/%s/%s' % (
				name,
				version
			))
		data = json.loads(response.read().decode('utf8'))
		if 'version' in data:
			raise RuntimeError(
				'Package %s %s already registered' % (
					name,
					version,
					))
	except urllib.error.HTTPError as err:
		if err.code == 404:
			pass
		else:
			raise

crates = {}
re_group = re.compile('^\s*\[(.*)\]\s*$')
re_dependency = re.compile('^(?:build-|dev-)?dependencies\.(.*)$')
re_name = re.compile('^\s*name\s*=\s*"(.*)"\s*$')
re_git = re.compile('^\s*git\s*=.*$')
re_version = re.compile('^\s*version\s*=\s*"(.*)"\s*$')

for path in manifests():
	manifest = open(os.path.join(path, CARGO_TOML), 'r')
	group = None
	name = None
	version = None
	for line in manifest:
		match = re_group.match(line)
		if match:
			group = match.group(1)
			continue
		if group != 'package':
			continue
		match = re_name.match(line)
		if match:
			name = match.group(1)
			crates[name] = path
			continue
		match = re_version.match(line)
		if match:
			version = match.group(1)
	if not name or not version:
		raise RuntimeError('Incomplete Cargo.toml at %s' % path)
	check_version(name, version)

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
