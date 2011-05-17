import os, os.path as path

REPO_DIR = ".xtag"
__basedir = None

class XTagError(Exception):
	pass
class XTagRepositoryError(XTagError):
	pass
class XTagTagError(XTagError):
	pass

def basedir(clearCache=False):
	""" Return path to .xtag/ parent-dir """
	global __basedir

	if clearCache:
		__basedir = None

	if __basedir == None:
		basedir = path.abspath(os.curdir)
		while basedir != "/":
			if path.exists(path.join(basedir, REPO_DIR)):
				__basedir = basedir
				break
			basedir = path.dirname(basedir)
	return __basedir

def repodir(clearCache=False):
	""" Return path to .xtag/ repository-dir """
	try:
		return path.join(basedir(clearCache), REPO_DIR)
	except TypeError: # raised when basedir() returns None
		raise XTagRepositoryError()

def get_files_by_tag(tag):
	try:
		return os.listdir(path.join(repodir(), tag))
	except OSError as e:
		if e.errno == 2:
			raise XTagTagError("No such tag:", tag)
		raise e

def get_tags_by_file(file):
	return [tag for tag in os.listdir(repodir()) if path.isfile(path.join(repodir(), tag, file))]

def taghash(file):
	return str(os.stat(file).st_ino)

def init():
	""" Initialize xtag-repository """
	if basedir() == None:
		os.mkdir(REPO_DIR, 0o744)
	else:
		raise XTagRepositoryError("Existing repository found at", repodir())

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
			# this check is probably superfluous, but this is also
			# the only place where serious harm could be done
			if not path.islink(tagfile):
				raise XTagError(tagfile, "is not a symlink")
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
		yield(path.realpath(path.join(repodir(), tags[0], tagfile)))

def orphans():
	""" Lists orphaned tags """
	for tagdir in os.listdir(repodir()):
		for tagfile in os.listdir(path.join(repodir(), tagdir)):
			file = path.realpath(path.join(repodir(), tagdir, tagfile))
			# broken symlink or different file (taghash differs)
			if not path.isfile(file) or taghash(file) != tagfile:
				yield(path.join(repodir(), tagdir, tagfile))
