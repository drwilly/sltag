#!/usr/bin/env python3
import os, os.path as path
import sys

REPO_DIR = ".xtag"
__basedir = None

def err(*msg):
	print(*msg, file=sys.stderr)

def basedir():
	""" Return path to .xtag/ parent-dir """
	global __basedir
	if __basedir == None:
		basedir = path.abspath(os.curdir)
		while basedir != "/":
			if path.exists(path.join(basedir, REPO_DIR)):
				__basedir = basedir
				break
			basedir = path.dirname(basedir)
	return __basedir

def repodir():
	""" Return path to .xtag/ repository-dir """
	if basedir() == None:
		return None
	else:
		return path.join(basedir(), REPO_DIR)

def get_files_by_tag(tag):
	return os.listdir(path.join(repodir(), tag))

def get_tags_by_file(file):
	return [tag for tag in os.listdir(repodir()) if path.isfile(path.join(repodir(), tag, file))]

def init():
	""" Initialize xtag-repository """
	if repodir() == None:
		os.mkdir(REPO_DIR, 0o744)
	else:
		err("Is an xtag repository already")

def modify_tags(modify, file, tags):
	if repodir() == None:
		err("Not an xtag repository")
		return
	if not path.exists(file):
		err("TODO: if not path.exists(file)")
		return
	if not len(tags) > 0:
		err("TODO: if not len(tags) > 0")
		return

	if path.isfile(file):
		file = path.abspath(file)
		print(modify.__name__, path.basename(file), "tags:", *tags, sep='\t')
		modify(file, tags)
	elif path.isdir(file):
		if True: # TODO: option --recursive
			for f in os.listdir(file):
				modify_tags(modify, path.join(file, f), tags)
		else:
			err(file, "is a directory")

def add_tags(file, tags):
	""" Add tags to file """
	for tag in tags:
		tag = path.join(repodir(), tag)
		tagfile = path.join(tag, str(os.stat(file).st_ino))
		if not path.exists(tag):
			os.mkdir(tag)
		if not path.exists(tagfile):
			os.link(file, tagfile)

def remove_tags(file, tags):
	""" Remove tags from file """
	for tag in tags:
		tag = path.join(repodir(), tag)
		tagfile = path.join(tag, str(os.stat(file).st_ino))
		if path.exists(tagfile):
			os.unlink(tagfile)
		if os.listdir(tag) == []:
			os.rmdir(tag)

def set_tags(file, tags):
	""" Set tags of file """
	add_tags(file, [tag for tag in tags if tag not in get_tags_by_file(file)])
	remove_tags(file, [tag for tag in get_tags_by_file(file) if tag not in tags])

def list(tags):
	""" List files having all passed tags """
	files = get_files_by_tag(tags[0])
	for tag in tags[1:]:
		files = [tagfile for tagfile in files if tagfile in get_files_by_tag(tag)] # wtf :D
	print(*files, sep='\n')

def orphans():
	""" Lists orphaned tags """
	tagfiles = [] # get all tag files
	for root, dirs, files in os.walk(path.join(basedir(), REPO_DIR)):
		tagfiles.extend(path.join(root, name) for name in files)
	inodes = {} # get corresponding inodes
	for tagfile in tagfiles:
		stat = os.stat(tagfile)
		if stat.st_nlink > 1:
			inodes[stat.st_ino] = tagfile
		else: # tag definitely orphaned
			print(tagfile)
	# check if inodes exist in repo (sigh)
	for root, dirs, files in os.walk(basedir()):
		if REPO_DIR in dirs:
			dirs.remove(REPO_DIR)
		# TODO workaround :\
		for foo in {inode for inode in inodes.keys() if inode in [os.stat(path.join(root, name)).st_ino for name in files]}:
			del inodes[foo]
	# remaining inodes == orphaned tags
	print(*inodes.values(), sep='\n')


# -- main --
commands = {
	"init"    : lambda args: init(),
	"add"     : lambda args: modify_tags(add_tags, args[0], args[1:]),
	"remove"  : lambda args: modify_tags(remove_tags, args[0], args[1:]),
	"set"	  : lambda args: modify_tags(set_tags, args[0], args[1:]),
	"list"    : lambda args: list(args),
	"orphans" : lambda args: orphans(),
}

del sys.argv[0]

if sys.argv == []:
	print("TODO: No command")
	sys.exit(1)

s = sys.argv.pop(0)
cmds = [c for c in commands.keys() if c.startswith(s)]
if len(cmds) == 1:
	commands[cmds[0]](sys.argv)
elif len(cmds) == 0:
	err(s, "is not a known command")
else:
	err(s, "is ambiguous: ", cmds)
