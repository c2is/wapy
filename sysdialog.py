# -*- coding: utf8 -*-
import sys
import os
import json
import ConfigParser
import signal
import subprocess
import logging
import redis
import time
from logging.handlers import RotatingFileHandler

def follow(thefile):
    global p
    c = 100
    thefile.seek(0, 2)
    while True:
        if p.poll() is not None:
             c = c -1
        if p.poll() is not None and c == 0:
            break
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

logger = logging.getLogger()
# set logger level to DEBUG, thus all will be written
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s {%(pathname)s:%(lineno)d} :: %(levelname)s :: %(message)s')
# file in 'append' mode, with 1 backup and a max size set to 10Mo
file_handler = RotatingFileHandler('/var/log/wapyd/wapyd.log', 'a', 10000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

config = ConfigParser.ConfigParser()
config.read('wapy.cfg')
projects_path = config.get('Capistrano', 'projects_path')
cap_command = config.get('Capistrano', 'cap_exec')
capify_command = config.get('Capistrano', 'capify_exec')
gearman_host = config.get('Gearman', 'host')
gearman_port = config.get('Gearman', 'port')

if config.get('Capistrano', 'cap_logger') == "redis":
    redis_host = config.get('Redis', 'host')
    redis_port = config.get('Redis', 'port')
    redis_pool = redis.ConnectionPool(host=redis_host, port=redis_port, db=0)
    redis_flow = redis.Redis(connection_pool=redis_pool)


def write_cap_file(job):
    dict = json.loads(job.data)
    proj_dir(dict.get("projectId"))
    file_path = projects_path + "/" + dict.get("projectId") + "/config/deploy/" + dict.get("stageId") + ".rb"
    capfile = open(file_path, "w")
    capfile.write(dict.get("content"))
    capfile.close()
    os.chmod(file_path, 0600)


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
            target_dir = projects_path + "/" + proj_id + "/"
            p = subprocess.Popen(capify_command + " " + target_dir, shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
        except OSError as e:
            logger.error("Command " + capify_command + " " + target_dir + " Return error: " + e.strerror)
        else:
            logger.info("Capified " + projects_path + "/" + proj_id)


def cap_log_append(job, line):
    if config.get('Capistrano', 'cap_logger') == "redis":
        global redis_flow
        redis_flow.append(job.handle, line)



def cap_work(gearman_worker, job):
    global p
    dict = json.loads(job.data)
    command_line = dict.get("capCommand").replace("cap", cap_command)
    command_line = command_line.replace("capify", capify_command)

    cap_log_append(job, command_line)
    logger.info("Executing cd " + projects_path + "/" + dict.get("projectId") + "; " + command_line)

    stdlogfile = dict.get("projectId") + command_line.replace(" ", "-").replace("/", "-") + ".log"
    errlogfile = dict.get("projectId") + command_line.replace(" ", "-").replace("/", "-") + "-error.log"
    stdoutput = open('/var/log/wapyd/' + stdlogfile, 'w+')
    erroutput = open('/var/log/wapyd/' + errlogfile, 'w+')

    p = subprocess.Popen(command_line.split(), shell=False, stdout=stdoutput,
                         stderr=stdoutput, cwd=projects_path + "/" + dict.get("projectId"))


    logfile = open('/var/log/wapyd/' + stdlogfile, "r")
    loglines = follow(logfile)
    for line in loglines:
        cap_log_append(job, line)

    logfile.close()
    stdoutput.close()
    erroutput.close()

    p.communicate()
    if p.returncode > 0:
        raise RuntimeError('CapistranoTaskFailed')

    logger.info("Execution terminated with return code " + str(p.returncode))


def signal_term_handler(signal, frame):
    logger.info("Worker stopped, sigterm sent")
    sys.exit(0)


signal.signal(signal.SIGTERM, signal_term_handler)