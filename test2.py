import subprocess
import re
import requests
import geopandas as gpd
import matplotlib.pyplot as plt
import random

# Run the traceroute command
link = 'deepseek.com'

result = subprocess.run(['traceroute', link], capture_output=True, text=True)
lines = result.stdout.splitlines()[1:]  # Skip header

ip_addresses = []
ip_colors = {}  # Dictionary to store IP and its color

# Load world map using GeoPandas (after downloading and extracting the shapefile)
world = gpd.read_file("./ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp")  # Replace with your file path

# Initialize plot
fig, ax = plt.subplots(figsize=(15, 10))

# Plot the base world map
world.plot(ax=ax, color='lightgray', edgecolor='black')

# Function to generate random colors
def random_color():
    return f"#{random.randint(0, 0xFFFFFF):06x}"

# Loop through each line from the traceroute output
for line in lines:
    match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)  # Find IP addresses
    if match:
        ip = match.group(1)
        ip_addresses.append(ip)

        try:
            # Query ipinfo.io for geolocation
            response = requests.get(f'https://ipinfo.io/{ip}/json')
            data = response.json()
            city = data.get('city', 'Unknown')
            loc = data.get('loc', '0,0').split(',')
            lat, lon = float(loc[0]), float(loc[1])

            # Generate random color for each IP
            color = random_color()
            ip_colors[ip] = color

            # Plot the IP location on the map with the generated color
            ax.scatter(lon, lat, color=color)

            print(f'{ip} → City: {city} at {lat}, {lon}')
        except Exception as e:
            print(f'{ip} → Error: {e}')

# Create custom legend labels with corresponding IPs and colors
handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10) for color in ip_colors.values()]
labels = list(ip_colors.keys())

# Display the legend on the left side
plt.legend(handles=handles, labels=labels, loc='upper left', fontsize=8)

# Function to zoom in/out with the scroll wheel
def zoom(event):
    # Get the current limits of the axes
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    zoom_factor = 1.1
    
    # Zoom in (scroll up) or out (scroll down)
    if event.button == 'up':
        ax.set_xlim([x * zoom_factor for x in xlim])
        ax.set_ylim([y * zoom_factor for y in ylim])
    elif event.button == 'down':
        ax.set_xlim([x / zoom_factor for x in xlim])
        ax.set_ylim([y / zoom_factor for y in ylim])
    
    # Redraw the plot to update
    fig.canvas.draw()

# Function to pan by dragging the mouse
press = None  # Initialize press as None

def on_press(event):
    global press
    press = (event.xdata, event.ydata)  # Store the initial position of the mouse click

def on_motion(event):
    global press
    if press is None:
        return
    dx = event.xdata - press[0]
    dy = event.ydata - press[1]
    # Adjust axis limits based on mouse drag
    ax.set_xlim(ax.get_xlim() - dx)
    ax.set_ylim(ax.get_ylim() - dy)
    press = (event.xdata, event.ydata)  # Update press to the current position
    fig.canvas.draw()

def on_release(event):
    global press
    press = None  # Reset press when the mouse button is released

# Connect the zoom function to mouse scroll events
fig.canvas.mpl_connect('scroll_event', zoom)

# Connect the pan function to mouse drag events
fig.canvas.mpl_connect('button_press_event', on_press)
fig.canvas.mpl_connect('motion_notify_event', on_motion)
fig.canvas.mpl_connect('button_release_event', on_release)  # Release the press when the button is released

# Show the map with the plotted IP addresses and legend
plt.title(f'Traceroute IPs to {link}')
plt.show()
