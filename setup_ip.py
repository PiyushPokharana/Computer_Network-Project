# Helper script to update SERVER_IP in client.py
# Run this before starting clients

import sys
import re

def get_local_ip():
    """Try to get local IP address"""
    import socket
    try:
        # Create a socket and connect to external address (doesn't actually send data)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return None

def update_server_ip(new_ip):
    """Update SERVER_IP in client.py"""
    try:
        with open('client.py', 'r') as f:
            content = f.read()
        
        # Find and replace SERVER_IP line
        pattern = r'SERVER_IP = "[^"]*"'
        replacement = f'SERVER_IP = "{new_ip}"'
        
        new_content = re.sub(pattern, replacement, content)
        
        with open('client.py', 'w') as f:
            f.write(new_content)
        
        print(f"✓ Updated SERVER_IP to '{new_ip}' in client.py")
        return True
    except Exception as e:
        print(f"✗ Error updating client.py: {e}")
        return False

def main():
    print("="*60)
    print("Federated Learning - Server IP Configuration Helper")
    print("="*60)
    
    # Try to detect local IP
    local_ip = get_local_ip()
    if local_ip:
        print(f"\nDetected local IP: {local_ip}")
    
    print("\nOptions:")
    print("1. Use localhost (127.0.0.1) - for testing on same machine")
    print("2. Use detected local IP - for testing on local network")
    print("3. Enter custom IP address")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        ip = "127.0.0.1"
    elif choice == "2":
        if local_ip:
            ip = local_ip
        else:
            print("Could not detect local IP. Please enter manually.")
            ip = input("Enter server IP: ").strip()
    elif choice == "3":
        ip = input("Enter server IP: ").strip()
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)
    
    # Validate IP format (basic check)
    parts = ip.split('.')
    if len(parts) != 4 or not all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
        print(f"✗ Invalid IP address format: {ip}")
        sys.exit(1)
    
    # Update client.py
    if update_server_ip(ip):
        print("\n" + "="*60)
        print("Configuration complete!")
        print("="*60)
        print("\nNext steps:")
        print("1. Start server: python server.py")
        print("2. Run clients: python client.py")
        print(f"\nClients will connect to {ip}:5000")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
