FROM python:latest

COPY requirements.txt .

RUN pip install -r requirements.txt
RUN python -m pip install 'boto3-stubs[essential]'

COPY transfer_old_data.py .

CMD python3 transfer_old_data.py

