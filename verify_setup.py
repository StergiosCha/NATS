import os
import sys
import time

print("--- DIAGNOSTIC START ---")

# 1. Check Directory
cwd = os.getcwd()
print(f"Current Directory: {cwd}")
network_dir = os.path.join(cwd, 'static', 'networks')

if not os.path.exists(network_dir):
    print(f"FAIL: Directory {network_dir} does not exist.")
    html_files = []
else:
    files = os.listdir(network_dir)
    html_files = [f for f in files if f.endswith('.html')]
    print(f"PASS: Found {len(html_files)} HTML files in static/networks")
    if html_files:
        print(f"      Sample: {html_files[0]}")
    else:
        print("WARN: No HTML files found in static/networks. Run an analysis first.")

# 2. Check wsgi.py content
if os.path.exists('wsgi.py'):
    with open('wsgi.py', 'r') as f:
        content = f.read()
        if 'serve_networks' in content:
            print("PASS: wsgi.py contains 'serve_networks' route.")
        else:
            print("FAIL: wsgi.py DOES NOT contain 'serve_networks' route. You didn't copy the updated file!")
        
        if 'PORT = 8052' in content:
            print("PASS: wsgi.py has PORT = 8052")
        else:
            print("FAIL: wsgi.py does not have PORT = 8052")
else:
    print("FAIL: wsgi.py not found in current directory.")

# 3. Check Server Connectivity
# We use urllib to avoid dependency on requests if not installed
import urllib.request
import urllib.error

if html_files:
    test_file = html_files[0]
    url = f"http://localhost:8052/static/networks/{test_file}"
    print(f"Testing URL: {url}")
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            if response.getcode() == 200:
                print("PASS: Successfully fetched visualization from server!")
            else:
                print(f"FAIL: Server returned status code {response.getcode()}")
    except urllib.error.URLError as e:
        print(f"FAIL: Could not connect to server: {e}. Is 'python wsgi.py' running?")
    except Exception as e:
        print(f"FAIL: Error checking server: {e}")
else:
    print("SKIP: Cannot test server connectivity without HTML files.")

print("--- DIAGNOSTIC END ---")
