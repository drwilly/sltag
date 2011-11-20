#!/usr/bin/env python3
import sltag

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
		if os.path.isfile(files[i]):
			print(modify.__name__, os.path.basename(files[i]), "tags:", *tags, sep='\t')
			i += 1
		elif os.path.isdir(files[i]):
			if True: # TODO: option --recursive
				files[i:i+1] = [os.path.join(files[i], file) for file in os.listdir(files[i])]
			else:
				die(files[i], "is a directory")

	if i == 0:
		die("No files")

	modify(files, tags)

commands = {
	"init"        : lambda args: sltag.init(),
	"tag-files"   : lambda args: modify_tags(sltag.add_tags, args[1:], args[:1]),
	"untag-files" : lambda args: modify_tags(sltag.remove_tags, args[1:], args[:1]),
	"add-tags"    : lambda args: modify_tags(sltag.add_tags, args[:1], args[1:]),
	"remove-tags" : lambda args: modify_tags(sltag.remove_tags, args[:1], args[1:]),
	"set-tags"    : lambda args: modify_tags(sltag.set_tags, args[:1], args[1:]),
	"list"        : lambda args: print(*os.listdir(sltag.get_repodir()), sep='\t') if len(args) == 0 else print(*sltag.list(args), sep='\n'),
	"orphans"     : lambda args: print(*sltag.orphans(), sep='\n'),
	"repository"  : lambda args: print(sltag.get_repodir()),
	"help"        : lambda args: print(*commands.keys(), sep='\n'),
}

del sys.argv[0]

if sys.argv == []:
	die("TODO: No command")

cmdstring = sys.argv.pop(0)
cmds = [c for c in commands.keys() if c.startswith(cmdstring)]
if len(cmds) == 0:
	die(cmdstring, "is not a known command")
elif len(cmds) > 1:
	die(cmdstring, "is ambiguous:", cmds)

try:
	commands[cmds[0]](sys.argv)
except Exception as e:
	die("Error:", e)
