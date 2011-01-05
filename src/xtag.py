from abc import ABCMeta, abstractmethod, abstractproperty
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

def get_files_by_tag(tag):
	os.chdir(path.join(basedir(), REPO_DIR))
	return os.listdir(tag)

def get_tags_by_file(file):
	os.chdir(path.join(basedir(), REPO_DIR))
	return [tag for tag in os.listdir(".") if path.isfile(path.join(tag, file))]

class cmd:
	@abstractmethod
	def exec(self, args):
		pass

class init(cmd):
	""" Initialize xtag-repository """
	def exec(self, args):
		if basedir() == None:
			os.mkdir(REPO_DIR, 0o744)
		else:
			print("Is an xtag repository already")

class modify(cmd):
	def exec(self, args):
		file = args[0]
		tags = args[1:]
		if not path.exists(file):
			err("TODO: if not path.exists(file)")
		if not len(tags) > 0:
			err("TODO: if not len(tags) > 0")

		if path.isfile(file):
			file = path.abspath(file)
			os.chdir(path.join(basedir(), REPO_DIR))
			self.modify_tags(file, tags)
		elif path.isdir(file):
			if False: # TODO: option --recursive
				for f in os.listdir(file):
					self.modify_tags(path.join(file, f), tags)
			else:
				err(file, " is a directory")
	@abstractmethod
	def modify_tags(self, file, tags):
		pass

class add(modify):
	""" Add tags to file """
	def modify_tags(self, file, tags):
		print("add", path.basename(file), "tags:", *tags, sep=' ')
		for tag in tags:
			if not path.exists(tag):
				os.mkdir(tag)
			f = path.join(tag, path.basename(file))
			if not path.exists(f):
				os.link(file, f)

class remove(modify):
	""" Remove tags from file """
	def modify_tags(self, file, tags):
		print("rem", path.basename(file), "tags:", *tags, sep=' ')
		for tag in tags:
			f = path.join(tag, path.basename(file))
			if path.exists(f):
				os.unlink(f)
			if os.listdir(tag) == []:
				os.rmdir(tag)

class set(modify):
	def modify_tags(self, file, tags):
		print("set", path.basename(file), "tags:", *tags, sep=' ')
		toadd = [tag for tag in tags if tag not in get_tags_by_file(file)]
		toremove = [tag for tag in get_tags_by_file(file) if tag not in tags]
		err("to add: ", toadd)
		err("to rem: ", toremove)
		err("TODO: modify_tags()")

class list(cmd):
	def exec(self, args):
		tags = args
		os.chdir(path.join(basedir(), REPO_DIR))
		files = self.get_files_by_tag(tags[0])
		for t in tags[1:]:
			files = [file for file in files if file in get_files_by_tag(t)] # wtf :D
		print(*files, sep='\n')

class orphans(cmd):
	""" Lists orphaned tags """
	def exec(self, args):
		err("TODO: orphans")

# -- main --
s = sys.argv[1]
commandclasses = [init, add, remove, set, list, orphans]
cmds = [c for c in commandclasses if c.__name__.startswith(s)]
if len(cmds) == 1:
	cmds[0]().exec(sys.argv[2:])
else:
	print(cmds)
