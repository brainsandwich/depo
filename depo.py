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

import json, os, sys, subprocess, shutil, argparse

# Self update function
def update_self():
	import stat
	repo = 'depo'

	subprocess.call(['git', 'clone', 'https://github.com/brainsandwich/depo.git'])
	if not os.path.isdir(repo):
		print 'Couldn\'t fetch update from github ...' 
		return False

	self_script = open(os.path.realpath(__file__), 'w')
	new_script = open(os.path.join(repo, 'depo.py'), 'r')
	for l in new_script:
		self_script.write(l)

	self_script.close()
	new_script.close()

	def set_rw(operation, name, exc):
	    os.chmod(name, stat.S_IWRITE)
	    operation(name)
	shutil.rmtree(os.path.abspath(repo), onerror=set_rw)
	return True

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', help='verbose output', action='store_true')
parser.add_argument('-u', '--update', help='update this script', action='store_true')
parser.add_argument('-c', '--cfg', help='path to the configuration file, default is \'./deps.json\'')
args = parser.parse_args()

if args.verbose:
	console_out = sys.stdout
else:
	console_out = open(os.devnull, 'w')

# Update if required
if args.update:
	update_self()

# init
script_path = os.path.dirname(os.path.realpath(__file__))
config_path = args.cfg if args.cfg else 'deps.json'
print('> Depo 1.0')
print('> Configuration file : ' + config_path)
if not os.path.exists(config_path):
	sys.exit('! No config found ! Aborting ...')

# parse config
config_file = open(config_path, 'r')
config = json.loads(config_file.read())
config_file.close()

# create dir
deps_path = config['path'] if 'path' in config else 'external'
print('> Installing dependencies in ' + deps_path)
if not os.path.exists(deps_path):
    os.makedirs(deps_path)

# clone packages (assume all git for now)
for package in config['packages']:
	sys.stdout.flush()
	name = package['name']
	origin = package['origin']
	repo_dir = os.path.join(deps_path, name)

	# one can either provide a version or a branch
	version = package['version'] if 'version' in package else ''
	branch = package['branch'] if 'branch' in package else ''

	# init repo in repo_dir
	if not os.path.exists(repo_dir):
		os.makedirs(repo_dir)
		subprocess.call(['git', 'init', repo_dir], stdout=console_out, stderr=console_out)
		subprocess.call(['git', 'remote', 'add', 'origin', origin], cwd=repo_dir, stdout=console_out, stderr=console_out)
		subprocess.call(['git', 'checkout', '-b', 'target'], cwd=repo_dir, stdout=console_out, stderr=console_out)

	# fetch branch / version (this will effectively download stuff)
	subprocess.call(['git', 'fetch'], cwd=repo_dir, stdout=console_out, stderr=console_out)
	if version != '':
		subprocess.call(['git', 'reset', '--hard', version], cwd=repo_dir, stdout=console_out, stderr=console_out)
		print('* Package \'' + name + '\' fetched ; with version ' + version)
	else:
		subprocess.call(['git', 'reset', '--hard', 'origin/' + branch], cwd=repo_dir, stdout=console_out, stderr=console_out)
		print('* Package \'' + name + '\' fetched ; on branch ' + branch)

print('> Dependencies ready')