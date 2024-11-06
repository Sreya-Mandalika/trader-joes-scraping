from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Initialize the WebDriver
driver = webdriver.Chrome()

# Define the product listing URL
product_listing_url = "https://www.wholefoodsmarket.com/products/produce?diets=paleo-friendly%2Cdairy-free%2Cwhole-foods-diet%2Cvegetarian%2Cketo-friendly%2Cgluten-free%2Corganic%2Cvegan%2Clow-fat"

def fetch_product_elements():
    return driver.find_elements(By.XPATH, "//a[@class='w-pie--product-tile__link']")

try:
    driver.get(product_listing_url)
    print("Waiting for product elements to load...")
    
    # Wait for the products to load
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "w-pie--product-tile__link")))
    print("Product elements loaded.")

    # Click the "Load More" button if it exists
    while True:
        try:
            load_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Load More')]"))
            )
            load_more_button.click()
            print("Clicked Load More button.")
            time.sleep(2)  # Wait for new products to load
        except Exception:
            print("No more products to load or error.")
            break

    current_index = 0

    while True:
        products = fetch_product_elements()  # Get fresh list of products
        product_count = len(products)

        if product_count == 0:
            print("No products available to process.")
            break

        if current_index >= product_count:
            print("No more products left to process.")
            break

        try:
            product_link = products[current_index]

            # Wait for the link to be clickable
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(product_link)
            )
            product_link.click()
            print(f"Clicked on {product_link.text.strip()}.")

            # Wait for the product page to load completely
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product-details"))
            )

            # Extract nutrition information
            # You can include your previous nutrition extraction code here

            # Forcefully navigate back to the product listing page
            driver.get(product_listing_url)
            print("Forcefully returned to product listing.")

            # Wait for the product listing to load again
            WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "w-pie--product-tile__link"))
            )

            # Increment current index to process the next product
            current_index += 1  

        except Exception as e:
            print(f"Error processing product at index {current_index}: {e}")
            time.sleep(2)  # Wait before re-fetching
            driver.get(product_listing_url)  # Forcefully return to the product listing page
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "w-pie--product-tile__link"))
            )  # Ensure elements are loaded again
            current_index += 1  # Attempt to process the next product

finally:
    driver.quit()
