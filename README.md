# SIT_Chatbot
<img src="https://github.com/user-attachments/assets/02669964-06f3-4ee4-9f02-b29e5ba4b466" alt="image" width="500"/>

# 📂 Introduction

An intelligent chatbot system designed to streamline information retrieval for students at the Singapore Institute of Technology (SIT). This project compares chatbot efficiency against traditional website navigation by collecting and analyzing user interaction data.


## 🖼️ Preview



## ⚙️ Setup
### 1. Clone the repository

``` bash
git clone https://github.com/your-username/joey-books-search.git
cd joey-books-search
```

### 2. Install Dependencies

``` bash
pip install -r requirements.txt
```

### 3. Configure Your .env File

```python
NEXT_PUBLIC_GOOGLE_BOOKS_API=<your_api_url>
```

### 4. Run the Application

``` bash
chainlit run app.py
```

Now open http://localhost:3000 to use the app.


# 📁 Project Structure
``` Python
google-books-search
/src/app/
  ├─ page.js                      → Home (search page)
  └─ /book/[id]/page.js           → Book Page
/public/
  ├─ website_logo.png             → App logo
  └─ website_search_button.png    → Search Button logo
.env                              → Environment variables
favicon.ico                       → Favicon Logo
```
