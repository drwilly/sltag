import os, os.path as path
import sys

REPO_DIR = ".xtag"
__basedir = None

class XTagException(Exception):
	def __init__(*msg):
		Exception.__init__(msg)

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
		else:
			raise XTagException()
	return __basedir

def repodir():
	""" Return path to .xtag/ repository-dir """
	if basedir() == None:
		return None
	return path.join(basedir(), REPO_DIR)

def get_files_by_tag(tag):
	return os.listdir(path.join(repodir(), tag))

def get_tags_by_file(file):
	return [tag for tag in os.listdir(repodir()) if path.isfile(path.join(repodir(), tag, file))]

def taghash(file):
	return str(os.stat(file).st_ino)

def init():
	""" Initialize xtag-repository """
	if repodir() == None:
		os.mkdir(REPO_DIR, 0o744)
	else:
		raise XTagException("Is an xtag repository already")

def modify_tags(modify, file, tags):
	if repodir() == None:
		raise XTagException("Not an xtag repository")
	if not path.exists(file):
		raise XTagException("TODO: if not path.exists(file)")
	if not len(tags) > 0:
		raise XTagException("TODO: if not len(tags) > 0")

	if path.isfile(file):
		file = path.abspath(file)
		print(modify.__name__, path.basename(file), "tags:", *tags, sep='\t')
		modify(file, tags)
	elif path.isdir(file):
		if True: # TODO: option --recursive
			for f in os.listdir(file):
				modify_tags(modify, path.join(file, f), tags)
		else:
			raise XTagException(file, "is a directory")

def add_tags(file, tags):
	""" Add tags to file """
	for tag in tags:
		tag = path.join(repodir(), tag)
		tagfile = path.join(tag, taghash(file))
		if not path.exists(tag):
			os.mkdir(tag)
		if not path.exists(tagfile):
			os.symlink(file, tagfile)

def remove_tags(file, tags):
	""" Remove tags from file """
	for tag in tags:
		tag = path.join(repodir(), tag)
		tagfile = path.join(tag, taghash(file))
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
	print(*[os.readlink(path.join(repodir(), tags[0], tagfile)) for tagfile in files], sep='\n')

def orphans():
	""" Lists orphaned tags """
	for tag in os.listdir(repodir()):
		for tagfile in os.listdir(path.join(repodir(), tag)):
			file = os.readlink(path.join(repodir(), tag, tagfile))
			# broken symlink or different file (taghash differs)
			if not path.isfile(file) or taghash(file) != tagfile:
				print(path.join(tag, tagfile))
