import pandas as pd
import requests
import csv

import matplotlib.pyplot as plt

# Load the CSV file
df = pd.read_csv('SystemSellAndBuyPrices-2025-02-05T16_00_00.000Z-2025-02-12T16_00_00.000Z.csv')
df['StartTime'] = pd.to_datetime(df['StartTime'])

print(df.head())

# Convert SettlementDate to string (if it's not already)
df['SettlementDate'] = df['SettlementDate'].astype(str)

# Convert StartTime to string (if it's not already)
df['StartTime'] = df['StartTime'].astype(str)

# Merge date and time columns properly
df['Datetime'] = pd.to_datetime(df['SettlementDate'] + ' ' + df['StartTime'])

# Sort by datetime
df = df.sort_values(by='Datetime')

# Set figure size
plt.figure(figsize=(12, 6))

# Plot data
plt.plot(df['Datetime'], df['NetImbalanceVolume'], label='Net Imbalance Volume', marker='o')
plt.plot(df['Datetime'], df['SystemBuyPrice'], label='System Buy Price', marker='x')

# Format plot
plt.title('Net Imbalance Volume and System Buy Price Over Time')
plt.xlabel('Time')
plt.ylabel('Value')
plt.xticks(rotation=45)

# Reduce the number of x-axis labels for readability
plt.gca().xaxis.set_major_locator(plt.MaxNLocator(nbins=10))  # Show only 10 labels

plt.legend()
plt.grid(True)
plt.tight_layout()

# Show the plot
plt.show()

# api_url1 = "https://data.elexon.co.uk/bmrs/api/v1/balancing/settlement/system-prices/2024-02-01?format=json"

# system_price = requests.get(api_url1)
# system_price.text

# system_price_json = system_price.json()

# system_price_data = system_price_json['data']
# print(system_price_data)

# def flatten_generationdata(original):
#   result = {
#       'startTime': original['startTime'],
#       'settlementPeriod':original['settlementPeriod'],
#   }

#   for element in original['data']:
#     psr_type = element['psrType']
#     result[psr_type] = element['quantity']

#   return result


# df1 = list(map(flatten_generationdata, generation_data))
