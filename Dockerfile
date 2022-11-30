FROM python:3.10

RUN mkdir -p /usr/src/get_order
WORKDIR /usr/src/get_order

COPY . /usr/src/get_order/
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]