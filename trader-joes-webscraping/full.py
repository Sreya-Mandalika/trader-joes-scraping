from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import re
import time

driver = webdriver.Chrome()

# initialize lists to store product names, prices, and details
all_products = []
all_prices = []
all_serving_size = []
all_calories = []
all_ingredients = []
all_allergens = []

# Extract elements and check for mismatches
def get_elements(driver, class_name, expected_count):
    elements = driver.find_elements(By.CLASS_NAME, class_name)
    while len(elements) < expected_count:
        print(f"Retrying... Expected {expected_count}, found {len(elements)} elements.")
        time.sleep(1) 
        elements = driver.find_elements(By.CLASS_NAME, class_name)
    return elements

for page in range(1, 11):
    print(f"Opening page {page}...")

    url = f"https://www.traderjoes.com/home/products/category/beverages-182"
    driver.get(url)

    # wait for product elements to load
    try:
        print("Waiting for product elements to load...")
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'ProductCard_card__title__text__uiWLe')))
        print("Product elements loaded.")
    except Exception as e:
        print("Error loading page:", e)
        driver.quit()
        exit()

    # scroll down to load more products if needed
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    # collect all product and price elements on this page
    product_elements = driver.find_elements(By.CLASS_NAME, 'ProductCard_card__title__text__uiWLe')
    price_elements = driver.find_elements(By.CLASS_NAME, 'ProductPrice_productPrice__1Rq1r')

    # check if product and price elements are equal - skip if mismatch
    print(f"Found {len(product_elements)} products and {len(price_elements)} prices.")
    if len(product_elements) != len(price_elements):
        print(f"Mismatch: {len(product_elements)} products, {len(price_elements)} prices. Skipping page.")
        continue

    # loop through products and collect details
    for i in range(len(product_elements)):
        try:
            product_elements = get_elements(driver, 'ProductCard_card__title__text__uiWLe', len(product_elements))
            price_elements = get_elements(driver, 'ProductPrice_productPrice__1Rq1r', len(price_elements)) 

            product = product_elements[i]
            product_name = product.text.strip().replace("\n", " ") if product.text else "Unknown"
            all_products.append(product_name)

            # add product price 
            price = price_elements[i].text.strip().replace("\n", " ") if i < len(price_elements) and price_elements[i].text else "Unknown"
            all_prices.append(price)

            # click on product and go to its corresponding page
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, product_name))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                driver.execute_script("arguments[0].click();", element)

                product_url = driver.current_url
                print(f"Current URL after clicking: {product_url}")

                # wait for product elements to load properly 
                time.sleep(5)

                try:
                    print("Waiting for product details to load...")
                    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'Section_section__oNcdC')))
                    print("Product details loaded.")
                except Exception as e:
                    print("Error loading product page:", e)
                    driver.back()
                    continue 

                # extract calories
                try:
                    calories_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'Item_characteristics__3rZUg')))
                    calories = calories_element.text.strip().replace("\n", " ") if calories_element else "Unknown"
                except Exception as e:
                    print("Calories extraction error.")
                    calories = "Unknown"
                all_calories.append(calories)

                # extract serving size
                try:
                    serving_size_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'Item_characteristics__text__dcfEC')))
                    serving_size = serving_size_element.text.strip().replace("\n", " ") if serving_size_element else "Unknown"
                except Exception as e:
                    print("Serving size extraction error.")
                    serving_size = "Unknown"
                all_serving_size.append(serving_size)

                # extract ingredients 
                try:
                    ingredients_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'IngredientsList_ingredientsList__1LoAJ'))
                    )
                    ingredients_list = ingredients_element.find_elements(By.TAG_NAME, 'li')  # Get all ingredients as a list
                    ingredients_text = ', '.join([a.text for a in ingredients_list]) if ingredients_list else "None"
                except Exception as e:
                    print("Ingredient extraction error.")
                    ingredients_text = "Unknown"
                all_ingredients.append(ingredients_text)

                # extract allergens
                try:
                    allergens_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'IngredientsSummary_ingredientsSummary__allergensList__1ROpD')))
                    allergens = allergens_element.text.strip().replace("\n", " ") if allergens_element else "Unknown"
                except Exception as e:
                    print("Allergens extraction error.")
                    allergens = "Unknown"
                all_allergens.append(allergens)

            except Exception as e:
                print(f"An error occurred while clicking the product: {e}")
                all_calories.append("Unknown")
                all_serving_size.append("Unknown")
                all_ingredients.append("Unknown")
                all_allergens.append("Unknown")

            # navigate back to main page and add delay to let page reload 
            driver.back()
            time.sleep(2)

        except IndexError:
            print(f"IndexError: List index out of range at product {i} on page {page}. Skipping product.")
            continue  

# make sure all lists have the same length
max_length = max(len(all_products), len(all_prices), len(all_serving_size), len(all_calories), len(all_ingredients))
all_products += ["Unknown"] * (max_length - len(all_products))
all_prices += ["Unknown"] * (max_length - len(all_prices))
all_serving_size += ["Unknown"] * (max_length - len(all_serving_size))
all_calories += ["Unknown"] * (max_length - len(all_calories))
all_ingredients += ["Unknown"] * (max_length - len(all_ingredients))
all_allergens += ["Unknown"] * (max_length - len(all_allergens))

# create dataframe
products_df = pd.DataFrame({
    'Product': all_products,
    'Price': all_prices,
    'Serving Size': all_serving_size,
    'Calories': all_calories,
    'Ingredients': all_ingredients,
    'Allergens': all_allergens
})

# split price column into ounces and put it next to price
products_df[['Price', 'Ounces']] = products_df['Price'].str.split('/', expand=True)
products_df['Price'] = products_df['Price'].str.strip().apply(lambda x: x if x.startswith('$') else f"${x}")

cols = list(products_df.columns)
cols.insert(2, cols.pop(cols.index('Ounces')))
products_df = products_df[cols]

# capitalize beginning of every word in ingredients and allergens
products_df['Ingredients'] = products_df['Ingredients'].apply(
    lambda x: ' '.join(word.capitalize() for word in re.findall(r'[\w\']+|[(){}\[\],]', x)) if x != 'Unknown' else 'Unknown'
)
products_df['Allergens'] = products_df['Allergens'].apply(
    lambda x: ' '.join(word.capitalize() for word in re.findall(r'[\w\']+|[(){}\[\],]', x)) if x != 'Unknown' else 'Unknown'
)

# format calories 
products_df['Calories'] = products_df['Calories'].apply(lambda x: re.search(r'CALORIES PER SERVING (\d+)', x).group(1) if re.search(r'CALORIES PER SERVING (\d+)', x) else 'Unknown')

products_df.to_csv("trader_joes_scraped_products.csv", index=False)

print("Scraping completed.")
