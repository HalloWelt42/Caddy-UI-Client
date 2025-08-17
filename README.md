# Caddy Manager

A desktop application for managing Caddy Server with automatic HTTPS/TLS support, Docker integration, and real-time monitoring.

## Features

- **Caddy Server Management**: Install, configure, start/stop Caddy directly from the GUI
- **Automatic HTTPS**: Let's Encrypt for public domains, internal certificates for local development
- **Route Management**: Add, remove, and manage reverse proxy routes through a visual interface
- **Docker Integration**: Monitor and control Docker containers
- **Real-time Monitoring**: System metrics (CPU, RAM) and service status with WebSocket streaming
- **Cross-platform Architecture**: FastAPI backend with PySide6 (Qt6) frontend

## Requirements

- Python 3.11 or higher
- macOS with Apple Silicon (M1/M2/M3) - currently supported
- Docker Desktop (optional, for container management)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/caddy-manager.git
cd caddy-manager

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Quick Start

```bash
# Make the start script executable
chmod +x start.sh

# Start both backend and frontend
./start.sh

# Or start components separately:
python run_server.py  # Terminal 1: Backend (FastAPI)
python run_client.py  # Terminal 2: Frontend (PySide6)
```

### Available Commands

```bash
./start.sh start    # Start backend and frontend
./start.sh stop     # Stop all services
./start.sh restart  # Restart all services
./start.sh status   # Show service status
./start.sh install  # Install dependencies only
./start.sh dev      # Development mode with terminal logging
```

## Project Structure

```
caddy-manager/
├── server/          # FastAPI backend
│   ├── api/         # API routes and services
│   └── config/      # Server configuration
├── client/          # PySide6 frontend
│   ├── ui/          # GUI components
│   └── services/    # API client
├── config/          # Configuration files
│   └── caddy/       # Caddyfile storage
├── data/            # Runtime data
│   ├── caddy/       # Caddy binary
│   ├── backups/     # Configuration backups
│   └── logs/        # Application logs
└── shared/          # Shared utilities
```

## API Documentation

The backend runs on `http://localhost:8000` with full OpenAPI documentation available at `/docs`.

### Core Endpoints

#### Server Information
- `GET /` - Server info and available endpoints
- `GET /health` - Health check with service status

#### Caddy Management
- `GET /api/caddy/status` - Get Caddy status (running/stopped/not_installed)
- `POST /api/caddy/install` - Install Caddy binary
- `POST /api/caddy/start` - Start Caddy server
- `POST /api/caddy/stop` - Stop Caddy server
- `POST /api/caddy/restart` - Restart Caddy server

#### Route Management
- `GET /api/caddy/routes` - List all configured routes
- `POST /api/caddy/routes` - Add new route
  ```json
  {
    "domain": "example.local",
    "upstream": "http://localhost:3000",
    "path": "/"
  }
  ```
- `DELETE /api/caddy/routes/{domain}` - Remove route by domain

#### Backup & Restore
- `POST /api/caddy/backup` - Create configuration backup
  ```json
  {
    "name": "my_backup"  // optional
  }
  ```
- `POST /api/caddy/restore` - Restore from backup
  ```json
  {
    "backup_name": "caddy_config_20250101_120000.json"
  }
  ```
- `GET /api/caddy/backups` - List all available backups

#### System Monitoring
- `GET /api/monitoring/metrics` - Current system metrics (CPU, RAM, requests/sec)
- `GET /api/monitoring/metrics/history` - Historical metrics data

#### Docker Management
- `GET /api/monitoring/docker/containers` - List all Docker containers
- `POST /api/monitoring/docker/containers/{container_id}/{action}` - Container control
  - Actions: `start`, `stop`, `restart`

### WebSocket Endpoints (Real-time Updates)

- `WS /api/caddy/install/progress` - Real-time installation progress
  ```json
  // Receive updates:
  {
    "message": "Downloading Caddy...",
    "progress": 45
  }
  ```

- `WS /api/monitoring/metrics/stream` - Live metrics stream
  ```json
  // Receive metrics every 5 seconds:
  {
    "cpu_percent": 12.5,
    "ram_percent": 45.2,
    "requests_per_second": 10,
    "avg_response_time": 25.3
  }
  ```

### API Testing

A comprehensive test suite is included:

```bash
# Run all API tests
python test_api_endpoints.py

# Test with custom server URL
python test_api_endpoints.py --url http://localhost:8000

# Interactive testing mode
python test_api_endpoints.py --interactive
```

## Configuration

### Environment Variables

The application uses a `.env` file (auto-created on first run):

```env
PROJECT_ROOT=/path/to/caddy-manager
DATA_DIR=/path/to/caddy-manager/data
CONFIG_DIR=/path/to/caddy-manager/config
LOGS_DIR=/path/to/caddy-manager/data/logs
CADDY_BINARY=/path/to/caddy-manager/data/caddy/caddy
CADDYFILE=/path/to/caddy-manager/config/caddy/Caddyfile
```

### Caddyfile

The Caddy configuration is managed automatically but can be manually edited at `config/caddy/Caddyfile`:

```caddyfile
# Admin API
{
    admin localhost:2019
    email admin@localhost
    local_certs
}

# Example route
example.local {
    tls internal
    reverse_proxy localhost:3000
}
```

## Development

### Running in Development Mode

```bash
# Backend with auto-reload
uvicorn server.main:app --reload --host 0.0.0.0 --port 8000

# Frontend with debug output
python run_client.py --debug
```

### Project Dependencies

Core dependencies include:
- **Backend**: FastAPI, uvicorn, httpx, psutil, docker, pydantic
- **Frontend**: PySide6, qasync, QtAwesome
- **Utilities**: orjson, watchdog, python-dotenv

See `requirements.txt` for complete list with versions.

## Known Limitations

- Currently supports only macOS with Apple Silicon (Phase 1)
- No authentication (designed for local development)
- Basic Caddyfile parsing (complex configurations may need manual editing)
- WebSocket progress tracking may be unstable in some environments

## Planned Features (Phase 2)

- **Platform Support**: Windows and Linux compatibility
- **Enhanced Features**: 
  - Log viewer with filtering
  - Configuration templates
  - Multi-server management
  - Plugin system
- **UI Improvements**:
  - Dark/Light mode toggle
  - Custom themes
  - Keyboard shortcuts
  - Status history graphs

## Troubleshooting

### Common Issues

1. **"Caddy not installed" error**
   - Use the Install button in the Dashboard
   - Or manually: `POST /api/caddy/install`

2. **"Connection refused" on API calls**
   - Ensure backend is running: `python run_server.py`
   - Check port 8000 is not in use

3. **Docker containers not showing**
   - Ensure Docker Desktop is running
   - Check Docker socket permissions

4. **SSL certificate errors**
   - Run `caddy trust` to install root certificate
   - For local domains, use `.local` suffix

### Debug Mode

Enable detailed logging:
```bash
# Start with debug script
./debug_start.sh

# Or set environment variable
export DEBUG=true
python run_server.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Acknowledgments

- [Caddy Server](https://caddyserver.com/) - The ultimate server with automatic HTTPS
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web API framework
- [PySide6](https://doc.qt.io/qtforpython/) - Python bindings for Qt6
- [Docker](https://www.docker.com/) - Container platform

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the [API documentation](http://localhost:8000/docs)
- Review the test suite for usage examples