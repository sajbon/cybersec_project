import pygame
import geopandas as gpd
import random

# Initialize Pygame
pygame.init()

# Define screen size
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Load world map using GeoPandas (after downloading and extracting the shapefile)
world = gpd.read_file("./ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp")  # Adjust the path

# Convert shapefile coordinates to pixel coordinates
# Get bounds for proper scaling
world_bounds = world.total_bounds  # [minx, miny, maxx, maxy]

# Define scaling factors based on screen size
scale_x = screen_width / (world_bounds[2] - world_bounds[0])
scale_y = screen_height / (world_bounds[3] - world_bounds[1])

# Function to convert lat/lon to screen coordinates
def lat_lon_to_pixel(lat, lon):
    x = int((lon - world_bounds[0]) * scale_x)
    y = int((world_bounds[3] - lat) * scale_y)
    return x, y

# Example: simulated IP locations with lat/lon
ip_data = [
    {"ip": "188.137.100.1", "lat": 52.23, "lon": 21.01},
    {"ip": "195.3.200.254", "lat": 50.0, "lon": 19.0},
    {"ip": "178.216.40.134", "lat": 50.2, "lon": 18.9}
]

# Initialize variables
zoom_factor = 1.0
pan_x, pan_y = 0, 0

# Initialize map image surface
map_surface = pygame.Surface((screen_width, screen_height))

# Event loop
running = True
while running:
    screen.fill((255, 255, 255))  # Clear screen with white
    map_surface.fill((255, 255, 255))  # Clear map surface

    # Draw the world map from shapefile data
    for _, shape in world.iterrows():
        # Handle both Polygon and MultiPolygon geometries
        if shape['geometry'].geom_type == 'Polygon':
            coords = shape['geometry'].exterior.coords
            pygame.draw.polygon(map_surface, (200, 200, 200), [(lat_lon_to_pixel(y, x)) for x, y in coords], 1)
        elif shape['geometry'].geom_type == 'MultiPolygon':
            for polygon in shape['geometry'].geoms:  # Use .geoms to iterate over individual polygons
                coords = polygon.exterior.coords
                pygame.draw.polygon(map_surface, (200, 200, 200), [(lat_lon_to_pixel(y, x)) for x, y in coords], 1)

    # Draw IP locations
    for ip in ip_data:
        lat, lon = ip["lat"], ip["lon"]
        x, y = lat_lon_to_pixel(lat, lon)
        pygame.draw.circle(map_surface, (255, 0, 0), (x, y), 5)

    # Display the map on screen
    screen.blit(map_surface, (pan_x, pan_y))

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                zoom_factor *= 1.1
            elif event.button == 5:  # Scroll down
                zoom_factor /= 1.1
        elif event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:  # Left click and drag
                pan_x, pan_y = pygame.mouse.get_pos()

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
