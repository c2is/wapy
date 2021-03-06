#!/usr/bin/env python
import time
import gearmanExtension
import sysdialog
import sys

sysdialog.logger.info("Worker started, waiting for job...")
gm_worker = gearmanExtension.GearmanWorker([sysdialog.gearman_host + ":" + sysdialog.gearman_port])


# See gearman/job.py to see attributes on the GearmanJob
def task_publish_stage(gearman_worker, gearman_job):
    sysdialog.redis_flow.set(gearman_job.handle, "Writing ruby file")
    # time.sleep(20)

    sysdialog.write_cap_file(gearman_job)
    # sysdialog.logger.info("Handler : " + gearman_job.handle)
    sysdialog.redis_flow.append(gearman_job.handle, "Ruby file wrote")
    gearman_worker.send_job_status(gearman_job, 4, 4)

    return ""


def task_cap_command(gearman_worker, gearman_job):
    sysdialog.redis_flow.set(gearman_job.handle, "Launch cap command")

    sysdialog.cap_work(gearman_worker, gearman_job)
    gearman_worker.send_job_status(gearman_job, 4, 4)

    return ""


def task_delete_stage(gearman_worker, gearman_job):
    sysdialog.redis_flow.set(gearman_job.handle, "Deleting command")

    sysdialog.delete_stage(gearman_job)
    gearman_worker.send_job_status(gearman_job, 4, 4)

    return ""

# gm_worker.set_client_id is optional
gm_worker.set_client_id('python_worker ' + str(sys.argv[1]))
gm_worker.register_task('publish_stage', task_publish_stage)
gm_worker.register_task('delete_stage', task_delete_stage)
gm_worker.register_task('cap_command', task_cap_command)

# Enter our work loop and call gm_worker.after_poll() after each time we timeout/see socket activity
gm_worker.work()

sysdialog.logger.info("Worker stopped")
