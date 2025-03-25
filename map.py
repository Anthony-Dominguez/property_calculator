import pandas as pd
import folium
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from folium import plugins
import json

# Load the CSV file
file_path = "updated_dataset.csv"
data = pd.read_csv(file_path)

# Ensure ZIP codes are read as strings and cleaned up
data['zipcode'] = data['zipcode'].astype(str)
data['zipcode'] = data['zipcode'].replace(['nan', 'NaN', 'None', 'inf', '-inf'], '')
data = data[data['zipcode'].str.strip() != '']
data['zipcode'] = data['zipcode'].astype(float).astype(int).astype(str).str.zfill(5)

print(data[['zipcode']].head(10))
print(data['zipcode'].dtype)

# Ensure the necessary columns exist
required_columns = ['list_price', 'description/beds', 'location/address/coordinate/lat', 
                    'location/address/coordinate/lon', 'primary_photo/href', 'location/address/line','description/baths_consolidated']
data = data.dropna(subset=required_columns)

# Convert necessary columns to numeric types
data['list_price'] = pd.to_numeric(data['list_price'], errors='coerce')
data['description/beds'] = pd.to_numeric(data['description/beds'], errors='coerce')
data['location/address/coordinate/lat'] = pd.to_numeric(data['location/address/coordinate/lat'], errors='coerce')
data['location/address/coordinate/lon'] = pd.to_numeric(data['location/address/coordinate/lon'], errors='coerce')
data['description/baths_consolidated'] = pd.to_numeric(data['description/baths_consolidated'], errors='coerce')


data = data.dropna(subset=['list_price', 'description/beds', 'location/address/coordinate/lat', 
                           'location/address/coordinate/lon'])

# Compute map center
mean_lat = data['location/address/coordinate/lat'].mean()
mean_lon = data['location/address/coordinate/lon'].mean()

# Compute price per bed (avoid division by zero)
data['price_per_bed'] = data.apply(
    lambda row: row['list_price'] / row['description/beds'] if row['description/beds'] > 0 else None,
    axis=1
)
min_ppb = data['price_per_bed'].min()
max_ppb = data['price_per_bed'].max()

# Create the base map (set width and height to "100%" so that our container CSS can work)
m = folium.Map(location=[mean_lat, mean_lon], zoom_start=8, width="100%", height="100%")
plugins.MiniMap().add_to(m)

# JavaScript for sidebar functions (loan calculator and property details update)
sidebar_script = """
<script>
    function setPropertyDetails(price, beds) {
        document.getElementById("purchase_price").value = price;
        document.getElementById("bedrooms").value = beds;
    }

    function calculateLoan() {
        let price = parseFloat(document.getElementById("purchase_price").value) || 0;
        let downpayment = parseFloat(document.getElementById("downpayment").value) || 0;
        let rate = parseFloat(document.getElementById("interest_rate").value) / 100 / 12;
        let term = parseFloat(document.getElementById("loan_term").value) * 12;
        
        let renovationBudget = parseFloat(document.getElementById("renovation_budget").value) || 0;
        let closingCost = parseFloat(document.getElementById("closing_cost").value) || 0;
        let includeRenovation = document.getElementById("include_renovation").checked;
        let includeClosing = document.getElementById("include_closing").checked;
        
        let extraCosts = 0;
        if (includeRenovation) {
            extraCosts += renovationBudget;
        }
        if (includeClosing) {
            extraCosts += closingCost;
        }
        
        let loanAmount = price + extraCosts - downpayment;
        let monthlyPayment = (rate === 0)
            ? (loanAmount / term)
            : (loanAmount * rate) / (1 - Math.pow(1 + rate, -term));
        
        document.getElementById("loan_payment").innerText = isNaN(monthlyPayment) 
            ? "$0 / month" 
            : "$" + monthlyPayment.toFixed(2) + " / month";
    }
</script>
"""

# Prepare marker data for JavaScript
marker_data = []
for _, row in data.iterrows():
    if pd.isna(row['price_per_bed']):
        continue
    normalized_ppb = (row['price_per_bed'] - min_ppb) / (max_ppb - min_ppb)
    color_hex = mcolors.to_hex(plt.cm.RdYlGn(1 - normalized_ppb)[:3])
    zip_code = str(row['zipcode']).zfill(5)
    
    street_view_link = f"https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={row['location/address/coordinate/lat']},{row['location/address/coordinate/lon']}"
    address_html = f'<a href="{street_view_link}" target="_blank">{row["location/address/line"]} (Street View)</a>'
    
    popup_html = f"""
    <div onclick="setPropertyDetails({row['list_price']}, {int(row['description/beds'])})">
        <img src="{row['primary_photo/href']}" width="200"><br>
        <b>Price:</b> ${row['list_price']:,.2f}<br>
        <b>Beds:</b> {int(row['description/beds'])}<br>
        <b>Bathrooms:</b> {(row['description/baths_consolidated'])}<br> 
        <b>Address:</b> {address_html}<br>
        <b>Zip code:</b> {zip_code}<br>
    </div>
    """
    marker_data.append({
        "lat": row['location/address/coordinate/lat'],
        "lon": row['location/address/coordinate/lon'],
        "popup": popup_html,
        "color": color_hex,
        "zipcode": zip_code
    })
    
    folium.CircleMarker(
        location=[row['location/address/coordinate/lat'], row['location/address/coordinate/lon']],
        radius=10,
        color=color_hex,
        fill=True,
        fill_color=color_hex,
        fill_opacity=0.7,
        popup=folium.Popup(popup_html, max_width=300)
    ).add_to(m)

marker_json = json.dumps(marker_data)

# Build the complete HTML page with dark, modern styling
map_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Interactive Property Map</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css?family=Roboto:400,500,700&display=swap" rel="stylesheet">
    
    <!-- Leaflet CSS & JS, and jQuery -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/leaflet.css" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/leaflet.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    
    <style>
        html, body {{
            height: 100vh;
            margin: 0;
            font-family: 'Roboto', sans-serif;
            background-color: #121212;
            color: #e0e0e0;
        }}
        /* Flex container for sidebar and map */
        #container {{
            display: flex;
            height: 100vh;
        }}
        #sidebar {{
            width: 320px;
            padding: 20px;
            background: #1e1e1e;
            box-shadow: 2px 0 10px rgba(0, 0, 0, 0.7);
            overflow-y: auto;
        }}
        #sidebar h3 {{
            margin-top: 0;
            color: #ffffff;
        }}
        #sidebar label {{
            display: block;
            margin-bottom: 5px;
            color: #bbbbbb;
        }}
        #sidebar input[type="number"],
        #sidebar input[type="text"],
        #sidebar select {{
            width: 100%;
            padding: 8px;
            margin-bottom: 15px;
            border: 1px solid #333;
            border-radius: 4px;
            background: #2a2a2a;
            color: #e0e0e0;
        }}
        #sidebar button {{
            width: 100%;
            padding: 10px;
            background: #64ffda;
            color: #121212;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.3s ease;
        }}
        #sidebar button:hover {{
            background: #52d0b0;
        }}
        .checkbox-label {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }}
        .checkbox-label input {{
            margin-right: 8px;
        }}
        #map-container {{
            flex: 1;
            height: 100vh;
            position: relative;
        }}
        /* Force the inner Folium map to fill its container */
        #map-container > div {{
            position: absolute !important;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
        }}
    </style>
</head>
<body>
    <div id="container">
        <div id="sidebar">
            <h3>Property Filter</h3>
            <label>Filter by ZIP Code:</label>
            <input type="text" id="zipcode_filter" placeholder="Enter ZIP Code" />
            <button type="button" onclick="filterMarkers()">Apply Filter</button>
            <hr>
            <h3>Property Calculator</h3>
            <label>Purchase Price:</label>
            <input type="number" id="purchase_price" />
            <label>Number of Bedrooms:</label>
            <input type="number" id="bedrooms" />
            <label>Down Payment:</label>
            <input type="number" id="downpayment" />
            <label>Renovation Budget:</label>
            <input type="number" id="renovation_budget" />
            <div class="checkbox-label">
                <input type="checkbox" id="include_renovation" />
                <label for="include_renovation">Include Renovation Budget in Loan</label>
            </div>
            <label>Closing Cost:</label>
            <input type="number" id="closing_cost" />
            <div class="checkbox-label">
                <input type="checkbox" id="include_closing" />
                <label for="include_closing">Include Closing Cost in Loan</label>
            </div>
            <label>Loan Type:</label>
            <select>
                <option>Fixed Mortgage</option>
                <option>Adjustable Rate</option>
            </select>
            <label>Interest Rate (%):</label>
            <input type="number" id="interest_rate" />
            <label>Loan Term (years):</label>
            <input type="number" id="loan_term" />
            <h4>Estimated Loan Payment:</h4>
            <p id="loan_payment" style="font-size:18px; font-weight:500;">$0 / month</p>
            <button type="button" onclick="calculateLoan()">Calculate</button>
        </div>
        <div id="map-container">
            {m._repr_html_()}
        </div>
    </div>
    {sidebar_script}
</body>
</html>
"""

# Save the final HTML to Flask's templates folder
map_file = "templates/map.html"
with open(map_file, "w") as file:
    file.write(map_html)

print(f"✅ Map with modern dark theme saved successfully at: {map_file}")