from almonds.app import create_app, task_scheduler

if __name__ == "__main__":

    bg_tasks = task_scheduler()
    bg_tasks.start()

    app = create_app()
    app.run(host="0.0.0.0")
