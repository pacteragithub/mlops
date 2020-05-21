FROM python:3.6

# Set up and activate virtual environment
ENV VIRTUAL_ENV = /venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH = $VIRTUAL_ENV/bin:$PATH

# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt