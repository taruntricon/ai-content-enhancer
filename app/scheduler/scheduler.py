from apscheduler.schedulers.background import BackgroundScheduler

from app.scheduler.jobs import fetch_unipile_comments_job

scheduler = BackgroundScheduler()


def start_scheduler():
    if scheduler.running:
        return

    scheduler.add_job(
        fetch_unipile_comments_job,
        trigger="interval",
        # minutes=1,
        hours=2,
        id="unipile_comments_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    scheduler.start()

    print("Scheduler started successfully")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)

        print("Scheduler stopped")
