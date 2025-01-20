from apscheduler.schedulers.background import BackgroundScheduler
import datetime

scheduler = BackgroundScheduler()

def print_message():
    print(f"hello world at {datetime.datetime.now()}")

scheduler.add_job(print_message, 'interval', seconds=5)

if __name__ == '__main__':
    print("Starting scheduler...")
    scheduler.start()

    input("Press Enter to exit...\n")
    scheduler.shutdown()
    print("Scheduler stopped.")

# Created/Modified files during execution:
print([])