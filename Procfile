web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker chat.fastapi_server:app --bind 0.0.0.0:$PORT
