FROM python:latest

EXPOSE 4321

WORKDIR /dashboard

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY dashboard.py . 

ENTRYPOINT ["streamlit", "run", "dashboard.py", "--server.port=4321", "--server.address=0.0.0.0", "--theme.primaryColor=#B99470", "--theme.backgroundColor=#FAF1E4", "--theme.secondaryBackgroundColor=#5F6F52"]
