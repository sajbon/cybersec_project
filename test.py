import subprocess
import re
import requests

link = input("domain name: ")
max_dead_hops = 3
dead_hop_streak = 0

# Run the traceroute command
result = subprocess.run(['traceroute', link], capture_output=True, text=True)
lines = result.stdout.splitlines()[1:]  # Skip header

ip_addresses = []

for line in lines:
    # Look for an IP address in the line
    match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
    if match:
        ip = match.group(1)
        ip_addresses.append(ip)
        dead_hop_streak = 0  # reset streak

        try:
            response = requests.get(f'https://ipinfo.io/{ip}/json')
            data = response.json()
            city = data.get('city', 'Unknown')
            print(f'{len(ip_addresses)}. {ip} → City: {city}')
        except Exception as e:
            print(f'{len(ip_addresses)}. {ip} → Error: {e}')

    else:
        dead_hop_streak += 1
        print(f'{len(ip_addresses)+1}. * * * (Unreachable hop {dead_hop_streak})')

    # Stop if we've hit 3 dead hops in a row
    if dead_hop_streak >= max_dead_hops:
        print(f'\nStopping traceroute: {max_dead_hops} unreachable hops in a row.')
        break