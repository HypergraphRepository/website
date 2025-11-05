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

list_computed_dataset = []
with open("./storage/logs/motifs.log") as f:
	for line in f:
		if line.startswith("run_approx_ver2_par.sh:") or line.startswith("Executed") or "killed" in line:
			continue
		name = line.split(',')[0]
		list_computed_dataset.append(name)

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
				p = subprocess.Popen(['bash', 'run_approx_ver2_par.sh', './motifs/' + output_filename + '.txt'], cwd=mochy_path)
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