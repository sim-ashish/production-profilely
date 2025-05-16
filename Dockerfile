FROM python:3.13-slim

ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*




COPY . .

RUN pip install -r requirements.txt



EXPOSE 8000


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]