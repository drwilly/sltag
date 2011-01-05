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

def modify(modify_tags, args):
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
		print(modify_tags.__name__, path.basename(file), "tags:", *tags, sep=' ')
		print(basedir(), REPO_DIR)
		os.chdir(path.join(basedir(), REPO_DIR))
		modify_tags(file, tags)
	elif path.isdir(file):
		if False: # TODO: option --recursive
			for f in os.listdir(file):
				modify_tags(path.join(file, f), tags)
		else:
			err(file, " is a directory")

def add(file, tags):
	""" Add tags to file """
	for tag in tags:
		if not path.exists(tag):
			os.mkdir(tag)
		f = path.join(tag, path.basename(file))
		if not path.exists(f):
			os.link(file, f)

def remove(file, tags):
	""" Remove tags from file """
	for tag in tags:
		f = path.join(tag, path.basename(file))
		if path.exists(f):
			os.unlink(f)
		if os.listdir(tag) == []:
			os.rmdir(tag)

def set(file, tags):
	""" Set tags of file """
	add(file, [tag for tag in tags if tag not in get_tags_by_file(file)])
	remove(file, [tag for tag in get_tags_by_file(file) if tag not in tags])

def list(tags):
	""" List files having all passed tags """
	os.chdir(path.join(basedir(), REPO_DIR))
	files = get_files_by_tag(tags[0])
	for t in tags[1:]:
		files = [file for file in files if file in get_files_by_tag(t)] # wtf :D
	print(*files, sep='\n')

def orphans():
	""" Lists orphaned tags """
	err("TODO: orphans")

# -- main --
commands = {
	"init"    : lambda args: init(),
	"add"     : lambda args: modify(add, args),
	"remove"  : lambda args: modify(remove, args),
	"set"	  : lambda args: modify(set, args),
	"list"    : lambda args: list(args),
	"orphans" : lambda args: orphans(),
}
s = sys.argv[1]
cmds = [c for c in commands.keys() if c.startswith(s)]
if len(cmds) == 1:
	commands[cmds[0]](sys.argv[2:])
elif len(cmds) == 0:
	err(s, " is not a known command")
else:
	err(s, " is ambiguous: ", cmds)
