import gearman
import sysdialog
import pprint


class GearmanWorker(gearman.GearmanWorker):
    def on_job_execute(self, current_job):
        sysdialog.logger.info("Job started, handle: " + current_job.handle + ", task:" + current_job.task + ", data: " + current_job.data)
        return super(GearmanWorker, self).on_job_execute(current_job)

    def on_job_exception(self, current_job, exc_info):
        sysdialog.logger.error("Job failed " + current_job.handle + " : " + str(exc_info))
        sysdialog.redis_flow.append(current_job.handle, "<br>Wapistrano Job failed " + current_job.handle + " : " + str(exc_info))
        return super(GearmanWorker, self).on_job_exception(current_job, exc_info)

    def on_job_complete(self, current_job, job_result):
        sysdialog.logger.info("Job complete")
        sysdialog.redis_flow.append(current_job.handle, "<br>Wapistrano job ended")
        return super(GearmanWorker, self).send_job_complete(current_job, job_result)

    def after_poll(self, any_activity):
        return True

