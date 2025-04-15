FROM python:3.13.3-alpine
WORKDIR /usr/src/app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --root-user-action=ignore -r requirements.txt
COPY . .
CMD ["python", "main.py"]