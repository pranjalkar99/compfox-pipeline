# Use the official Python 3.11 image as the base image
FROM python:3.11


# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY  requirements.txt .
COPY last_done.txt .
COPY split.py .
COPY upload_gcp.py .
Copy compfox-367313-0c3890a157f2.json .

RUN pip install --upgrade pip

# Install the Python dependencies
RUN pip install -r requirements.txt

# Copy the test.py file to the container
COPY pipeline.py .

# Set the entrypoint command to run your FastAPI app
CMD ["uvicorn", "pipeline:app", "--host", "0.0.0.0"]
