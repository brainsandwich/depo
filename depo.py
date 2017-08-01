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

import json, os, sys, subprocess, shutil, argparse, threading

# ------------------------------------------------------
# Functions
# ------------------------------------------------------

#
# Dowload a package
#
def getpack(root, name, origin, target, remote_target, force):
	# init repo in root dir
	if not os.path.exists(root):
		os.makedirs(root)
		subprocess.call(['git', 'clone', '-b', target, '--single-branch', '--depth', '1', origin, root], stdout=console_out, stderr=console_out)
		subprocess.call(['git', 'checkout', '-b', 'target'], cwd=root, stdout=console_out, stderr=console_out)
	elif force:
		subprocess.call(['git', 'fetch'], cwd=root, stdout=console_out, stderr=console_out)
		subprocess.call(['git', 'reset', '--hard', remote_target], cwd=root, stdout=console_out, stderr=console_out)

	print('* Package \'' + name + '/' + target + '\' fetched ')
	return

#
# Build a package
#
def makepack(srcpath, buildpath, outpath, generator, parameters):
	print('* Making package \'' + name + ' ...')
	sys.stdout.flush()

	# CMake configure command
	configure_command = ['cmake', '-G' + generator, '-H' + srcpath, '-B' + buildpath, '-DCMAKE_INSTALL_PREFIX=' + outpath, '-DCMAKE_DEBUG_POSTFIX=_d']
	if parameters is not None:
		for param in parameters:
			configure_command.append('-D' + param)
	subprocess.call(configure_command, stdout=console_out, stderr=console_out)

	# CMake build command
	subprocess.call(['cmake', '--build', buildpath, '--target', 'INSTALL', '--config', 'Debug'], stdout=console_out, stderr=console_out)
	subprocess.call(['cmake', '--build', buildpath, '--target', 'INSTALL', '--config', 'Release'], stdout=console_out, stderr=console_out)

	print('* Package \'' + name + ' ready.')
	sys.stdout.flush()
	return

#
# Self update function
#
def update_self():
	import stat
	repo = 'depo'

	getpack(repo, repo, 'https://github.com/brainsandwich/depo.git', 'master', '', True)
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

#
# Package getter thread
#
class PackageGetter (threading.Thread):
	def __init__(self, root, name, origin, target, remote_target, force):
		threading.Thread.__init__(self)
		self.root = root
		self.name = name
		self.origin = origin
		self.target = target
		self.remote_target = remote_target
		self.force = force

	def run(self):
		getpack(self.root, self.name, self.origin, self.target, self.remote_target, self.force)

# ------------------------------------------------------
# Script
# ------------------------------------------------------

print('depo 1.2')
sys.stdout.flush()

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', help='verbose output', action='store_true')
parser.add_argument('-u', '--update', help='update this script', action='store_true')
parser.add_argument('-c', '--clear', help='clear dependencies folder before fetching', action='store_true')
parser.add_argument('-f', '--force', help='forces redownload of packages', action='store_true')
parser.add_argument('-b', '--build', help='build packages', action='store_true')
parser.add_argument('-i', '--input', help='path to the configuration file, default is \'./deps.json\'')
args = parser.parse_args()

# Keep quiet if not verbose
console_out = sys.stdout if args.verbose else open(os.devnull, 'w')

# Update if required
if args.update:
	update_self()
	sys.exit()

# Init some paths
script_path = os.path.dirname(os.path.realpath(__file__))
config_path = args.input if args.input else 'deps.json'
print('> Configuration file : ' + config_path)
if not os.path.exists(config_path):
	sys.exit('! No config found ! Aborting ...')

# Parse JSON config
config_file = open(config_path, 'r')
config = json.loads(config_file.read())
config_file.close()

# Get config parameters
generator = config['generator'] if 'generator' in config else ''
dowload_path = config['download-path'] if 'download-path' in config else 'external/sources'
build_path = config['build-path'] if 'build-path' in config else 'external/build'
output_path = config['output-path'] if 'output-path' in config else 'external/output'

# Clear directories
if args.clear and os.path.exists(dowload_path):
	def set_rw(operation, name, exc):
		os.chmod(name, stat.S_IWRITE)
		operation(name)
	shutil.rmtree(os.path.abspath(dowload_path), onerror=set_rw)
	shutil.rmtree(os.path.abspath(build_path), onerror=set_rw)
	shutil.rmtree(os.path.abspath(output_path), onerror=set_rw)

# Create download dir
print('> Dowloading dependencies in ' + dowload_path)
if not os.path.exists(dowload_path):
    os.makedirs(dowload_path)

package_getters = []

# Clone packages (assume all git for now)
for package in config['packages']:
	sys.stdout.flush()
	name = package['name']
	origin = package['origin']
	repo_dir = os.path.join(dowload_path, name)

	# A version or a branch name must be set
	version = package['version'] if 'version' in package else ''
	branch = package['branch'] if 'branch' in package else ''
	target = version if len(version) != 0 else branch
	remote_target = 'origin/' + target if len(version) == 0 else target

	th = PackageGetter(repo_dir, name, origin, target, remote_target, args.force)
	th.start()
	package_getters.append(th)

# Wait for dowload completion
for th in package_getters:
	th.join()

# Build packages
if args.build and len(generator) > 0:
	for package in config['packages']:
		sys.stdout.flush()
		name = package['name']
		repo_dir = os.path.join(dowload_path, name)
		build_dir = os.path.join(build_path, name)
		build_package = package['build'] if 'build' in package else False
		if build_package:
			makepack(repo_dir, build_dir, output_path, generator, package['build-options'] if 'build-options' in package else None)

print('> Dependencies ready')