FROM python:3.10-slim

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed dependencies specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY . ..

# Run the bot when the container launches
CMD ["python", "main.py"]
