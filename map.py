import pandas as pd
import folium
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from folium import plugins

# Load the CSV file
file_path = "unionandallnj.csv"
data = pd.read_csv(file_path)

# Ensure the necessary columns exist
required_columns = ['list_price', 'description/beds', 'location/address/coordinate/lat', 
                    'location/address/coordinate/lon', 'primary_photo/href', 'location/address/line']
data = data.dropna(subset=required_columns)

# Convert necessary columns to numeric types
data['list_price'] = pd.to_numeric(data['list_price'], errors='coerce')
data['description/beds'] = pd.to_numeric(data['description/beds'], errors='coerce')
data['location/address/coordinate/lat'] = pd.to_numeric(data['location/address/coordinate/lat'], errors='coerce')
data['location/address/coordinate/lon'] = pd.to_numeric(data['location/address/coordinate/lon'], errors='coerce')

# Drop rows with missing values
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

# Get min and max for normalization
min_ppb = data['price_per_bed'].min()
max_ppb = data['price_per_bed'].max()

# Create the map
m = folium.Map(location=[mean_lat, mean_lon], zoom_start=8)

# JavaScript function to update sidebar values when clicking a property
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

        let loanAmount = price - downpayment;
        let monthlyPayment = (loanAmount * rate) / (1 - Math.pow(1 + rate, -term));

        document.getElementById("loan_payment").innerText = isNaN(monthlyPayment) ? "$0 / month" : `$${monthlyPayment.toFixed(2)} / month`;
    }
</script>
"""

# Add markers with JavaScript to update the sidebar
for _, row in data.iterrows():
    if pd.isna(row['price_per_bed']):
        continue

    # Normalize price per room for color coding
    normalized_ppb = (row['price_per_bed'] - min_ppb) / (max_ppb - min_ppb)
    color_hex = mcolors.to_hex(plt.cm.RdYlGn(1 - normalized_ppb)[:3])

    # Google Maps Link
    street_view_link = f"https://www.google.com/maps/@{row['location/address/coordinate/lat']},{row['location/address/coordinate/lon']},3a,75y,90t"
    address_html = f'<a href="{street_view_link}" target="_blank">{row["location/address/line"]} (Street View)</a>'

    # Popup Content
    popup_html = f"""
    <div onclick="setPropertyDetails({row['list_price']}, {row['description/beds']})">
        <img src='{row['primary_photo/href']}' width='150'><br>
        <b>Price:</b> ${row['list_price']:,.2f}<br>
        <b>Beds:</b> {row['description/beds']}<br>
        <b>Address:</b> {address_html}
    </div>
    """

    folium.CircleMarker(
        location=[row['location/address/coordinate/lat'], row['location/address/coordinate/lon']],
        radius=10,
        color=color_hex,
        fill=True,
        fill_color=color_hex,
        fill_opacity=0.7,
        popup=folium.Popup(popup_html, max_width=300)
    ).add_to(m)

# Add minimap
plugins.MiniMap().add_to(m)

# Save the map with sidebar
map_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Interactive Property Map</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/leaflet.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/leaflet.css" />
    
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            display: flex;
            height: 100vh;
            margin: 0;
            overflow: hidden;
        }}
        #sidebar {{
            width: 300px;
            padding: 20px;
            background: #f8f9fa;
            border-right: 2px solid #ddd;
            overflow-y: auto;
        }}
        #map-container {{
            flex-grow: 1;
        }}
        #map {{
            width: 100%;
            height: 100%;
        }}
        input, select {{
            width: 100%;
            margin-bottom: 10px;
            padding: 8px;
        }}
        button {{
            width: 100%;
            padding: 10px;
            background: #28a745;
            color: white;
            border: none;
            cursor: pointer;
        }}
        button:hover {{
            background: #218838;
        }}
    </style>
</head>
<body>

    <!-- Sidebar Calculator -->
    <div id="sidebar">
        <h3>Property Calculator</h3>
        
        <label>Purchase Price:</label>
        <input type="number" id="purchase_price" />

        <label>Number of Bedrooms:</label>
        <input type="number" id="bedrooms" />

        <label>Down Payment:</label>
        <input type="number" id="downpayment" />

        <label>Loan Type:</label>
        <select>
            <option>Fixed Mortgage</option>
            <option>Adjustable Rate</option>
        </select>

        <label>Interest Rate (%):</label>
        <input type="number" id="interest_rate" />

        <label>Loan Term (years):</label>
        <input type="number" id="loan_term" />

        <h4>Estimated Loan Payment: <span id="loan_payment">$0 / month</span></h4>
        <button onclick="calculateLoan()">Calculate</button>
    </div>

    <!-- Map Container -->
    <div id="map-container">
        {m._repr_html_()}
    </div>

    {sidebar_script}

</body>
</html>
"""

# Save the map to Flask's templates folder
map_file = "templates/map.html"
with open(map_file, "w") as file:
    file.write(map_html)

print(f"✅ Map with sidebar saved successfully at: {map_file}")
