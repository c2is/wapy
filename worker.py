import time
import gearmanExtension
import sysdialog
import sys

sysdialog.logger.info("Worker started, waiting for job...")
gm_worker = gearmanExtension.GearmanWorker(['localhost:4730'])

# See gearman/job.py to see attributes on the GearmanJob
# Send back a reversed version of the 'data' string
def task_publish_stage(gearman_worker, gearman_job):
    sysdialog.write_cap_file()
    gearman_worker.send_job_status(gearman_job, 4, 4)

    #return "Yep sincou, t'as vu ?" + gearman_job.data
    return "Yep sincou, t'as vu ?"

# gm_worker.set_client_id is optional
gm_worker.set_client_id('your_worker_client_id_name')
gm_worker.register_task('publish_stage', task_publish_stage)

# Enter our work loop and call gm_worker.after_poll() after each time we timeout/see socket activity
gm_worker.work()

sysdialog.logger.info("Worker stopped")
