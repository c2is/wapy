import gearman
import sysdialog
import pprint
import traceback

class GearmanWorker(gearman.GearmanWorker):
    def on_job_execute(self, current_job):
        sysdialog.logger.info("Job started, handle: " + current_job.handle + ", task:" + current_job.task + ", data: " + current_job.data)
        try:
            function_callback = self.worker_abilities[current_job.task]
            job_result = function_callback(self, current_job)
        except Exception:
            return self.on_job_exception(current_job, traceback.format_exc())

        return super(GearmanWorker, self).on_job_execute(current_job)

    def on_job_exception(self, current_job, exc_info):
        sysdialog.logger.error("Job failed " + current_job.handle + " : " + exc_info)
        sysdialog.redis_flow.append(current_job.handle, "<br>Wapistrano Job failed " + current_job.handle + " : " + exc_info)
        return super(GearmanWorker, self).on_job_exception(current_job, exc_info)

    def on_job_complete(self, current_job, job_result):
        sysdialog.logger.info("Job complete")
        sysdialog.redis_flow.append(current_job.handle, "<br>Wapistrano job ended")
        return super(GearmanWorker, self).send_job_complete(current_job, job_result)

    def after_poll(self, any_activity):
        return True

