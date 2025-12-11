import os, sys, re
from os.path import dirname, abspath
import subprocess
import psycopg
import os
from dotenv import load_dotenv
load_dotenv()
import uuid
import datetime

print("Executed at: ", datetime.datetime.now())

DB_U= os.getenv("DB_USERNAME")
DB_P= os.getenv("DB_PASSWORD")
DB_D= os.getenv("DB_DATABASE")
DB_H= os.getenv("DB_HOST")

d = dirname(dirname(abspath(__file__)))
mochy_path = d + "/storage/app/public/MoCHy"
datasets = d + "/storage/app/public/datasets"

if not os.path.exists(mochy_path):
	print("Mochy directory not found")
	exit()

def dataset_to_compute():
	# select all hgraphs where motifsdist is null
	cnx = psycopg.connect(host=DB_H, user=DB_U, password=DB_P, dbname=DB_D)
	cursor = cnx.cursor()
	search_hgraphs = ("SELECT name FROM hgraphs WHERE motifsdist IS NULL")
	cursor.execute(search_hgraphs)
	hgraphs = cursor.fetchall()
	dataset_list = []
	for hgraph in hgraphs:
		dataset_list.append(hgraph[0])
	print("Found ", len(dataset_list), " datasets to compute motifs for.")
	return dataset_list

def create_mochy_input(input_path, datataset_name):
	with open(input_path) as infile, open(mochy_path + "/motifs/" + datataset_name + ".txt", 'w') as outfile:
		first = True
		for line in infile:
			if first:
				first = False
				continue
			if not line.strip(): continue
			numbers = re.findall(r'\d+', line)
			line = ','.join(numbers) + '\n'
			outfile.write(str(line))

to_compute_dataset = dataset_to_compute()
print("Datasets to compute motifs for: ", to_compute_dataset)

for ds in to_compute_dataset:
	if not os.path.exists(os.path.join(mochy_path, "motifs", ds + ".txt")):
		# print("Motifs file for dataset ", ds, " not found, skipping.")
		create_mochy_input(os.path.join(datasets, ds, ds + ".hgf"), ds)
	
	with open(os.path.join(datasets, ds, ds + ".hgf")) as f:
		line = f.readline()
		num_nodes, num_edges = map(int, re.findall(r'\d+', line))

	ds_path = os.path.join(mochy_path, "motifs", ds + ".txt")
	if num_nodes > 100000 or num_edges > 100000:
		print("Dataset ", ds, " is too large (nodes: ", num_nodes, ", edges: ", num_edges, "), skipping exact computation.")
		#p = subprocess.Popen(['bash', 'run_exact2.sh', ds_path], cwd=mochy_path)
		continue
	else:
		p = subprocess.Popen(['bash', 'run_approx_ver2_par.sh', ds_path], cwd=mochy_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

	output, errors = p.communicate()
	ret = p.returncode
	if ret is not None and ret < 0:
		try:
			os.remove(os.path.join(mochy_path, "motifs", ds + ".txt"))
		except OSError:
			pass
	
	motif_dist = output
	cnx = psycopg.connect(host=DB_H, user=DB_U, password=DB_P, dbname=DB_D)
	cursor = cnx.cursor()
	name = motif_dist.split(',')[0]
	motifs = ','.join(motif_dist.split(',')[1:])
	insert_motifs = ("UPDATE hgraphs SET motifsdist = '"+str(motifs)+"' WHERE name = '"+str(name)+"'")
	cursor.execute(insert_motifs)
	cnx.commit()
	update_hgraph = ("UPDATE hgraphs SET updated_at = NOW() WHERE name = '"+str(name)+"'")
	cursor.execute(update_hgraph)
	cnx.commit()

print("\n----Motif computation completed----\n")

def old_compute():
	# list_computed_dataset = []
	# with open("./storage/logs/motifs.log") as f:
	# 	for line in f:
	# 		if line.startswith("run_approx_ver2_par.sh:") or line.startswith("Executed") or "killed" in line:
	# 			continue
	# 		name = line.split(',')[0]
	# 		list_computed_dataset.append(name)
	for subdir, dirs, files in os.walk(datasets):
		files = sorted(files)
		for filename in files:
			input_path = os.path.join(subdir, filename)
			if input_path.endswith(".hgf"):
				output_filename = filename.split(".")[0]
				# if we haven't already calculated the motifs for this hgf
				if not os.path.exists(mochy_path + "/motifs/" + output_filename + ".txt"):
					with open(input_path) as infile, open(mochy_path + "/motifs/" + output_filename + ".txt", 'w') as outfile:
						first = True
						for line in infile:
							if first:
								first = False
								continue
							if not line.strip(): continue
							numbers = re.findall(r'\d+', line)
							line = ','.join(numbers) + '\n'
							outfile.write(str(line))

				if output_filename not in list_computed_dataset:
					# p = subprocess.Popen(['bash', 'run_approx_ver2_par.sh', './motifs/' + output_filename + '.txt'], cwd=mochy_path)
					ret = p.wait()
					if ret is not None and ret < 0:
						try:
							os.remove(os.path.join(mochy_path, "motifs", output_filename + ".txt"))
						except OSError:
							pass

				cnx = psycopg.connect(host=DB_H, user=DB_U, password=DB_P, dbname=DB_D)
				cursor = cnx.cursor()
				with open("./storage/logs/motifs.log") as f:
					for line in f:
						# first element before comma is the name
						if line.startswith("run_approx_ver2_par.sh:") or line.startswith("Executed") or "killed" in line:
								continue
						name = line.split(',')[0]
						# put all the elements after the first comma in a string
						motifs = ','.join(line.split(',')[1:])
						insert_motifs = ("UPDATE hgraphs SET motifsdist = '"+str(motifs)+"' WHERE name = '"+str(name)+"'")
						cursor.execute(insert_motifs)
						cnx.commit()
						update_hgraph = ("UPDATE hgraphs SET updated_at = NOW() WHERE name = '"+str(name)+"'")
						cursor.execute(update_hgraph)
						cnx.commit()
				

					# check if value is "" or the hypergraph has been updated
					# cnx = psycopg.connect(host=DB_H, user=DB_U, password=DB_P, dbname=DB_D)
					# cursor = cnx.cursor()
					# search_motifs = ("SELECT motifsdist FROM hgraphs WHERE name = '"+str(output_filename)+"'")
					# cursor.execute(search_motifs)
					# motifs = cursor.fetchone()