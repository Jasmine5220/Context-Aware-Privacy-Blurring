# Setup Guide for Context-Aware Privacy Blurring

This guide will help you set up and run the Context-Aware Privacy Blurring system on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.10 or higher
- PostgreSQL database server
- Git
- Webcam (built-in or external)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/context-aware-privacy-blurring.git
cd context-aware-privacy-blurring
```

### 2. Set Up the Environment

#### Option 1: Using the setup script (Linux/Mac)
```bash
chmod +x setup.sh
./setup.sh
```

#### Option 2: Manual setup

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

2. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r dependencies.txt
   ```

### 3. Configure Database

1. Create a PostgreSQL database for the application.

2. Copy the example environment file and edit it with your database credentials:
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file with your database connection details:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/privacy_blurring
   PGUSER=your_username
   PGPASSWORD=your_password
   PGDATABASE=privacy_blurring
   PGHOST=localhost
   PGPORT=5432
   ```

### 4. Initialize the Database

Run the initialization script to create all tables and default data:
```bash
python init_db.py
```

### 5. Streamlit Configuration (Optional)

For optimal performance, you can create a Streamlit configuration file:

1. Create the directory:
   ```bash
   mkdir -p .streamlit
   ```

2. Create a config file:
   ```bash
   echo '[server]
   headless = true
   address = "0.0.0.0"
   port = 5000' > .streamlit/config.toml
   ```

## Running the Application

1. Make sure your virtual environment is activated.

2. Start the Streamlit server:
   ```bash
   streamlit run app.py
   ```

3. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

## Troubleshooting

### Camera Issues
- Ensure your webcam is properly connected
- Check that no other applications are using the webcam
- Ensure your browser has permission to access the camera

### Database Issues
- Verify your database credentials in the `.env` file
- Make sure the PostgreSQL server is running
- Check database logs for any errors
- Run `python init_db.py` to reinitialize the database if needed

### Package Issues
- If you encounter missing packages, try running:
  ```bash
  pip install -r dependencies.txt --upgrade
  ```

## Additional Information

- The application saves detection sessions and statistics to the database
- Default blur rules and keyword lists are created during database initialization
- Privacy settings can be customized through the UI and will be saved for future sessions

# 🪟 Setup Guide (Windows)  
**Context-Aware Privacy Blurring System**

This guide walks you through setting up and running the system on a **Windows machine**.

---

## ✅ Prerequisites

Ensure the following are installed:

- **Python 3.10+**
- **PostgreSQL**
- **Git for Windows**
- **A webcam**
- **Streamlit** (will be installed via `pip`)

---

## 🔄 Installation Steps

### 1. Clone the Repository

Open **Git Bash** or **Command Prompt** and run:

```bash
git clone https://github.com/yourusername/context-aware-privacy-blurring.git
cd context-aware-privacy-blurring
```

---

### 2. Set Up the Environment

#### 🅰️ Manual Setup (Recommended for Windows)

1. **Create a virtual environment:**
   ```cmd
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   ```cmd
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```cmd
   pip install -r dependencies.txt
   ```

> 📝 You can inspect the `setup.sh` manually but avoid running it directly on Windows—it’s intended for Unix-like systems.

---

### 3. Configure PostgreSQL

1. **Create a PostgreSQL database** using pgAdmin or `psql`.

2. **Copy and modify environment file:**
   ```cmd
   copy .env.example .env
   ```

3. Edit `.env` with your PostgreSQL details:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/privacy_blurring
   PGUSER=your_username
   PGPASSWORD=your_password
   PGDATABASE=privacy_blurring
   PGHOST=localhost
   PGPORT=5432
   ```

---

### 4. Initialize the Database

While your environment is activated, run:

```cmd
python init_db.py
```

---

### 5. (Optional) Streamlit Configuration

You can configure Streamlit with a settings file for consistent behavior:

1. **Create directory:**
   ```cmd
   mkdir .streamlit
   ```

2. **Create config file:**
   Open Notepad or VS Code and paste the following into `.streamlit/config.toml`:
   ```toml
   [server]
   headless = true
   address = "0.0.0.0"
   port = 5000
   ```

---

## ▶️ Running the Application

1. Activate your virtual environment:
   ```cmd
   venv\Scripts\activate
   ```

2. Run the app:
   ```cmd
   streamlit run app.py
   ```

3. Open your browser to:
   ```
   http://localhost:5000
   ```

---

## 🛠 Troubleshooting

### 🔍 Webcam
- Ensure your camera is connected and accessible
- Make sure no other apps are using it
- Allow permissions if prompted by browser

### 🧩 Packages
If any dependency errors appear:
```cmd
pip install -r dependencies.txt --upgrade
```

### 🐘 PostgreSQL
- Double-check your `.env` credentials
- Ensure PostgreSQL service is running
- Re-run `init_db.py` if needed
