
FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /teste_python
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip --no-cache-dir install -r requirements.txt
COPY . /teste_python