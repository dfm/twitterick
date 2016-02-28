FROM python:3.5
ADD . /code
WORKDIR /code
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN python -m nltk.downloader cmudict
CMD python -u run.py
