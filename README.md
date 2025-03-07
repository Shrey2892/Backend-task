# 📌 Django Project with Google OAuth, Google Drive, and WebSockets

## 🚀 Overview
This project is a Django-based web application featuring:
- ✅ **Google OAuth 2.0 Authentication** (Sign in with Google)
- ✅ **Google Drive Integration** (Upload/download files)
- ✅ **Real-time Chat using WebSockets**
- ✅ **Django REST Framework for API Development**
- ✅ **PostgreSQL as Database (Hosted on Neon)**
- ✅ **Session Management**
- ✅ **Deployment on Heroku**

## 🛠 Tech Stack
- **Backend:** Django, Django REST Framework
- **Database:** PostgreSQL (Neon)
- **Authentication:** Google OAuth 2.0
- **Real-time Communication:** Django Channels, WebSockets
- **Deployment:** Heroku

## 📦 Installation
Follow these steps to set up the project locally:

### 1️⃣ Clone the repository
```bash
git clone https://github.com/Shrey2892/Backend-task.git
cd Project
```

### 2️⃣ Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Apply migrations
```bash
python manage.py migrate
```

### 5️⃣ Run the development server
```bash
python manage.py runserver
```

## 🔑 Environment Variables
Create a `.env` file in the root directory and add the following:
```bash
DATABASE_URL= "postgresql://taskdb_owner:npg_lOtZ0HBcq3KA@ep-wild-butterfly-a1vflq1y-pooler.ap-southeast-1.aws.neon.tech:5432/taskdb"
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
ALLOWED_HOSTS=yourdomain.com,localhost,127.0.0.1
```

## 📬 API Endpoints
### Authentication
- `POST /auth/login/` - Login using Google OAuth
- `GET /auth/user/` - Get logged-in user details

### Google Drive
- `POST /drive/upload/` - Upload a file to Google Drive
- `GET /drive/files/` - Fetch list of uploaded files
- `GET /drive/download/<file_id>/` - Download a file from Google Drive

### Real-time Chat
- WebSocket: `ws://localhost:8000/ws/chat/<room_name>/`

## 🎯 Deployment on Heroku
### 1️⃣ Install Heroku CLI and login
```bash
heroku login
```
### 2️⃣ Create a Heroku app and push code
```bash
heroku create your-app-name
git push heroku main
```
### 3️⃣ Set environment variables
```bash
heroku config:set SECRET_KEY=your_secret_key
heroku config:set DATABASE_URL=your_postgresql_url
heroku config:set GOOGLE_CLIENT_ID=your_google_client_id
heroku config:set GOOGLE_CLIENT_SECRET=your_google_client_secret
```
### 4️⃣ Run migrations on Heroku
```bash
heroku run python manage.py migrate
```

## 🛠 Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature-name`)
3. Commit changes (`git commit -m "Added feature"`)
4. Push to GitHub (`git push origin feature-name`)
5. Create a pull request

## 📄 License
This project is licensed under the MIT License.

## 📬 Contact
For any inquiries, reach out to:
- **GitHub:** [yourusername](https://github.com/yourusername)
- **Email:** your.email@example.com

