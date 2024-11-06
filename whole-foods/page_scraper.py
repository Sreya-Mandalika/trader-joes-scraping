from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Initialize the WebDriver
driver = webdriver.Chrome()

# Initialize lists to store product names and prices
all_products = []
all_prices = []

# Open the Whole Foods product page URL
driver.get("https://www.wholefoodsmarket.com/products/meat")

# Wait for the popup and close it if present
try:
    print("Waiting for popup to close...")
    popup_close_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'w-button--close'))  # Adjust based on actual close button class
    )
    popup_close_button.click()
    print("Closed the popup.")
except Exception as e:
    print("No popup or error:", e)

# Wait for the initial product elements to load
try:
    print("Waiting for product elements to load...")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'w-cms--font-body__sans-bold')))
    print("Product elements loaded.")
except Exception as e:
    print("Error loading page:", e)
    driver.quit()
    exit()

# Load more products until the button is no longer present
while True:
    try:
        load_more_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.w-button--load-more"))
        )
        load_more_button.click()
        print("Clicked Load More button.")
        time.sleep(5)  # Extended wait for new products to load
        
    except Exception as e:
        print("No more products to load or error:", e)
        break  # Exit the loop if the button is not found or there's an error

# Extract product elements
product_elements = driver.find_elements(By.CLASS_NAME, 'w-cms--font-body__sans-bold')

# Collect product names
for product in product_elements:
    product_text = product.text.strip()
    if product_text and "Product" not in product_text and "Category" not in product_text and "Filters" not in product_text and "Featured" not in product_text:
        all_products.append(product_text)

# Try to extract prices using JavaScript
price_elements_js = driver.execute_script("""
    return Array.from(document.querySelectorAll('.text-left.bds--heading-5')).map(el => el.innerText);
""")

# If JavaScript extraction was successful, add prices to list
all_prices.extend(price_elements_js)

# Debugging: Print product and price lengths
print(f"Collected {len(all_products)} products and {len(all_prices)} prices.")

# Ensure both lists are the same length
max_length = max(len(all_products), len(all_prices))
all_products += ["Unknown"] * (max_length - len(all_products))
all_prices += ["Unknown"] * (max_length - len(all_prices))

# Create DataFrame
products_df = pd.DataFrame({
    'Product': all_products,
    'Price': all_prices
})

# Save to CSV
products_df.to_csv('whole_foods_products.csv', index=False)

print("Data saved to whole_foods_products.csv.")

# Close the WebDriver
driver.quit()
