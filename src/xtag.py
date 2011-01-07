import os, os.path as path
import sys

REPO_DIR = ".xtag"

def err(*msg):
	print(*msg, file=sys.stderr)

def basedir():
	""" Return path to .xtag/ repository-dir """
	basedir = path.abspath(os.curdir)
	while basedir != "/":
		if path.exists(path.join(basedir, REPO_DIR)):
			return basedir
		basedir = path.dirname(basedir)
	return None

def get_files_by_tag(tag):
	os.chdir(path.join(basedir(), REPO_DIR))
	return os.listdir(tag)

def get_tags_by_file(file):
	os.chdir(path.join(basedir(), REPO_DIR))
	return [tag for tag in os.listdir(".") if path.isfile(path.join(tag, file))]

def init():
	""" Initialize xtag-repository """
	if basedir() == None:
		os.mkdir(REPO_DIR, 0o744)
	else:
		err("Is an xtag repository already")

def modify_tags(modify, args):
	file = args[0]
	tags = args[1:]
	if not path.exists(file):
		err("TODO: if not path.exists(file)")
		return
	if not len(tags) > 0:
		err("TODO: if not len(tags) > 0")
		return

	if path.isfile(file):
		file = path.abspath(file)
		print(modify.__name__, path.basename(file), "tags:", *tags, sep=' ')
		os.chdir(path.join(basedir(), REPO_DIR))
		modify(file, tags)
	elif path.isdir(file):
		if False: # TODO: option --recursive
			for f in os.listdir(file):
				modify(path.join(file, f), tags)
		else:
			err(file, "is a directory")

def add_tags(file, tags):
	""" Add tags to file """
	for tag in tags:
		if not path.exists(tag):
			os.mkdir(tag)
		f = path.join(tag, path.basename(file))
		if not path.exists(f):
			os.link(file, f)

def remove_tags(file, tags):
	""" Remove tags from file """
	for tag in tags:
		f = path.join(tag, path.basename(file))
		if path.exists(f):
			os.unlink(f)
		if os.listdir(tag) == []:
			os.rmdir(tag)

def set_tags(file, tags):
	""" Set tags of file """
	add(file, [tag for tag in tags if tag not in get_tags_by_file(file)])
	remove(file, [tag for tag in get_tags_by_file(file) if tag not in tags])

def list(tags):
	""" List files having all passed tags """
	files = get_files_by_tag(tags[0])
	for t in tags[1:]:
		files = [file for file in files if file in get_files_by_tag(t)] # wtf :D
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
	"add"     : lambda args: modify_tags(add_tags, args),
	"remove"  : lambda args: modify_tags(remove_tags, args),
	"set"	  : lambda args: modify_tags(set_tags, args),
	"list"    : lambda args: list(args),
	"orphans" : lambda args: orphans(),
}

del sys.argv[0]

s = sys.argv.pop(0)
cmds = [c for c in commands.keys() if c.startswith(s)]
if len(cmds) == 1:
	commands[cmds[0]](sys.argv)
elif len(cmds) == 0:
	err(s, "is not a known command")
else:
	err(s, "is ambiguous: ", cmds)
