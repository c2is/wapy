import gearman
import time


gm_worker = gearman.GearmanWorker(['localhost:4730'])

# See gearman/job.py to see attributes on the GearmanJob
# Send back a reversed version of the 'data' string
def task_listener_reverse(gearman_worker, gearman_job):
    gearman_worker.send_job_data(gearman_job, "a-")
    time.sleep(6)
    return "Yep sincou, t'as vu ?" + gearman_job.data

# gm_worker.set_client_id is optional
gm_worker.set_client_id('your_worker_client_id_name')
gm_worker.register_task('reverse', task_listener_reverse)

# Enter our work loop and call gm_worker.after_poll() after each time we timeout/see socket activity
gm_worker.work()