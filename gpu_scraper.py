import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import mplcursors  # For hover functionality

# URL of the GPU database
url = "https://www.techpowerup.com/gpu-specs/"

# Send a GET request to the website
response = requests.get(url)

# Check if the request was successful
if response.status_code != 200:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
    exit()

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Locate the table within the div with id="list" and class="table-wrapper"
table_wrapper = soup.find('div', {'id': 'list', 'class': 'table-wrapper'})
if not table_wrapper:
    print("Table wrapper not found on the page.")
    exit()

# Find the GPU table with class="processors"
gpu_table = table_wrapper.find('table', {'class': 'processors'})
if not gpu_table:
    print("GPU table not found on the page.")
    exit()

# Extract table headers
headers = []
# Find the header row in the thead with class="colheader"
header_row = gpu_table.find('thead', {'class': 'colheader'}).find('tr')
if header_row:
    for th in header_row.find_all('th'):
        headers.append(th.text.strip())
else:
    print("Header row not found in the table.")
    exit()

# Debug: Print extracted headers
print("Extracted Headers:", headers)

# If headers are empty, manually define them based on the website's structure
if not headers:
    headers = ["Product Name", "GPU Chip", "Released", "Bus", "Memory", "GPU clock", "Memory clock", "Shaders / TMUs / ROPs"]

# Extract GPU data rows
gpu_data = []
# Find all rows directly under the table (since there's no tbody)
rows = gpu_table.find_all('tr')
for row in rows:
    # Skip rows that are part of the header
    if row.find('th'):
        continue
    columns = row.find_all('td')
    if len(columns) == len(headers):  # Ensure the row has the expected number of columns
        row_data = []
        for col in columns:
            # Handle links (e.g., GPU Chip)
            if col.find('a'):
                row_data.append(col.find('a').text.strip())
            else:
                row_data.append(col.text.strip())
        gpu_data.append(row_data)

# Convert the data into a pandas DataFrame
df = pd.DataFrame(gpu_data, columns=headers)

# Debug: Print the first few rows of the DataFrame
print(df.head())

# Clean and convert GPU clock and Memory clock to numeric values
df['GPU clock'] = pd.to_numeric(df['GPU clock'].str.replace(' MHz', ''), errors='coerce')
df['Memory clock'] = pd.to_numeric(df['Memory clock'].str.replace(' MHz', ''), errors='coerce')

# Drop rows with missing values in GPU clock or Memory clock
df = df.dropna(subset=['GPU clock', 'Memory clock'])

# Sort the DataFrame by GPU clock for better visualization
df = df.sort_values(by='GPU clock', ascending=False)

# Reset the index after sorting
df = df.reset_index(drop=True)

# Plot the data
plt.figure(figsize=(14, 10))  # Adjust figure size for vertical bars

# Bar plot for GPU clock
plt.subplot(1, 2, 1)  # 1 row, 2 columns, first plot
bars_gpu = plt.barh(df['Product Name'], df['GPU clock'], color='blue', label='GPU Clock (MHz)')  # Use barh for horizontal bars
plt.xlabel('GPU Clock (MHz)')
plt.ylabel('GPU Model')
plt.title('GPU Clock Speeds')
plt.legend()

# Bar plot for Memory clock
plt.subplot(1, 2, 2)  # 1 row, 2 columns, second plot
bars_memory = plt.barh(df['Product Name'], df['Memory clock'], color='green', label='Memory Clock (MHz)')  # Use barh for horizontal bars
plt.xlabel('Memory Clock (MHz)')
plt.ylabel('GPU Model')
plt.title('Memory Clock Speeds')
plt.legend()

# Add hover functionality using mplcursors
cursor_gpu = mplcursors.cursor(bars_gpu, hover=True)
cursor_memory = mplcursors.cursor(bars_memory, hover=True)

# Define what to display on hover
@cursor_gpu.connect("add")
def on_add_gpu(sel):
    sel.annotation.set_text(
        f"Model: {df['Product Name'][sel.index]}\n"
        f"Released: {df['Released'][sel.index]}\n"
        f"GPU Clock: {df['GPU clock'][sel.index]} MHz"
    )

@cursor_memory.connect("add")
def on_add_memory(sel):
    sel.annotation.set_text(
        f"Model: {df['Product Name'][sel.index]}\n"
        f"Released: {df['Released'][sel.index]}\n"
        f"Memory Clock: {df['Memory clock'][sel.index]} MHz"
    )

# Adjust layout to prevent overlap
plt.tight_layout()

# Show the plot
plt.show()