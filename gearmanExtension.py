import gearman
import sysdialog
import pprint


class GearmanWorker(gearman.GearmanWorker):
    def on_job_execute(self, current_job):
        sysdialog.logger.info("Job started, task:" + current_job.task + ", data: " + current_job.data)
        return super(GearmanWorker, self).on_job_execute(current_job)

    def on_job_exception(self, current_job, exc_info):
        sysdialog.logger.info("Job failed " + exc_info)
        return super(GearmanWorker, self).on_job_exception(current_job, exc_info)

    def on_job_complete(self, current_job, job_result):
        sysdialog.logger.info("Job complete")
        return super(GearmanWorker, self).send_job_complete(current_job, job_result)

    def after_poll(self, any_activity):
        return True

