FROM python:3.13-slim AS heavy

ENV PIP_ROOT_USER_ACTION=ignore

RUN pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    ultralytics opencv-python-headless pillow


FROM python:3.13-slim AS api

WORKDIR /app

ENV PIP_ROOT_USER_ACTION=ignore


COPY requirements-api.txt .


RUN pip install --no-cache-dir -r requirements-api.txt


COPY --from=heavy /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

COPY api/ api/
COPY db/ db/
COPY images/ images/

CMD ["python", "-m", "api.auth_api"]
