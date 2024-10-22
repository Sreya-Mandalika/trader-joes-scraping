from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import re
import time

# Initialize the WebDriver
driver = webdriver.Chrome()

# Initialize lists to store product names, prices, and details
all_products = []
all_prices = []
all_serving_size = []
all_calories = []
all_ingredients = []
all_allergens = []

# Loop through the first pages
for page in range(1, 2):  # Change 2 to 71 for all pages
    print(f"Opening page {page}...")

    url = f"https://www.traderjoes.com/home/products/category/food-8?filters=%7B%22page%22%3A{page}%7D"
    driver.get(url)

    # Wait for product elements to load
    try:
        print("Waiting for product elements to load...")
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'ProductCard_card__title__text__uiWLe')))
        print("Product elements loaded.")
    except Exception as e:
        print("Error loading page:", e)
        driver.quit()
        exit()

    # Optionally scroll down to load more products
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    # Collect all product and price elements on this page
    product_elements = driver.find_elements(By.CLASS_NAME, 'ProductCard_card__title__text__uiWLe')
    price_elements = driver.find_elements(By.CLASS_NAME, 'ProductPrice_productPrice__1Rq1r')

    print(f"Found {len(product_elements)} products and {len(price_elements)} prices.")

    # Loop through products and collect details
    for i in range(len(product_elements)):
        # Re-find the product elements in case the DOM has changed
        product_elements = driver.find_elements(By.CLASS_NAME, 'ProductCard_card__title__text__uiWLe')
        price_elements = driver.find_elements(By.CLASS_NAME, 'ProductPrice_productPrice__1Rq1r')  # Reload prices to avoid StaleElementReferenceException

        product = product_elements[i]
        product_name = product.text.strip().replace("\n", " ") if product.text else "Unknown"
        all_products.append(product_name)

        # Add corresponding price
        price = price_elements[i].text.strip().replace("\n", " ") if i < len(price_elements) and price_elements[i].text else "Unknown"
        all_prices.append(price)

        # Click on the product to go to the detail page
        try:
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, product_name))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            driver.execute_script("arguments[0].click();", element)

            product_url = driver.current_url
            print(f"Current URL after clicking: {product_url}")

            # Ensure we stay on the page for at least 5 seconds
            time.sleep(5)

            # Wait for product detail elements to load
            try:
                print("Waiting for product details to load...")
                WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'Section_section__oNcdC')))
                print("Product details loaded.")
            except Exception as e:
                print("Error loading product page:", e)
                driver.quit()
                exit()

            # Extract calories
            try:
                calories_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'Item_characteristics__3rZUg')))
                calories = calories_element.text.strip().replace("\n", " ") if calories_element else "Unknown"
            except Exception as e:
                print("Calories extraction error")
                calories = "Unknown"
            all_calories.append(calories)

            # Extract serving size
            try:
                serving_size_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'Item_characteristics__text__dcfEC')))
                serving_size = serving_size_element.text.strip().replace("\n", " ") if serving_size_element else "Unknown"
            except Exception as e:
                print("Serving size extraction error")
                serving_size = "Unknown"
            all_serving_size.append(serving_size)

            # First attempt to find ingredients in the main ingredients section
            try:
                ingredients_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'IngredientsList_ingredientsList__1LoAJ'))
                )
                ingredients_list = ingredients_element.find_elements(By.TAG_NAME, 'li')  # Get all ingredients as a list
                ingredients_text = ', '.join([a.text for a in ingredients_list]) if ingredients_list else "None"
            except Exception as e:
                print("Ingredient extraction error")
                ingredients_text = "Unknown"

            # Append ingredients text to the list
            all_ingredients.append(ingredients_text)

            # Extract allergens
            try:
                allergens_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'IngredientsSummary_ingredientsSummary__allergensList__1ROpD')))
                allergens = allergens_element.text.strip().replace("\n", " ") if allergens_element else "Unknown"
            except Exception as e:
                print("Allergens extraction error")
                allergens = "Unknown"
            all_allergens.append(allergens)

        except Exception as e:
            print(f"An error occurred while clicking the product: {e}")
            all_calories.append("Unknown")
            all_serving_size.append("Unknown")
            all_ingredients.append("Unknown")
            all_allergens.append("Unknown")

        # Navigate back to the listing page to continue processing other products
        driver.back()

        # Add a small delay after navigating back to give the page time to reload
        time.sleep(2)

# Ensure all lists have the same length
max_length = max(len(all_products), len(all_prices), len(all_serving_size), len(all_calories), len(all_ingredients))
all_products += ["Unknown"] * (max_length - len(all_products))
all_prices += ["Unknown"] * (max_length - len(all_prices))
all_serving_size += ["Unknown"] * (max_length - len(all_serving_size))
all_calories += ["Unknown"] * (max_length - len(all_calories))
all_ingredients += ["Unknown"] * (max_length - len(all_ingredients))
all_allergens += ["Unknown"] * (max_length - len(all_allergens))

# Create DataFrame
products_df = pd.DataFrame({
    'Product': all_products,
    'Price': all_prices,
    'Serving Size': all_serving_size,
    'Calories': all_calories,
    'Ingredients': all_ingredients,
    'Allergens': all_allergens
})

# 1. Split Price into Price and Ounces (splitting on the '/')
products_df[['Price', 'Ounces']] = products_df['Price'].str.split('/', expand=True)
products_df['Price'] = products_df['Price'].str.replace('$', '', regex=False).astype(float, errors='ignore')
products_df['Ounces'] = products_df['Ounces'].str.replace('oz', '').str.strip()

# 2. Extract only the calories after 'CALORIES PER SERVING'
products_df['Calories'] = products_df['Calories'].apply(lambda x: re.search(r'CALORIES PER SERVING (\d+)', x).group(1) if re.search(r'CALORIES PER SERVING (\d+)', x) else 'Unknown')

# 3. Capitalize the first letter of each word in Ingredients and Allergens
products_df['Ingredients'] = products_df['Ingredients'].apply(lambda x: ' '.join([word.capitalize() for word in x.split()]) if x != 'Unknown' else 'Unknown')
products_df['Allergens'] = products_df['Allergens'].apply(lambda x: ' '.join([word.capitalize() for word in x.split()]) if x != 'Unknown' else 'Unknown')

# Save to CSV
products_df.to_csv('trader_joes_products_cleaned.csv', index=False)

print("Data saved to trader_joes_products_cleaned.csv.")

# Close the WebDriver
driver.quit()
