#!/usr/bin/env python
from __future__ import print_function
import os
import pickle as pickle
from colorama import Fore, Back, Style
joinversion = 0.2

ignore_list_file = ['.DS_Store']
ignore_list_dirs = []


def log(msg):
	print("log: " + str(msg))
	with open("log", "a") as log:
		log.write(msg)

def initlog(target):
	log("____"*10 + "\n")
	log("Start session\n")
	log("pack version: ")
	log(str(joinversion)+"\n")
	log("ignoring files:")
	for i in ignore_list_file:
		log( " " + str(i))
	log("\nand folders: ")
	for i in ignore_list_dirs:
		log( str(i) + "\n")
	log("\n")
	log("..."*3+"\n")
def endlog():
	log("End session\n\n")

def join(jli,target,dir_list, out_filename = None, chunksize=64*1024):

	if not out_filename:
		out_filename = target[:-1:] + ".dat"
	meta = [chunksize, joinversion, target]

	log("output -> " + str(out_filename)+"\n")
	log("chunksize: " + str(meta[0])+" joinversion: " + str(meta[1]))
	log(" target: " + str(target) + "\n")

	with open(out_filename, "wb") as outfile:

		print("writing to ", out_filename)
		pickle.dump(meta, outfile)
		pickle.dump(dir_list, outfile)
		pickle.dump([target + i[5::] for i in jli], outfile)

		for fname in jli:

			log("> " + str(fname) + "\n")
			filesize = os.path.getsize(fname)
			loops = int(filesize/chunksize)

			if filesize%chunksize != 0:
				loops += 1
			if loops == 0:
				loops += 1
				log("empty file: " + str(fname) + "\n")

			file_meta = [target + fname[5::], filesize, loops]
			log("	s: " + str(filesize) + " l: " + str(loops) + "\n")
			pickle.dump(file_meta, outfile)
			log("	s")
			with open(fname, "rb") as infile:

				counter = 0
				while True:

					chunk = infile.read(chunksize)
					if(len(chunk) < chunksize):
						chunk += ' '*(chunksize - len(chunk))
						outfile.write(chunk)
						counter += 1
						break

					elif(len(chunk) == 0):  #looks fishy, is elif required? rtn works with if too...
						if(loops != 0):
							break
						chunk = ' '*chunksize  # prevents skipping empty files
					outfile.write(chunk)
					counter += 1

				if(counter != loops):
					log("	Error c: " + str(counter) + " l: " + str(loops) + "\n")
			log("	d\n")
	log("complete\n")
	log("joined " + str(len(jli)) + " files and")
	log(str(len(dir_list)) + " directories\n")

def pack(target):

	dir_list = []
	file_list = []

	for (dirpath, dirname, filenames) in os.walk("./in/"):

		dir_list.append(target + dirpath[5::])
		for i in filenames:
			if i in ignore_list_file: continue
			file_list.append(dirpath+ '/' + i)

	initlog(target)
	join(file_list, str(target), dir_list)
	endlog()

def extract(in_filename):

	print("extracting from "+ str(in_filename)+"\n")
	with open(in_filename, "rb") as infile:

		meta = pickle.load(infile)
		dir_list = pickle.load(infile)
		if meta[1] != joinversion:
			log("incorrect version; using " + str(joinversion) + " obtained " + str(meta[1]) + "\n")
			exit(1)

		chunksize = meta[0]
		file_list = pickle.load(infile)
		for fname in file_list:

			log("< " + str(fname) + "\n")
			with open(fname, "wb") as outfile:

				file_meta = pickle.load(infile)
				if(file_meta[0] != fname):
					log("Infile Corrupt; Abort\n")
					return

				filesize = file_meta[1]
				loops = file_meta[2]
				log("	s: " + str(filesize) + " l: " + str(loops) + "\n")

				log("	e")
				for i in range(loops):
					chunk = infile.read(chunksize)
					outfile.write(chunk)
				outfile.truncate(filesize)
				log("	d\n")
	log("extracted " + str(len(file_list)) + " files and ")
	log(str(len(dir_list)) + " directories\n")

def unpack(in_filename):

	with open(in_filename, "rb") as infile:

		meta = pickle.load(infile)
		initlog(str(meta[2]))
		log(str(in_filename) + " -> input" +"\n")
		#os.remove((meta[2][2::])[:-1:])
		try:
			os.system("rmdir " + str(meta[2]))
			os.system("rm -r " + str(meta[2]))

		except:
			print("directory ", str(meta[2]), " exists, move it to another location and try again")
			log("dir exists: " + str(meta[2]) + "\n")
			pass #os.system() doesn't catch errors :p

		log("reading dir structure...\n")
		dir_list = pickle.load(infile)
		for i in dir_list:
			os.makedirs(i)
		log("created directories\n")


	extract(in_filename)
	endlog()

#pack("./pack/")
#unpack("./pack.dat")
