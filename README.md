# Info

Test the live project at [Site](http://hypergraphrepository.di.unisa.it/)

## Datasets info

You can deeply investigate all the infos about datasets at [Repository](https://github.com/HypergraphRepository/datasets)

# RUNNING THE project

## requirements
- php
- composer
- env file (use .env.example as a template). the following variables need to be set:
  - DB_DATABASE
  - DB_USERNAME
  - DB_PASSWORD
  - GIT_USERNAME
  - GIT_TOKEN

# To run locally
```bash
composer install
php artisan migrate:fresh
cd website/storage/app/public && git clone https://github.com/HypergraphRepository/datasets && git config credential.helper store 
php artisan storage:link
php artisan serve
```

On first run, if you open the website, you will need to generate the api key through the button on landing page.
You can populate the database using the python script.

## python dependencies
pip install -r requirements.txt

you can generate a venv inside scripts folder and install the dependencies there:
```bash
python3.10 -m venv venv
. venv/bin/activate
pip3 install matplotlib python-dotenv requests mysql-connector-python
python3 -m pip install julia
```

# julia dependencies
to call julia from python, you need to install the julia python package:
```bash
python3 -m pip install --user julia
```
Then you need to start python3 shell and run:
```python
import julia
julia.install()
```

add Suppressor and SimpleHypergraph packages to julia through package manager


At the end you can check if you populate the database correctly by running inside scripts folder:
```bash
python3 checkRepo.py
```

You can pull update repository of dataset by running:
```bash
bash gitPull.sh
```

if you have setup correctly the repository, you can run the scheduler locally to activate the cron jobs:
```bash
php artisan schedule:work
```

# Docker build
```bash
docker compose up
```

To use the julia script, compile a custom system image for PyJulia, run
```bash
python3 -m julia.sysimage sys.so
```

To build a single service
```bash
docker compose build name_service
```

To run a command inside the docker
```bash
sudo docker exec -it hgraph php artisan schedule:test
```
