#!/bin/bash
# Download Natural Earth 110m countries GeoJSON
curl -L "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson" -o ne_110m_countries.json
echo "Downloaded Natural Earth GeoJSON to public/ne_110m_countries.json"
