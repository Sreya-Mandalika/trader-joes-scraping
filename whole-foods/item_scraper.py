from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Initialize the webdriver
driver = webdriver.Chrome()

# Open the Whole Foods product page URL
url = "https://www.wholefoodsmarket.com/product/whole-foods-market-moms-chicken-soup-24-oz-b0884p2jxq"  # Replace with your product URL
driver.get(url)

# Wait for the Nutrition tab to be clickable and click it
try:
    nutrition_tab = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Nutrition')]"))
    )
    nutrition_tab.click()

    # Wait for the serving size element to load and get its text
    serving_size = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.nutrition-column.text-md.text-bold.text-right"))
    ).text

    # Wait for the calories element to load and get its text
    calories = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.nutrition-column.calories-row.amount.text-right.align-bottom"))
    ).text

except Exception as e:
    serving_size = "Unknown"
    calories = "Unknown"
    print(f"Error extracting nutrition information: {e}")

# Print the nutrition information
print(f"Serving Size: {serving_size}")
print(f"Calories: {calories}")

# Now click the Ingredients tab to get the ingredients
try:
    ingredients_tab = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Ingredients')]"))
    )
    ingredients_tab.click()

    # Wait for the ingredients element to load and get its text
    ingredients = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "tabpanel_Ingredients"))
    ).find_element(By.TAG_NAME, "p").text

except Exception as e:
    ingredients = "Unknown"
    print(f"Error extracting ingredients: {e}")

# Print the ingredients
print(f"Ingredients: {ingredients}")

# Close the WebDriver
driver.quit()
