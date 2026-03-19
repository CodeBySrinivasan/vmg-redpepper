# Use a standard Python image
FROM python:3.9

# Set the folder where our code lives
WORKDIR /code

# Install the tools from our requirements file
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your main.py and index.html into the server
COPY . .

# Start the Python server on Port 7860 (Hugging Face's favorite port)
CMD ["python", "main.py"]