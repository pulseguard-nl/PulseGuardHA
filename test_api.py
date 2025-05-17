#!/usr/bin/env python3
"""Test script for PulseGuard API connection."""

import json
import platform
import socket
import uuid
import sys
import requests
import psutil

def get_local_ip():
    """Get the local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception:
        return "127.0.0.1"

def get_mac_address():
    """Get the MAC address."""
    try:
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                        for elements in range(0, 8 * 6, 8)][::-1])
        return mac
    except Exception:
        return "00:00:00:00:00:00"

def test_api_connection(api_token, device_uuid, api_url="https://app.pulseguard.nl/api"):
    """Test API connection with the provided credentials."""
    print(f"Testing connection to {api_url} with device {device_uuid}")
    
    # Get system info for validation request
    hostname = platform.node()
    ip_address = get_local_ip()
    mac_address = get_mac_address()
    
    # Get system metrics
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    disk = psutil.disk_usage('/')
    disk_usage = disk.percent
    
    # Create system specs payload
    system_specs = {
        "cpu_cores": psutil.cpu_count(logical=True),
        "total_memory": memory.total // (1024 * 1024)  # Convert to MB
    }
    
    # Create metrics payload
    metrics = {
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "disk_usage": disk_usage,
        "uptime": 60  # Just a placeholder for validation
    }
    
    # Create validation data with all required fields
    validation_data = {
        "hostname": f"Home Assistant Test - {hostname}",
        "ip_address": str(ip_address),
        "mac_address": str(mac_address),
        "os_type": "homeassistant",
        "os_version": str(platform.version()),
        "system_specs": system_specs,
        "metrics": metrics,
        "services": []
    }
    
    # Print the request data
    print("\nSending data:")
    print(json.dumps(validation_data, indent=2))
    
    # Set up headers
    headers = {
        "Content-Type": "application/json",
        "X-API-Token": api_token,
        "Accept": "application/json",
    }
    
    print(f"\nAPI URL: {api_url}/devices/check-in")
    print(f"Headers: X-API-Token: {api_token[:8]}...{api_token[-8:] if len(api_token) > 16 else ''}")
    
    try:
        # Test API connectivity
        response = requests.post(
            f"{api_url}/devices/check-in",
            headers=headers,
            json=validation_data,
            timeout=30,
        )
        
        # Print response details
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        # Check if successful
        if response.status_code == 200:
            print("\n✅ SUCCESS: API connection test successful!")
            return True
        else:
            print(f"\n❌ ERROR: API returned status code {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as err:
        print(f"\n❌ ERROR: Connection error: {err}")
        if hasattr(err, "response") and err.response is not None:
            print(f"Response status code: {err.response.status_code}")
            print(f"Response content: {err.response.text}")
        return False
    except Exception as err:
        print(f"\n❌ ERROR: Unexpected error: {err}")
        return False

def main():
    """Run the test with command-line arguments."""
    if len(sys.argv) < 3:
        print("Usage: python test_api.py <device_uuid> <api_token> [api_url]")
        print("Example: python test_api.py 914759c0-bcec-43be-a2b6-3d6f7bf67749 apitoken123456")
        sys.exit(1)
    
    device_uuid = sys.argv[1]
    api_token = sys.argv[2]
    api_url = sys.argv[3] if len(sys.argv) > 3 else "https://app.pulseguard.nl/api"
    
    test_api_connection(api_token, device_uuid, api_url)

if __name__ == "__main__":
    main() 