# 📂 Introduction
An intelligent chatbot system built using Large Language Models (LLMs) and Retrieval Augemeneted Generation (RAG) to streamline information retrieval from the Singapore Institute of Technology (SIT) website. This project compares chatbot efficiency against traditional website navigation by collecting and analyzing user interaction data.

## 🖼️ Preview

![BT_video_demo-ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/29d011f5-52d0-4bad-a1a4-fb0a2524ad57)
![BT_tele_video_demo-ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/69070d7d-71f9-47ae-ab84-8a4faa63476b)

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
