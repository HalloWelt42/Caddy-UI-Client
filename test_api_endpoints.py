#!/usr/bin/env python3
"""
Caddy Manager API Test Script
Testet alle dokumentierten API Endpoints
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional
from datetime import datetime
from server.config.settings import settings

from typing_inspection.typing_objects import alias

# Konfiguration
BASE_URL = settings.api_server
TIMEOUT = 10


# Farben für Terminal-Output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Druckt einen formatierten Header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'=' * 60}")
    print(f"{text}")
    print(f"{'=' * 60}{Colors.RESET}")


def print_test(endpoint: str, method: str = "GET"):
    """Druckt Test-Info"""
    print(f"\n{Colors.YELLOW}Testing: {method} {endpoint}{Colors.RESET}")


def print_success(message: str):
    """Druckt Erfolgs-Nachricht"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_error(message: str):
    """Druckt Fehler-Nachricht"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")


def print_info(message: str):
    """Druckt Info-Nachricht"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")


def print_response(response: requests.Response, show_body: bool = True):
    """Druckt Response-Details"""
    print(f"  Status Code: {response.status_code}")
    print(f"  Response Time: {response.elapsed.total_seconds():.2f}s")

    if show_body and response.text:
        try:
            body = response.json()
            print(f"  Response Body: {json.dumps(body, indent=2)[:500]}")  # Erste 500 Zeichen
        except:
            print(f"  Response Text: {response.text[:200]}")


def test_endpoint(method: str, endpoint: str, data: Optional[Dict] = None,
                  expected_status: Optional[int] = None, test_name: Optional[str] = None) -> bool:
    """
    Testet einen einzelnen Endpoint

    Returns:
        bool: True wenn Test erfolgreich
    """
    url = f"{BASE_URL}{endpoint}"
    test_desc = test_name or f"{method} {endpoint}"

    print_test(endpoint, method)

    try:
        # Request senden
        if method == "GET":
            response = requests.get(url, timeout=TIMEOUT)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=TIMEOUT)
        elif method == "DELETE":
            response = requests.delete(url, timeout=TIMEOUT)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=TIMEOUT)
        else:
            print_error(f"Unsupported method: {method}")
            return False

        # Response prüfen
        print_response(response)

        # Status Code prüfen
        if expected_status:
            if response.status_code == expected_status:
                print_success(f"Expected status code {expected_status}")
                return True
            else:
                print_error(f"Expected {expected_status}, got {response.status_code}")
                return False
        else:
            # Standard-Erwartungen
            if method == "GET" and response.status_code == 200:
                print_success("GET request successful")
                return True
            elif method == "POST" and response.status_code in [200, 201]:
                print_success("POST request successful")
                return True
            elif method == "DELETE" and response.status_code in [200, 204]:
                print_success("DELETE request successful")
                return True
            else:
                print_error(f"Unexpected status code: {response.status_code}")
                return False

    except requests.exceptions.ConnectionError:
        print_error(f"Connection failed! Is the server running on {BASE_URL}?")
        return False
    except requests.exceptions.Timeout:
        print_error(f"Request timeout after {TIMEOUT} seconds")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def main():
    """Hauptfunktion - führt alle Tests aus"""

    print_header("CADDY MANAGER API TEST SUITE")
    print(f"Target: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Test-Ergebnisse sammeln
    results = {
        "passed": 0,
        "failed": 0,
        "skipped": 0
    }

    # Server-Verfügbarkeit prüfen
    print_header("1. SERVER CONNECTIVITY")

    if not test_endpoint("GET", "/health"):
        print_error("\nServer is not reachable! Please start the server with:")
        print_info("python run_server.py")
        sys.exit(1)
    results["passed"] += 1

    # API Status
    print_header("2. CADDY STATUS ENDPOINTS")

    if test_endpoint("GET", "/api/caddy/status"):
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Caddy Installation (optional - kann System verändern)
    print_header("3. CADDY INSTALLATION")
    print_info("Skipping installation test (would modify system)")
    print_info("To test manually: POST /api/caddy/install")
    results["skipped"] += 1

    # Caddy Control Endpoints
    print_header("4. CADDY CONTROL ENDPOINTS")

    # Diese können fehlschlagen wenn Caddy nicht installiert ist
    endpoints_control = [
        ("POST", "/api/caddy/start"),
        ("POST", "/api/caddy/stop"),
        ("POST", "/api/caddy/restart"),
    ]

    for method, endpoint in endpoints_control:
        if test_endpoint(method, endpoint):
            results["passed"] += 1
        else:
            results["failed"] += 1
            print_info("Note: This might fail if Caddy is not installed")

    # Route Management
    print_header("5. ROUTE MANAGEMENT")

    # Routes auflisten
    if test_endpoint("GET", "/api/caddy/routes"):
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Neue Route hinzufügen
    test_route = {
        "domain": "test.local",
        "upstream": "http://localhost:3000",
        "path": "/"
    }

    print_info("Adding test route: test.local -> localhost:3000")
    if test_endpoint("POST", "/api/caddy/routes", data=test_route):
        results["passed"] += 1

        # Route wieder entfernen
        time.sleep(1)
        if test_endpoint("DELETE", "/api/caddy/routes/test.local"):
            results["passed"] += 1
            print_success("Test route cleaned up")
        else:
            results["failed"] += 1
            print_error("Could not delete test route")
    else:
        results["failed"] += 1
        print_info("Note: Route operations might fail if Caddy is not running")

    # Docker Endpoints
    print_header("6. DOCKER INTEGRATION")

    # Container auflisten
    if test_endpoint("GET", "/api/monitoring/docker/containers"):
        results["passed"] += 1
    else:
        results["failed"] += 1
        print_info("Note: Docker might not be installed or running")

    # Container Control (braucht eine gültige Container ID)
    print_info("Skipping container control tests (need valid container ID)")
    print_info("To test manually:")
    print_info("  POST /api/monitoring/docker/containers/{container_id}/start")
    print_info("  POST /api/monitoring/docker/containers/{container_id}/stop")
    print_info("  POST /api/monitoring/docker/containers/{container_id}/restart")
    results["skipped"] += 3

    # System Monitoring
    print_header("7. SYSTEM MONITORING")

    # Monitoring Endpoints
    monitoring_endpoints = [
        "/api/monitoring/metrics",
        "/api/monitoring/metrics/history"
    ]

    for endpoint in monitoring_endpoints:
        if test_endpoint("GET", endpoint):
            results["passed"] += 1
        else:
            results["failed"] += 1

    # Root Endpoint
    print_header("8. SERVER INFO")

    if test_endpoint("GET", "/"):
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Backup/Restore
    print_header("9. BACKUP & RESTORE")

    # Backup erstellen
    backup_data = {"name": "test_backup"}
    if test_endpoint("POST", "/api/caddy/backup", data=backup_data):
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Backups auflisten
    if test_endpoint("GET", "/api/caddy/backups"):
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Restore (würde System verändern)
    print_info("Skipping restore test (would modify system)")
    print_info("To test manually: POST /api/caddy/restore with {\"backup_name\": \"...\"}")
    results["skipped"] += 1

    # API Documentation
    print_header("10. API DOCUMENTATION")

    if test_endpoint("GET", "/docs", expected_status=200):
        results["passed"] += 1
        print_success("API documentation available at: {BASE_URL}/docs")
    else:
        results["failed"] += 1

    if test_endpoint("GET", "/openapi.json", expected_status=200):
        results["passed"] += 1
        print_success("OpenAPI specification available")
    else:
        results["failed"] += 1

    # Test-Zusammenfassung
    print_header("TEST SUMMARY")

    total = results["passed"] + results["failed"] + results["skipped"]

    print(f"\n  Total Tests: {total}")
    print(f"  {Colors.GREEN}Passed: {results['passed']}{Colors.RESET}")
    print(f"  {Colors.RED}Failed: {results['failed']}{Colors.RESET}")
    print(f"  {Colors.YELLOW}Skipped: {results['skipped']}{Colors.RESET}")

    success_rate = (results["passed"] / (results["passed"] + results["failed"]) * 100) if (results["passed"] + results[
        "failed"]) > 0 else 0

    print(f"\n  Success Rate: {success_rate:.1f}%")

    if results["failed"] == 0:
        print_success("\n✨ All tests passed successfully!")
        return 0
    else:
        print_error(f"\n⚠️  {results['failed']} tests failed. Check the output above for details.")
        return 1


def test_single_endpoint():
    """Interaktiver Modus zum Testen einzelner Endpoints"""

    print_header("INTERACTIVE API TEST MODE")

    while True:
        print("\nEnter request (e.g., 'GET /api/status' or 'POST /api/routes') or 'quit':")

        try:
            user_input = input("> ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                break

            parts = user_input.split(' ', 1)
            if len(parts) != 2:
                print_error("Format: METHOD /path/to/endpoint")
                continue

            method, endpoint = parts
            method = method.upper()

            # Bei POST nach Daten fragen
            data = None
            if method in ["POST", "PUT"]:
                print("Enter JSON data (or press Enter for empty):")
                data_input = input("> ").strip()
                if data_input:
                    try:
                        data = json.loads(data_input)
                    except json.JSONDecodeError:
                        print_error("Invalid JSON format")
                        continue

            test_endpoint(method, endpoint, data)

        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print_error(f"Error: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test Caddy Manager API Endpoints")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the API", alias="API_SERVER")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")

    args = parser.parse_args()

    BASE_URL = args.url.rstrip('/')
    TIMEOUT = args.timeout

    if args.interactive:
        test_single_endpoint()
    else:
        exit_code = main()
        sys.exit(exit_code)