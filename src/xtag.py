import os, os.path as path

REPO_DIR = ".xtag"
__basedir = None

class XTagError(Exception):
	pass

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
		raise XTagError("Is an xtag repository already")

def modify_tags(modify, files, tags):
	if repodir() == None:
		raise XTagError("Not an xtag repository")

	for file in files:
		if path.isfile(file):
			#file = path.abspath(file)
			print(modify.__name__, path.basename(file), "tags:", *tags, sep='\t')
		elif path.isdir(file):
			if True: # TODO: option --recursive
				for f in os.listdir(file):
					modify_tags(modify, path.join(file, f), tags)
			else:
				raise XTagError(file, "is a directory")
	modify(files, tags)

def add_tags(files, tags):
	""" Add tags to files """
	files_and_hashes = [(file, taghash(file)) for file in files]
	for tag in tags:
		tagdir = path.join(repodir(), tag)
		if not path.exists(tagdir):
			os.mkdir(tagdir)
		for file, hash in files_and_hashes:
			relfile = path.relpath(file, tagdir)
			tagfile = path.join(tagdir, hash)
			try:
				os.symlink(relfile, tagfile)
			except:
				pass

def remove_tags(files, tags):
	""" Remove tags from files """
	hashes = [taghash(file) for file in files]
	for tag in tags:
		tagdir = path.join(repodir(), tag)
		for hash in hashes:
			tagfile = path.join(tagdir, hash)
			os.unlink(tagfile)
		try:
			os.rmdir(tagdir)
		except:
			pass

def set_tags(files, tags):
	""" Set tags of files """
	for file in files:
		current_tags = get_tags_by_file(file)
		add_tags(file, [tag for tag in tags if tag not in current_tags])
		remove_tags(file, [tag for tag in current_tags if tag not in tags])

def list(tags):
	""" List tagfiles having all passed tags """
	tagfiles = get_files_by_tag(tags[0])
	for tag in tags[1:]:
		tagfiles = [tagfile for tagfile in tagfiles if tagfile in get_files_by_tag(tag)]
	for tagfile in tagfiles:
		yield(path.abspath(os.readlink(path.join(repodir(), tags[0], tagfile))))

def orphans():
	""" Lists orphaned tags """
	for tag in os.listdir(repodir()):
		for tagfile in os.listdir(path.join(repodir(), tag)):
			file = os.readlink(path.join(repodir(), tag, tagfile))
			# broken symlink or different file (taghash differs)
			if not path.isfile(file) or taghash(file) != tagfile:
				yield(path.join(repodir(), tag, tagfile))
