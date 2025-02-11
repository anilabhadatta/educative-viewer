# Educative Viewer

A self-hosted web viewer for [Educative.io](https://www.educative.io/) courses downloaded using [Educative.io_Scraper](https://github.com/anilabhadatta/educative.io_scraper).

> **Note:** This viewer is designed for courses scraped in **Dark Mode**.

## Features

- 📚 Browse and read downloaded Educative.io courses
- 🔐 Multi-user authentication with signup tokens
- 📍 Automatic progress tracking (last visited course/topic)
- 💻 Monaco editor for viewing code files
- 📦 Download course folders as ZIP
- 🐳 Docker deployment with systemd auto-start
- 🌐 Remote access via Tailscale

## Quick Start (Docker)

### Prerequisites

- Docker & Docker Compose
- Tailscale (optional, for remote access)
- Courses downloaded using [Educative.io_Scraper](https://github.com/anilabhadatta/educative.io_scraper)

### 1. Clone & Configure

```bash
git clone https://github.com/anilabhadatta/educative-viewer.git
cd educative-viewer
```

Edit `docker-compose.yml` to set your course directory:

```yaml
volumes:
  - /path/to/your/courses:/course_data:ro,Z  # Change this path
  - ./data:/app/data:Z
environment:
  - authtoken=your-signup-token      # Token required during signup
  - downloadtoken=your-download-token # Token for download access
```

### 2. Install & Start Service

```bash
./start-educative-viewer.sh
```

This installs a systemd user service that:
- Starts on boot (with lingering enabled)
- Runs Docker Compose in background
- Exposes port 5001 via Tailscale automatically

### 3. Access

| Method | URL |
|--------|-----|
| Local | http://localhost:5001/edu-viewer/ |
| Tailscale | https://your-machine.ts.net/edu-viewer/ |

## Service Management

```bash
# Control service
systemctl --user start educative-viewer
systemctl --user stop educative-viewer
systemctl --user restart educative-viewer
systemctl --user status educative-viewer

# View logs
journalctl --user -u educative-viewer -f
docker-compose logs -f

# Tailscale
tailscale serve status
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `course_dir` | Path to courses inside container | `.` |
| `authtoken` | Token required for user signup | `""` |
| `downloadtoken` | Token for ZIP download access | `""` |
| `EDUCATIVE_VIEWER_ROOT` | Database storage path | `~/EducativeViewer` |

### Data Persistence

The SQLite database stores user accounts and progress. With Docker, it's persisted to `./data/db.sqlite`.

**Migrate existing database:**

```bash
mkdir -p ./data
cp ~/EducativeViewer/db.sqlite ./data/
```

## Course Directory Structure

Point `course_dir` to a folder containing scraped courses:

```
courses/
├── course-name-1/
│   ├── 01-introduction/
│   │   ├── index.html
│   │   └── ...
│   └── 02-getting-started/
└── course-name-2/
```

![Course folder example](https://i.imgur.com/sQQlJGI.jpg)

## Manual Installation (Without Docker)

<details>
<summary>Click to expand</summary>

### Prerequisites

- Python 3.12+
- Git

### Setup

```bash
git clone https://github.com/anilabhadatta/educative-viewer.git
cd educative-viewer

# Create virtual environment
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export course_dir=/path/to/courses
export FLASK_APP=educative-viewer
export authtoken=your-token
export downloadtoken=your-token

# Run
flask run --host=0.0.0.0 --port=5001
```

### Production (Gunicorn)

```bash
gunicorn --workers=2 -b 0.0.0.0:5001 'educative-viewer:create_app()' --timeout 120000
```

</details>

## Version

**4.0.9** — Delete existing `db.sqlite` if upgrading from older versions (schema changes).

## Deployment on Azure

This application is configured for a low-cost deployment on Azure Container Apps with scale-to-zero capabilities and persistent storage using Azure File Share.

Infrastructure code is located in [infra/tofu/](infra/tofu/).

### Prerequisites
- [OpenTofu](https://opentofu.org/) installed.
- Azure CLI installed and logged in (`az login`).
- Docker image pushed to a registry (e.g., GHCR).

### Steps
1. Navigate to the infra directory: [infra/tofu/](infra/tofu/).
2. Create a `terraform.tfvars` file (use `terraform.tfvars.example` as a template).
3. Initialize: `tofu init`
4. Deploy: `tofu apply`
5. After deployment, upload your `courses` and `db.sqlite` to the created Azure File Share.

### How it works
- **Scaling:** The app scales to zero when not in use, incurring no costs for the container replicas.
- **Persistence:** All data (SQLite DB and courses) is stored in Azure Files, which is mounted to `/mnt/azure` inside the container.
- **Environment Variables:** `COURSE_DIR` and `EDUCATIVE_VIEWER_ROOT` are set to point to the mounted storage.

## License

See [LICENSE](LICENSE) file.
