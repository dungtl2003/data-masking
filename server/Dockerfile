FROM python:3.10-alpine@sha256:4c4097e46608e9b9025a486e3b72d628ac8947a3caa20f142c2e8c0029a12b21

WORKDIR /usr/src

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/usr/src

EXPOSE 80

CMD ["python", "app/main.py"]
