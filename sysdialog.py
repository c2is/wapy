# -*- coding: utf8 -*-
import sys
import os
import json
import ConfigParser
import signal
import subprocess
import logging
import redis
from logging.handlers import RotatingFileHandler


logger = logging.getLogger()
# on met le niveau du logger à DEBUG, comme ça il écrit tout
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
# fichier en mode 'append', avec 1 backup et une taille max de 10Mo
file_handler = RotatingFileHandler('/var/log/wapyd.log', 'a', 10000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
# création d'un second handler qui va rediriger chaque écriture de log
# sur la console
#steam_handler = logging.StreamHandler()
#steam_handler.setLevel(logging.DEBUG)
#logger.addHandler(steam_handler)
# levels : CRITICAL ERROR WARNING INFO DEBUG
# example logger.info('Hello')

config = ConfigParser.ConfigParser()
config.read('wapy.cfg')
projects_path = config.get('Capistrano', 'projects_path')
cap_command = config.get('Capistrano', 'cap_exec')
capify_command = config.get('Capistrano', 'capify_exec')
gearman_host = config.get('Gearman', 'host')
gearman_port = config.get('Gearman', 'port')
redis_host = config.get('Redis', 'host')
redis_port = config.get('Redis', 'port')

redis_pool = redis.ConnectionPool(host=redis_host, port=redis_port, db=0)
redis_flow = redis.Redis(connection_pool=redis_pool)


def write_cap_file(job):
    dict = json.loads(job.data)
    proj_dir(dict.get("projectId"))
    capfile = open(projects_path + "/" + dict.get("projectId") + "/config/deploy/" + dict.get("stageId") + ".rb", "w")
    capfile.write(dict.get("content"))
    capfile.close()


def delete_stage(job):
    dict = json.loads(job.data)
    os.unlink(projects_path + "/" + dict.get("projectId") + "/config/deploy/" + dict.get("stageId") + ".rb")


def proj_dir(proj_id):
    if not os.path.isdir(projects_path + "/" + proj_id):
        try:
            os.mkdir(projects_path + "/" + proj_id )
        except OSError:
            logger.error("Cannot create dirs in " + projects_path + "/" + proj_id)
        else:
            os.mkdir(projects_path + "/" + proj_id + "/config")
            os.mkdir(projects_path + "/" + proj_id + "/config/deploy")
            multistage_file = open(projects_path + "/" + proj_id + "/config/deploy.rb", "w")
            multistage_file.write("require 'capistrano/ext/multistage'")
            multistage_file.close()

    if not os.path.isfile(projects_path + "/" + proj_id + "/Capfile"):
        try:
            p = subprocess.Popen(capify_command + " "+ projects_path + "/" + proj_id, shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
        except OSError:
            logger.error("Cannot capify dir " + projects_path + "/" + proj_id)
        else:
            logger.info("Capified " + projects_path + "/" + proj_id)


def p_work(job):
    global redis_flow
    p = subprocess.Popen("ls -alrt", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #print p.communicate()[0]
    for line in iter(p.stdout.readline, ''):
        redis_flow.append(job.handle, "<br>" + line.rstrip())


def cap_work(gearman_worker, job):
    global redis_flow
    dict = json.loads(job.data)
    command_line = dict.get("capCommand").replace("cap", cap_command)
    command_line = command_line.replace("capify", capify_command)

    logger.info("Executing cd " + projects_path + "/" + dict.get("projectId") + "; " + command_line)
    p = subprocess.Popen("cd " + projects_path + "/" + dict.get("projectId") + "; " + command_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for line in iter(p.stdout.readline, ''):
        redis_flow.append(job.handle, "<br>" + line.rstrip())
        logger.info(line.rstrip())

    error = False
    for line in iter(p.stderr.readline, ''):
        error = True
        redis_flow.append(job.handle, "<br>" + line.rstrip())
        logger.error(line.rstrip())

    if error:
        raise RuntimeError('CapistranoTaskFailed')

    logger.info("Execution terminated with return code ")


def signal_term_handler(signal, frame):
    logger.info("Worker stopped, sigterm sent")
    sys.exit(0)


signal.signal(signal.SIGTERM, signal_term_handler)




