import psycopg
import os
from os.path import dirname, abspath
from dotenv import load_dotenv
load_dotenv()
import uuid
import requests
import datetime
from julia import Julia
jl = Julia(sysimage="scripts/sys.so")
from julia import Main

Main.include("scripts/hypergraphs.jl")

DB_U= os.getenv("DB_USERNAME")
DB_P= os.getenv("DB_PASSWORD")
DB_D= os.getenv("DB_DATABASE")
DB_H= os.getenv("DB_HOST")
GIT_U= os.getenv("GIT_USERNAME")
GIT_T= os.getenv("GIT_TOKEN")
# repo in same root
# d = dirname(dirname(dirname(abspath(__file__))))
# datasets = d + "/datasets"

print("Executed at: ", datetime.datetime.now())

d = dirname(dirname(abspath(__file__)))
datasets = d + "/storage/app/public/datasets"

############################
# add empty category if not present
cnxEmpty = psycopg.connect(host=DB_H, user=DB_U, password=DB_P, dbname=DB_D)
category = "empty"
search_empty = ("SELECT * FROM categories WHERE type = '"+category+"'")
cursor = cnxEmpty.cursor()
cursor.execute(search_empty)
result = cursor.fetchall()
if len(result) == 0:
    myuuid_empty_category = uuid.uuid4()
    cursor = cnxEmpty.cursor()
    add_category = ("INSERT INTO categories (id, type)"
                    " VALUES ('"+str(myuuid_empty_category)+"', '"+str(category)+"')")
    cursor.execute(add_category)
    cnxEmpty.commit()
cnxEmpty.close()
############################

############################
# delete old hgraphs who are not in the repo anymore
cnx = psycopg.connect(host=DB_H, user=DB_U, password=DB_P, dbname=DB_D)
search_hgraph = ("SELECT name FROM hgraphs")
cursor = cnx.cursor()
cursor.execute(search_hgraph)
result = cursor.fetchall()
cnx.close()
list_hgraph_db = []
list_hgraph_repo = []
for row in result:
    list_hgraph_db.append(row[0])
for filename in os.listdir(datasets):
    f = os.path.join(datasets, filename)
    if os.path.isdir(f) and not filename.startswith(".") and not filename == "scripts":
        list_hgraph_repo.append(filename)
for hgraph in list_hgraph_db:
    if hgraph not in list_hgraph_repo:
        print("deleting ", hgraph)
        cnx = psycopg.connect(host=DB_H, user=DB_U, password=DB_P, dbname=DB_D)
        cursor = cnx.cursor()
        delete_hgraph = ("DELETE FROM hgraphs WHERE name = '"+str(hgraph)+"'")
        cursor.execute(delete_hgraph)
        cnx.commit()
        cnx.close()
############################

for filename in os.listdir(datasets):
    f = os.path.join(datasets, filename)
    # checking if it is a directory and not a hidden directory
    if os.path.isdir(f) and not filename.startswith(".") and not filename == "scripts":        
        for files in os.listdir(f):      
            if files.endswith(".hgf"):
                apiCall = "https://api.github.com/repos/HypergraphRepository/datasets/commits?path=" + filename + "/" + filename + ".hgf"
                response = requests.get(apiCall, auth=(GIT_U, GIT_T))
                res = response.json()
                cnx = psycopg.connect(host=DB_H, user=DB_U, password=DB_P, dbname=DB_D)
                # sql query to search for the name of the folder
                search_hgraph = ("SELECT * FROM hgraphs WHERE name = '"+str(filename)+"'")
                cursor = cnx.cursor()
                cursor.execute(search_hgraph)
                result = cursor.fetchall()
                if len(result) == 0:
                    # if the folder name is not in the database, add it
                    myuuid = uuid.uuid4()
                    res = response.json()
                    last = len(res)-1
                    first_commit = res[last]
                    author = first_commit['commit']['author']['name']
                    author_url = first_commit['author']['html_url']
                    first_commit_date = first_commit['commit']['author']['date']
                    last_commit = res[0]
                    last_commit_date = last_commit['commit']['author']['date']
                    
                    created_at = first_commit_date.replace("T", " ")
                    created_at = created_at.replace("Z", "")
                    update_at = last_commit_date.replace("T", " ")
                    update_at = update_at.replace("Z", "")

                    # read the file
                    categories_path = "./storage/app/public/datasets/" + filename + "/categories.info"
                    # if the file is not present, create it
                    categories_empty = "empty"
                    domain = "empty"
                    if os.path.isfile(categories_path):
                        read = open(categories_path, "r").read()
                        # read = read.replace("\n", ", ")
                        # # remove last comma
                        # read = read[:-2]
                        # categories = str(read)
                        categories = read.split("\n")
                        my_domain = categories[0]
                        domain = my_domain
                        # exclude first two lines
                        for category in categories[2:]:
                            if category == "":
                                continue
                            else:
                                # check if the category is already in the database
                                search_category = ("SELECT * FROM categories WHERE type = '"+str(category)+"'")
                                cursor = cnx.cursor()
                                cursor.execute(search_category)
                                result_category = cursor.fetchall()

                                myuuid_category = ""
                                if len(result_category) == 0:
                                    # if the category is not in the database, add it
                                    myuuid_category = uuid.uuid4()
                                    cursor = cnx.cursor()
                                    add_category = ("INSERT INTO categories (id, type)"
                                                    " VALUES ('"+str(myuuid_category)+"', '"+str(category)+"')")
                                    cursor.execute(add_category)
                                    cnx.commit()
                                else:
                                    # if the category is in the database, get the id
                                    myuuid_category = result_category[0][0]

                                # insert the category in the hgraph_categories table
                                cursor = cnx.cursor()
                                myuuid_hgraph_category = uuid.uuid4()
                                add_hgraph_category = ("INSERT INTO hgraphs_categories (id, hgraph_id, category_id)"
                                                " VALUES ('"+str(myuuid_hgraph_category)+"', '"+str(myuuid)+"', '"+str(myuuid_category)+"')")
                                cursor.execute(add_hgraph_category)
                    else:
                        # add empty category
                        search_category = ("SELECT * FROM categories WHERE type = '"+str(categories_empty)+"'")
                        cursor = cnx.cursor()
                        cursor.execute(search_category)
                        result_category = cursor.fetchall()
                        myuuid_hgraph_category = uuid.uuid4()
                        # print(result_category)
                        myuuid_category = result_category[0][0]
                        add_hgraph_category = ("INSERT INTO hgraphs_categories (id, hgraph_id, category_id)"
                                                " VALUES ('"+str(myuuid_hgraph_category)+"', '"+str(myuuid)+"', '"+str(myuuid_category)+"')")
                        cursor.execute(add_hgraph_category)



                    descr = "./storage/datasets/" + filename + "/README.md"
                    # url = "https://github.com/HypergraphRepository/datasets" + filename + "/" + filename + ".hgf"
                    url = "https://hypergraphrepository.di.unisa.it/download/" + filename
                    pathToHg = "./storage/app/public/datasets/" + filename + "/" + filename + ".hgf"
                    (nodes, edges, avg_node_degree, avg_edge_degree, distribution_node_degree, distribution_edge_size, node_degree_max, edge_degree_max, distribution_node_degree_hist, distribution_edge_size_hist) = Main.collect_infos(pathToHg)
                    # sort distribution in ascending order

                    distribution_node_degree.sort(reverse=True)
                    distribution_node_degree = ",".join(str(x) for x in distribution_node_degree)
                    distribution_edge_size.sort(reverse=True)
                    distribution_edge_size = ",".join(str(x) for x in distribution_edge_size)
                    summary = "test summary"
                    add_hgraph= ("INSERT INTO hgraphs (id, name, summary, domain, author, authorurl, nodes, edges, dnodemax, dedgemax, dnodeavg, dedgeavg, dnodes, dedges, dedgeshist, dnodeshist, url, description, created_at, updated_at)"
                                #  " VALUES ('"+str(myuuid)+"', '"+str(filename)+"','" + author + "','" + str(nodes) + "','" + str(edges) + "','" + str(node_degree_max) + "','" + str(edge_degree_max) + "','" + str(avg_node_degree) + "','" + str(avg_edge_degree) + "','" + str(distribution_node_degree) + "','" + str(distribution_edge_size) + "','" + url +"', '" + categories + "','" + str(descr) + "','"+str(created_at)+"', '"+str(update_at)+"')")
                                    " VALUES ('"+str(myuuid)+"', '"+str(filename)+"','" + str(summary) + "','" + str(domain) + "','" + author + "','" + author_url + "','" + str(nodes) + "','" + str(edges) + "','" + str(node_degree_max) + "','" + str(edge_degree_max) + "','" + str(avg_node_degree) + "','" + str(avg_edge_degree) + "','" + str(distribution_node_degree) + "','" + str(distribution_edge_size) + "','" + str(distribution_edge_size_hist) + "','" + str(distribution_node_degree_hist) + "','" + url +"', '" + str(descr) + "','"+str(created_at)+"', '"+str(update_at)+"')")
                        # " VALUES ('"+str(myuuid)+"', '"+str(filename)+"','" + author + "','" + str(nodes) + "','" + str(edges) + "','" + url +"', '" + categories + "','" + str(descr) + "','"+str(created_at)+"', '"+str(update_at)+"')")    
                    cursor.execute(add_hgraph)
                    cnx.commit()
                else:
                    # last commit on the file
                    res = res[0]
                    author = res['commit']['author']['name']
                    date = res['commit']['author']['date']
                    # format date
                    date = date.replace("T", " ")
                    date = date.replace("Z", "")

                    # check if the date is different
                    db_row_UpdatedAt = len(result[0])-1
                    db_row_createdAt = len(result[0])-2

                    if str(result[0][db_row_UpdatedAt]) != str(date):
                        # i have to update all the data
                        cursor = cnx.cursor()
                        update_hgraph = ("UPDATE hgraphs SET updated_at = '"+str(date)+"' WHERE name = '"+str(filename)+"'")
                        cursor.execute(update_hgraph)
                        cnx.commit()

                        pathToHg = "./storage/app/public/datasets/" + filename + "/" + filename + ".hgf"
                        (nodes, edges, avg_node_degree, avg_edge_degree, distribution_node_degree, distribution_edge_size, node_degree_max, edge_degree_max) = Main.collect_infos(pathToHg)
                        
                        distribution_node_degree.sort(reverse=True)
                        distribution_node_degree = ",".join(str(x) for x in distribution_node_degree)
                        distribution_edge_size.sort(reverse=True)
                        distribution_edge_size = ",".join(str(x) for x in distribution_edge_size)
                        update_hgraph_stats = ("UPDATE hgraphs SET nodes = '"+str(nodes)+"', edges = '"+str(edges)+"' WHERE name = '"+str(filename)+"'")
                        cursor.execute(update_hgraph_stats)
                        cnx.commit()
                
                cnx.close()

            if files.endswith(".md"):
                print("md file")

            if files.endswith(".info"):
                print("info file")
                