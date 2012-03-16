import os, os.path as path

REPO_DIR = ".sltag"
__basedir = None
__repodir = None

class SLTagError(Exception):
	pass
class SLTagRepositoryError(SLTagError):
	pass
class SLTagTagError(SLTagError):
	pass

def get_basedir(clearCache=False):
	""" Return path to .sltag/ parent-dir """
	global __basedir
	if __basedir == None or clearCache:
		__basedir = None
		basedir = path.abspath(os.curdir)
		while basedir != "/":
			if path.exists(path.join(basedir, REPO_DIR)):
				__basedir = basedir
				break
			basedir = path.dirname(basedir)
	return __basedir

def get_repodir(clearCache=False):
	""" Return path to .sltag/ repository-dir """
	global __repodir
	if __repodir == None or clearCache:
		basedir = get_basedir(clearCache)
		if basedir == None:
			raise SLTagRepositoryError()
		__repodir = path.join(basedir, REPO_DIR)
	return __repodir

def get_files_by_tag(tag):
	try:
		return os.listdir(path.join(get_repodir(), tag))
	except OSError as e:
		if e.errno == 2:
			raise SLTagTagError("No such tag:", tag)
		raise e

def get_tags_by_file(file):
	repodir = get_repodir()
	hash = taghash(file)
	return [tag for tag in os.listdir(repodir) if path.islink(path.join(repodir, tag, hash))]

def taghash(file):
	return str(os.stat(file).st_ino)

def init():
	""" Initialize sltag-repository """
	if get_basedir() == None:
		os.mkdir(REPO_DIR, 0o744)
	else:
		raise SLTagRepositoryError("Existing repository found at", get_repodir())

def add_tags(files, tags):
	""" Add tags to files """
	repodir = get_repodir()
	files_and_hashes = [(file, taghash(file)) for file in files]
	for tag in tags:
		tagdir = path.join(repodir, tag)
		if not path.exists(tagdir):
			os.mkdir(tagdir)
		for file, hash in files_and_hashes:
			relfile = path.relpath(file, tagdir)
			tagfile = path.join(tagdir, hash)
			try:
				os.symlink(relfile, tagfile)
			except OSError:
				pass

def remove_tags(files, tags):
	""" Remove tags from files """
	repodir = get_repodir()
	hashes = [taghash(file) for file in files]
	for tag in tags:
		tagdir = path.join(repodir, tag)
		for hash in hashes:
			tagfile = path.join(tagdir, hash)
			# this check is probably superfluous, but this is also
			# the only place where serious harm could be done
			if not path.islink(tagfile):
				raise SLTagError(tagfile, "is not a symlink")
			os.unlink(tagfile)
		try:
			os.rmdir(tagdir)
		except OSError:
			pass

def set_tags(files, tags):
	""" Set tags of files """
	for file in files:
		current_tags = get_tags_by_file(file)
		add_tags(file, [tag for tag in tags if tag not in current_tags])
		remove_tags(file, [tag for tag in current_tags if tag not in tags])

def list(tags):
	""" List tagfiles having all passed tags """
	repodir = get_repodir()
	firsttag = tags.pop()
	tagfiles = set(get_files_by_tag(firsttag))
	for tag in tags:
		tagfiles &= set(get_files_by_tag(tag))
	for tagfile in tagfiles:
		file = path.realpath(path.join(repodir, firsttag, tagfile))
		yield(path.relpath(file))

def orphans():
	""" Lists orphaned tags """
	repodir = get_repodir()
	for tagdir in os.listdir(repodir):
		for tagfile in os.listdir(path.join(repodir, tagdir)):
			tagfile_fullpath = path.join(repodir, tagdir, tagfile)
			# broken symlink or different file (taghash differs)
			# os.stat (path.isfile() and taghash()) follows symlinks
			if not path.isfile(tagfile_fullpath) or taghash(tagfile_fullpath) != tagfile:
				yield(tagfile_fullpath)
