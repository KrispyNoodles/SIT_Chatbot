# 📂 Introduction
An intelligent chatbot system built using Large Language Models (LLMs) and Retrieval Augemeneted Generation (RAG) to streamline information retrieval from the Singapore Institute of Technology (SIT) website. This project compares chatbot efficiency against traditional website navigation by collecting and analyzing user interaction data.

## 🖼️ Preview
### Chainlit Web Application
![Media1-ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/b1dfe031-57ee-4bf0-97aa-010660087a68)

### Telegram Chatbot
![Media2-ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/a2918412-ab26-4cb7-993c-d6b8664948bf)

## ⚙️ Setup
### 1. Clone the repository

``` bash
git clone https://github.com/KrispyNoodles/SIT_Chatbot.git
cd SIT_Chatbot
```

### 2. Install Dependencies

``` bash
pip install -r requirements.txt
```

### 3. Configure Your .env File, use the .env-sample as a reference of which variables to be adjusted

### 4. Run the Application (Chainlit)

``` bash
chainlit run app.py
```

### 4. Run the Application (Telegram)

``` bash
python tele.py
```

Now open http://localhost:8000 to use the chainlit app.

## 🐳 Containerization
This project can be containerized using Docker for easy deployment.

### Create the docker image
Run the following command in the root directory of the project to build the Docker image:

``` bash
docker build -t sit-chatbot .
```

### Run the docker file
Once the image is built, you can run the container using:

``` bash
docker run --env-file .env sit-chatbot
```
