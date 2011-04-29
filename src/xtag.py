import os, os.path as path

REPO_DIR = ".xtag"
__basedir = None

class XTagError(Exception):
	pass
class XTagRepositoryError(XTagError):
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
		raise XTagRepositoryError("Existing repository found at", repodir())

def add_tags(files, tags):
	""" Add tags to files """
	if repodir() == None:
		raise XTagRepositoryError()

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
	if repodir() == None:
		raise XTagRepositoryError()

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
	if repodir() == None:
		raise XTagRepositoryError()

	for file in files:
		current_tags = get_tags_by_file(file)
		add_tags(file, [tag for tag in tags if tag not in current_tags])
		remove_tags(file, [tag for tag in current_tags if tag not in tags])

def list(tags):
	""" List tagfiles having all passed tags """
	if repodir() == None:
		raise XTagRepositoryError()

	tagfiles = get_files_by_tag(tags[0])
	for tag in tags[1:]:
		tagfiles = [tagfile for tagfile in tagfiles if tagfile in get_files_by_tag(tag)]
	for tagfile in tagfiles:
		yield(path.realpath(path.join(repodir(), tags[0], tagfile)))

def orphans():
	""" Lists orphaned tags """
	if repodir() == None:
		raise XTagRepositoryError()

	for tagdir in os.listdir(repodir()):
		for tagfile in os.listdir(path.join(repodir(), tagdir)):
			file = path.realpath(path.join(repodir(), tagdir, tagfile))
			# broken symlink or different file (taghash differs)
			if not path.isfile(file) or taghash(file) != tagfile:
				yield(path.join(repodir(), tagdir, tagfile))
