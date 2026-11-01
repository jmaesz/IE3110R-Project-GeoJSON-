# IE3110R Bus 96 GeoJSON Project

This project uses Bus 96 route and bus stop data to estimate the distance along the route between consecutive stops (chainage).

## Files

- `bus96_route_chainage.py` — Python script that loads the route and stop data, projects their coordinates into metres, finds the closest suitable point on the route for each stop, orders stops by distance along the route, and prints the distance between each pair of consecutive stops. It also prints the total route length using both the projected coordinates and a WGS84 geodesic calculation.
- `bus_96_busrouter_sg.geojson` — GeoJSON route geometry for Bus 96. The script uses this line to calculate distance along the route.
- `bus_96_stops.geojson` — GeoJSON bus stop locations and properties, including stop codes and labels. The script uses these to place and identify stops along the route.
- `README.md` — This project description and the data credit.

## Data credit

The Bus 96 route and bus stop data are credited to [BusRouter SG](https://busrouter.sg/).
