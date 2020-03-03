from apscheduler.schedulers.blocking import BlockingScheduler

from main import run


# Create an instance of scheduler and add function.
scheduler = BlockingScheduler()
func_args = ['aroget', 'Discover Weekly', 'Discovery Weekly Archive']
scheduler.add_job(run, "cron", func_args, day_of_week='0', hour='9')

scheduler.start()
