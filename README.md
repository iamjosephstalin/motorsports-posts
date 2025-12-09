# 🏎️ Racing Tamizhan Auto System

An autonomous content engine for F1 & MotoGP updates. This system fetches news, designs branded social media posts, generates AI-narrated video reels, and handles publishing to Instagram and YouTube.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

## ✨ Features
- **🌎 Autonomous Scout**: Fetches news from major motorsport RSS feeds.
- **🎨 Creative Studio**:
  - Auto-extracts team colors (Red Bull, Ferrari, etc.).
  - Generates highly visual "Cover Slides" for Instagram.
  - **AI Video**: Creates vertical reels with "Ken Burns" effects and Neural Voiceovers.
  - **Smart Reader**: Fetches full article text for accurate summaries.
- **🚀 Logic Publisher**:
  - Uploads to Instagram (Feed/Reels) and YouTube (Shorts).
  - Deletes local files automatically after successful upload.
- **🛡️ Secure Dashboard**: Password-protected Streamlit interface.

## 🛠️ Installation (Local)

1. **Clone the repository**
   ```bash
   git clone https://github.com/iamjosephstalin/insta-post-maker.git
   cd insta-post-maker
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   *Note: You may need `ffmpeg` installed for video generation.*

3. **Configure Environment**
   Create a `.env` file (copied from `.env.example` if available, or scratch):
   ```properties
   # Credentials
   ADMIN_PASSWORD=your_strong_password
   
   # Instagram
   IG_USERNAME=your_username
   IG_PASSWORD=your_password
   
   # YouTube (Optional)
   YOUTUBE_CLIENT_SECRET_FILE=client_secret.json
   ```

4. **Run the Dashboard**
   ```bash
   streamlit run dashboard.py
   ```

## ☁️ Deployment

### Option 1: Streamlit Community Cloud (Free & Easy)
*Best for testing, but Instagram login might be flagged due to shared IP.*

1. Fork this repo to your GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io/).
3. Connect your GitHub and select this repo.
4. In "Advanced Settings", add your secrets (`ADMIN_PASSWORD`, `IG_USERNAME`, etc.) as **Secrets** (not `.env` file).
   ```toml
   # .streamlit/secrets.toml format in cloud dashboard
   ADMIN_PASSWORD = "..."
   IG_USERNAME = "..."
   ```

### Option 2: Docker / VPS (Recommended for Production)
*Recommended to keep a stable IP address for Instagram safety.*

1. **Dockerfile** is included (create one if missing):
   ```dockerfile
   FROM python:3.10-slim
   WORKDIR /app
   RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6
   COPY . .
   RUN pip install --no-cache-dir -r requirements.txt
   EXPOSE 8501
   CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Build & Run**:
   ```bash
   docker build -t racing-bot .
   docker run -p 8501:8501 --env-file .env racing-bot
   ```

## ⚠️ Disclaimer
This tool uses `instagrapi` which automates Instagram. Use responsibly. Excessive automation can lead to account flags.
