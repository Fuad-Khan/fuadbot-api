


## 🚀 Live URL

Backend (FastAPI) hosted on **Render**:  
➡️ https://fuadbot-api.onrender.com

Frontend live here:  
🎨 https://fuadbot-ui.vercel.app

---

## 🧰 Tech Stack

- Python 3.10+
- FastAPI
- Uvicorn
- Requests
- python-dotenv
- Groq API (LLaMA 3)
- CORS

---

## 📦 Installation

```bash
git clone https://github.com/Fuad-Khan/fuadbot-api.git
cd fuadbot-api
````

### 1️⃣ Create a virtual environment

**Windows:**

```bash
python -m venv venv
```

**macOS / Linux:**

```bash
python3 -m venv venv
```

### 2️⃣ Activate the virtual environment

**Windows:**

```bash
venv\Scripts\activate
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

### 3️⃣ Install dependencies

```bash
pip install fastapi uvicorn[standard] python-dotenv requests
```

Or if `requirements.txt` exists:

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

You must set this key for the API to function.

---

## 🧪 Running the API Locally

From the project folder (with venv activated):

```bash
uvicorn main:app --reload --port 5000
```

Your API will be available at:

* Swagger UI → [http://localhost:5000/docs](http://localhost:5000/docs)
* ReDoc → [http://localhost:5000/redoc](http://localhost:5000/redoc)

---

## 📡 API Endpoints

### `POST /chat`

Handles chatbot interaction.

**Request:**

```json
{
  "message": "Hello FuadBot!"
}
```

**Response:**

```json
{
  "reply": "Hi! How can I help you today?"
}
```

Behavior:

* Validates the input message.
* Detects special case: "tell about me".
* Applies system prompt from `prompt/systemPrompt.txt`.
* Injects today's date.
* Calls Groq's LLaMA 3 model.
* Applies 10s timeout.
* Handles errors & rate limits.

---

### `POST /reset`

Simple manual reset hook:

```text
Reset done
```

---

## 🧱 Project Structure

```
fuadbot-api/
├── prompt/
│   └── systemPrompt.txt
├── main.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

## 📤 Deployment Notes

* Add `GROQ_API_KEY` inside your hosting platform's environment settings.
* Example production command:

```bash
uvicorn main:app --host 0.0.0.0 --port 10000
```

* Make sure `venv/`, `.env`, and `__pycache__/` are included in `.gitignore`.

---

## 🎉 Final Notes

FuadBot API is lightweight, fast, and ready for production or experimentation. Customize the system prompt, enhance routing, or integrate session memory — the backend is flexible and extendable.

Happy building! ⚡🧠


