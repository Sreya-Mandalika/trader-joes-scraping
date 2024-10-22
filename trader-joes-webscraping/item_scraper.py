from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Set Chrome options to ignore certificate errors
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')

# Initialize the WebDriver with the options
driver = webdriver.Chrome(options=options)

# Initialize lists to store product details
all_products = []
all_prices = []
all_serving_size = []
all_calories = []
all_ingredients = []

# Construct the URL for the specific product (example: Organic Turkey Bone Broth)
url = "https://www.traderjoes.com/home/products/pdp/organic-turkey-bone-broth-079464"  #Replace with the actual product URL
driver.get(url)

# Wait for product elements to load
try:
    print("Waiting for product elements to load...")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'Section_section__oNcdC')))
    print("Product elements loaded.")
except Exception as e:
    print("Error loading page:", e)
    driver.quit()
    exit()

# Extract product name
product_name = driver.find_element(By.CLASS_NAME, 'ProductDetails_main__title__14Cnm').text

# Extract price
price = driver.find_element(By.CLASS_NAME, 'ProductPrice_productPrice__1Rq1r').text

# Extract calories
try:
    calories_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'Item_characteristics__3rZUg')))
    calories = calories_element.text if calories_element else "Unknown"
except Exception as e:
    print("serving_size extraction error:", e)
    calories = "Unknown"

# Extract serving size 
try:
    serving_size_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'Item_characteristics__text__dcfEC')))
    serving_size = serving_size_element.text if serving_size_element else "Unknown"
except Exception as e:
    print("serving_size extraction error:", e)
    serving_size = "Unknown"

# Extract ingredients
try:
    ingredients_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'IngredientsSummary_ingredientsSummary__allergensList__1ROpD')))
    ingredients_list = ingredients_element.find_elements(By.TAG_NAME, 'li')  # Get all ingredients as a list
    ingredients_text = ', '.join([a.text for a in ingredients_list]) if ingredients_list else "None"
except Exception as e:
    print("Ingredient first extraction error:", e)
    try:
        ingredients_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'IngredientsList_ingredientsList__1LoAJ')))
        ingredients_list = ingredients_element.find_elements(By.TAG_NAME, 'li')  # Get all ingredients as a list
        ingredients_text = ', '.join([a.text for a in ingredients_list]) if ingredients_list else "None"
    except Exception as e:
        print("Ingredient second extraction error:", e)
        try:
            ingredients_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'IngredientsList_ingredientsList__1LoAJ')))
            ingredients_list = ingredients_element.find_elements(By.TAG_NAME, 'li')  # Get all ingredients as a list
            ingredients_text = ', '.join([a.text for a in ingredients_list]) if ingredients_list else "None"
        except Exception as e:
            print("Ingredient extraction error:", e)
            ingredients_text = "Unknown"

# Print the results
print(f"Product: {product_name}")
print(f"Price: {price}")
print(f"Serving Size: {serving_size}")
print(f"Calories: {calories}")
print(f"Ingredients: {ingredients_text}")

# Close the WebDriver
driver.quit()
