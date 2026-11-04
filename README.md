# Page-load counter backend

This Flask service records the number of page loads sent by the frontend in a
MySQL counter table. Each request to `POST /api/loads` accepts JSON such as
`{"loads": 1}` and returns the updated total as `{"total_loads": 1}`.

## Setup on Windows

Run these commands from this directory in PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create the database and counter table using a MySQL account with permission to
create databases:

```powershell
mysql -u root -p < schema.sql
```

Set the connection settings in PowerShell (replace the example password):

```powershell
$env:MYSQL_HOST = "127.0.0.1"
$env:MYSQL_PORT = "3306"
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = "your-mysql-password"
$env:MYSQL_DATABASE = "load_counter"
```

Start the backend:

```powershell
python app.py
```

The API listens at `http://127.0.0.1:5000`. The default CORS origins allow the
frontend served from `localhost:5500` or `127.0.0.1:5500`; set
`FRONTEND_ORIGINS` to a comma-separated list if it uses a different origin.

To run the backend tests:

```powershell
python -m unittest
```
