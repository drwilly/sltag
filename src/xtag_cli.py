#!/usr/bin/env python3
from xtag import *
import os
import sys

def die(*msg):
	print(*msg, file=sys.stderr)
	sys.exit(1)

def modify_tags(modify, files, tags):
	if len(tags) == 0:
		die("No tags")

	i = 0
	while i < len(files):
		if path.isfile(files[i]):
			print(modify.__name__, path.basename(files[i]), "tags:", *tags, sep='\t')
			i += 1
		elif path.isdir(files[i]):
			if True: # TODO: option --recursive
				files[i:i+1] = [path.join(files[i], file) for file in os.listdir(files[i])]
			else:
				die(files[i], "is a directory")

	if i == 0:
		die("No files")

	modify(files, tags)

commands = {
	"init"        : lambda args: init(),
	"tag-files"   : lambda args: modify_tags(add_tags, args[1:], args[:1]),
	"untag-files" : lambda args: modify_tags(remove_tags, args[1:], args[:1]),
	"add-tags"    : lambda args: modify_tags(add_tags, args[:1], args[1:]),
	"remove-tags" : lambda args: modify_tags(remove_tags, args[:1], args[1:]),
	"set-tags"    : lambda args: modify_tags(set_tags, args[:1], args[1:]),
	"list"        : lambda args: print(*list(args), sep='\n'),
	"orphans"     : lambda args: print(*orphans(), sep='\n'),
	"help"        : lambda args: print(*commands.keys(), sep='\n'),
}

del sys.argv[0]

if sys.argv == []:
	die("TODO: No command")

s = sys.argv.pop(0)
cmds = [c for c in commands.keys() if c.startswith(s)]
if len(cmds) == 0:
	die(s, "is not a known command")
elif len(cmds) > 1:
	die(s, "is ambiguous:", cmds)

try:
	commands[cmds[0]](sys.argv)
except Exception as e:
	die(*e.args)
