# Base image
FROM ubuntu:22.04

# install python
RUN apt-get update && apt-get install -y python3 python3-pip

# Set the working directory in the container
WORKDIR /chat_bot

# Copy the local files into the container
COPY . /chat_bot

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Run the script
# CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8000"]

# Command to run Chainlit with the python file
CMD ["sh", "-c", "chainlit run app.py --host 0.0.0.0 --port 8000 & python3 tele.py"]
