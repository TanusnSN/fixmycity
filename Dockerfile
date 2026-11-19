FROM python:3.11-slim
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
RUN mkdir -p uploads
EXPOSE 8000
CMD ["sh", "-c", "python -m app.create_admin && if [ \"$SEED_DEMO_DATA\" = \"true\" ]; then python -m app.seed; fi; uvicorn app.main:app --host 0.0.0.0 --port 8000"]