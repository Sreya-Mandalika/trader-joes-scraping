from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Initialize the WebDriver
driver = webdriver.Chrome()

# Initialize lists to store product details
all_products = []
all_prices = []
all_serving_sizes = []
all_calories = []
all_ingredients = []
all_allergens = []
all_amounts = []
product_links = []

# Open the Whole Foods product page URL
driver.get("https://www.wholefoodsmarket.com/products/snacks-chips-salsas-dips")

# Wait for the popup and close it if present
try:
    print("Waiting for popup to close...")
    popup_close_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'w-button--close'))
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

# Collect product names and links
product_elements = driver.find_elements(By.CLASS_NAME, 'w-cms--font-body__sans-bold')
for product in product_elements:
    product_text = product.text.strip()
    if product_text and "Product" not in product_text and "Category" not in product_text and "Filters" not in product_text and "Featured" not in product_text and "Dietary Restrictions" not in product_text:
        all_products.append(product_text)

        # Try to find the product link correctly
        try:
            product_link = product.find_element(By.XPATH, "./ancestor::a").get_attribute('href')
            product_links.append(product_link)
        except Exception as e:
            print(f"Error finding link for product '{product_text}': {e}")

# Remove the first item in all_products to exclude "Dietary Preference" or other undesired labels
if all_products:
    all_products.pop(0)

# Extract prices using JavaScript
price_elements_js = driver.execute_script("""
    return Array.from(document.querySelectorAll('.text-left.bds--heading-5')).map(el => el.innerText);
""")
all_prices.extend(price_elements_js)

# Extract additional details for each product
for index, link in enumerate(product_links):
    driver.get(link)
    time.sleep(2)  # Keep the page open longer for each product

    try:
        # Wait for product page to load and click "Nutrition" tab
        nutrition_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Nutrition')]"))
        )
        nutrition_tab.click()

        # Extract serving size and calories
        serving_size = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.nutrition-column.text-md.text-bold.text-right"))
        ).text
        calories = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.nutrition-column.calories-row.amount.text-right.align-bottom"))
        ).text
    except Exception:
        serving_size = "Unknown"
        calories = "Unknown"

    try:
        # Click "Ingredients" tab and extract ingredients
        ingredients_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Ingredients')]"))
        )
        ingredients_tab.click()
        ingredients = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "tabpanel_Ingredients"))
        ).find_element(By.TAG_NAME, "p").text.replace("Ingredients:", "").strip('"')
    except Exception:
        ingredients = "Unknown"

    try:
        # Check for allergens
        allergens = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@id='tabpanel_Ingredients']//h3[contains(text(), 'Allergens')]/following-sibling::p"))
        ).text
    except Exception:
        allergens = "Unknown"

    # Extract amount information based on label, price, or servings
    amount = "Unknown"
    
    # Check for labeled amount in the product name
    if ',' in all_products[index]:
        product_name_split = all_products[index].split(',')
        all_products[index] = product_name_split[0].strip()
        label_amount = product_name_split[1].strip()
        if any(unit in label_amount for unit in ["oz", "ml", "lb"]):  # Check for standard units
            amount = label_amount

    # Check if the price mentions a per-pound price
    if amount == "Unknown" and "/lb" in all_prices[index]:
        amount = "1 lb"

    # Revisit Nutrition tab to check for servings if amount is still unknown
    if amount == "Unknown":
        try:
            nutrition_tab.click()  # Ensure we're on the Nutrition tab
            servings = driver.find_element(By.CLASS_NAME, 'servings').text.strip()
            if servings:
                amount = servings
        except Exception:
            pass  # Keep amount as "Unknown" if servings not found

    # Append all the collected data
    all_serving_sizes.append(serving_size)
    all_calories.append(calories)
    all_ingredients.append(ingredients)
    all_allergens.append(allergens)
    all_amounts.append(amount)  # Use all_amounts instead of all_ounces

    # Go back to the listing page
    driver.back()
    WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'w-cms--font-body__sans-bold'))
    )

# Debugging: Print product and price lengths
print(f"Collected {len(all_products)} products and {len(all_prices)} prices.")

# Pad lists to ensure all lists are the same length
max_length = max(len(all_products), len(all_prices), len(all_serving_sizes), len(all_calories), len(all_ingredients), len(all_allergens), len(all_amounts))
all_products += ["Unknown"] * (max_length - len(all_products))
all_prices += ["Unknown"] * (max_length - len(all_prices))
all_serving_sizes += ["Unknown"] * (max_length - len(all_serving_sizes))
all_calories += ["Unknown"] * (max_length - len(all_calories))
all_ingredients += ["Unknown"] * (max_length - len(all_ingredients))
all_allergens += ["Unknown"] * (max_length - len(all_allergens))
all_amounts += ["Unknown"] * (max_length - len(all_amounts))

# Create DataFrame
products_df = pd.DataFrame({
    'Product': all_products,
    'Price': all_prices,
    'Amount': all_amounts,  # Updated column name
    'Serving Size': all_serving_sizes,
    'Calories': all_calories,
    'Ingredients': all_ingredients,
    'Allergens': all_allergens
})

products_df['Price'] = products_df['Price'].str.extract(r'(\$\d+\.\d{2})')

# Remove any "Ingredients:" or similar variants at the beginning of the ingredients text
products_df['Ingredients'] = products_df['Ingredients'].str.replace(r'(?i)^ingredients[:\s]*', '', regex=True)

products_df.to_csv('whole_foods_snacks.csv', index=False)

print("Data saved to whole_foods_snacks.csv.")

# Close the WebDriver
driver.quit()
