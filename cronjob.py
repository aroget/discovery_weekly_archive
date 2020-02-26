from apscheduler.schedulers.blocking import BlockingScheduler

from main import run

# Create an instance of scheduler and add function.
scheduler = BlockingScheduler()
# scheduler.add_job(run, "cron", day_of_week='0', hour='9')
scheduler.add_job(run, "cron", day='*', hour="9")

scheduler.start()
