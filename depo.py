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

# 
def getpack(root, name, origin, branch, version):
	target = version if len(version) != 0 else branch
	remote_target = 'origin/' + target if len(version) == 0 else target

	# init repo in root dir
	if not os.path.exists(root):
		os.makedirs(root)
		subprocess.call(['git', 'init', root], stdout=console_out, stderr=console_out)
		subprocess.call(['git', 'remote', 'add', 'origin', origin], cwd=root, stdout=console_out, stderr=console_out)
		subprocess.call(['git', 'checkout', '-b', 'target'], cwd=root, stdout=console_out, stderr=console_out)
	else:
		try:
			subprocess.call(['git', 'fetch'], cwd=root, stdout=console_out, stderr=console_out)
			diff = subprocess.check_output(['git', 'diff', remote_target, 'target'], cwd=root, stderr=console_out)
		except Exception as e:
			print('! Failed to get diff with remote target for package \'' + name + '\' ; branch / version \'' + target + '\' may not exist')
			return

		if len(diff) == 0:
			print('* Package \'' + name + '\' already fetched ; with branch / version \'' + target + '\'')
		else:
			print('* Package \'' + name + '\' has changed')
			subprocess.call(['git', 'reset', '--hard', remote_target], cwd=root, stdout=console_out, stderr=console_out)
			
	return

# Self update function
def update_self():
	import stat
	repo = 'depo'

	getpack(repo, repo, 'https://github.com/brainsandwich/depo.git', 'master', '')
	lastupdate = subprocess.check_output(['git', 'show', '-s', '--format=\"%ci\"'], cwd=repo)

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

	print('> Depo script correctly updated !')
	print('> Last update : ' + lastupdate)
	sys.stdout.flush()
	return


parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', help='verbose output', action='store_true')
parser.add_argument('-u', '--update', help='update this script', action='store_true')
parser.add_argument('-c', '--clear', help='clear dependencies folder before fetching', action='store_true')
parser.add_argument('-i', '--input', help='path to the configuration file, default is \'./deps.json\'')
parser.add_argument('-o', '--output', help='path to the dependencies installation folder, default is \'./external\'')
args = parser.parse_args()

console_out = sys.stdout if args.verbose else open(os.devnull, 'w')

# Update if required
if args.update:
	update_self()
	sys.exit()

# init
script_path = os.path.dirname(os.path.realpath(__file__))
config_path = args.input if args.input else 'deps.json'
print('> Depo 1.0')
print('> Configuration file : ' + config_path)
if not os.path.exists(config_path):
	sys.exit('! No config found ! Aborting ...')

# parse config
config_file = open(config_path, 'r')
config = json.loads(config_file.read())
config_file.close()

# rmdir before doing anything
deps_path = args.output if args.output else 'external'
if args.clear and os.path.exists(deps_path):
	def set_rw(operation, name, exc):
		os.chmod(name, stat.S_IWRITE)
		operation(name)
	shutil.rmtree(os.path.abspath(deps_path), onerror=set_rw)

# create dir
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
	target = version if len(version) != 0 else branch
	remote_target = 'origin/' + target if len(version) == 0 else target

	getpack(repo_dir, name, origin, branch, version)

print('> Dependencies ready')