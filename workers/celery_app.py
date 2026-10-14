import os
from celery import Celery

app=Celery("verigraph",broker=os.getenv("REDIS_URL","redis://redis:6379/0"),backend=os.getenv("REDIS_URL","redis://redis:6379/0"))
app.conf.update(task_track_started=True,task_time_limit=int(os.getenv("SANDBOX_TIMEOUT_SECONDS","120")),worker_prefetch_multiplier=1)

@app.task(name="verigraph.health")
def health()->dict[str,str]:return {"status":"ok"}

