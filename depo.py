# This script downloads git repositories and sets them to the
# specified version / branch you want. It's up to you to use 
# the downloaded packages correctly.
# 
# A deps.json file must be provided (I'll add command args parsing later)
# containing declaration for dependencies. It also points out where to
# install the packages
#
# Made by brainsandwich
# Free of use

import json, os, sys, subprocess

# init
script_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_path, sys.argv[1] if len(sys.argv) > 1 else 'deps.json')
print('> Deps fetcher 1.0')
print('> Configuration file : ' + config_path)
if not os.path.exists(config_path):
	sys.exit('! No config found ! Aborting ...')

# parse config
config_file = open(config_path, 'r')
config = json.loads(config_file.read())
config_file.close()

# create dir
deps_path = os.path.join(script_path, config['path'] if 'path' in config else 'external')
print('> Installing dependencies in ' + deps_path + ' ...')
if not os.path.exists(deps_path):
    os.makedirs(deps_path)

# clone packages (assume all git for now)
for package in config['packages']:
	sys.stdout.flush()
	name = package['name']
	repo_dir = os.path.join(deps_path, name)
	print('> Fetching package ' + name + ' in ' + repo_dir)

	# if origin is not a url, it's a filepath and
	# we need its absolute value
	origin = package['origin']
	if not origin[:4] == 'http':
		origin = os.path.join(script_path, origin)

	# one can either provide a version or a branch
	version = package['version'] if 'version' in package else ''
	branch = package['branch'] if 'branch' in package else ''

	# init repo in repo_dir
	if not os.path.exists(repo_dir):
		os.makedirs(repo_dir)
		subprocess.call(['git', 'init', repo_dir])
		subprocess.call(['git', 'remote', 'add', 'origin', origin], cwd=repo_dir)
		subprocess.call(['git', 'checkout', '-b', 'target'], cwd=repo_dir)

	# fetch branch / version (this will effectively download stuff)
	subprocess.call(['git', 'fetch'], cwd=repo_dir)
	if version != '':
		subprocess.call(['git', 'reset', '--hard', version], cwd=repo_dir)
	else:
		subprocess.call(['git', 'reset', '--hard', 'origin/' + branch], cwd=repo_dir)
