import time
import pickle
from selenium import webdriver
from selenium.common.exceptions import (ElementClickInterceptedException,
										NoSuchElementException,
										StaleElementReferenceException)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def start_driver():
	useOpera = False
	if useOpera:
		# Uses opera installation
		options = webdriver.ChromeOptions()
		options.add_argument("--start-maximized")
		options.add_experimental_option('w3c', False)
		driver = webdriver.Opera(executable_path=r'C:\\operadriver.exe',options=options)
	else:
		# Uses a Chrome node connected to this selenium grid
		selenium_grid_url = "192.168.178.98:4444"
		capabilities = DesiredCapabilities.CHROME.copy()
		driver = webdriver.Remote(desired_capabilities=capabilities,command_executor=selenium_grid_url)
	action = ActionChains(driver)
	return driver, action

def check_exists_by_xpath(xpath):
	try:
		driver.find_element_by_xpath(xpath)
	except NoSuchElementException:
		return False
	return True

def click_if_exists_by_xpath(xpath):
	if check_exists_by_xpath(xpath) == True:
 		driver.find_element_by_xpath(xpath).click()

# Accepts Cookies
def accept_cookies():
	click_if_exists_by_xpath('/html/body/div[3]/div[3]/div/div/div[2]/div/button[2]')

# Close the welcome popup
def close_welcome_popup():
	click_if_exists_by_xpath('/html/body/modal-container/div/div/sb-landing-page-modal/div[1]/button')

# Logging in with the loaded Steam Cookies
def login():
	# Clicking on the Steam Redirect
	driver.get('https://skinbaron.com/steam-login')
	time.sleep(1)
	# Clicking on the Sign In button in Steam and redirecting to Skinbaron
	driver.find_element_by_xpath('//*[@id="imageLogin"]').click()
	time.sleep(2)
	# Waiting until returning logged in to skinbaron
	if check_exists_by_xpath('/html/body/sb-root/div/sb-layout-header/sb-layout-header-default/div/header/nav/ul/li[1]/sb-profile-widget/a/span/span[2]/strong') == False:
		print('Requires manual login by user')
		while True:
			if check_exists_by_xpath('/html/body/sb-root/div/sb-layout-header/sb-layout-header-default/div/header/nav/ul/li[1]/sb-profile-widget/a/span/span[2]/strong') == True:
				time.sleep(0.5)
				break
			time.sleep(0.1)

def get_price(price):
	price = price.text
	price = price.split('\n')
	price.reverse()
	price = price[0]
	price = price.replace(' €','').replace(',','.')
	price = float(price)
	return price

# def get_stock(item):
# 	stock = item.find_element_by_xpath('.//div[2]/div[4]/div[3]/p').text
# 	stock = stock[:-10]
# 	stock = int(stock)
# 	return stock

def get_simple_items():
	return_items = []
	items = driver.find_elements_by_xpath('//*[@id="offer-container"]/ul/li/sb-stackable-offer') + driver.find_elements_by_xpath('//*[@id="offer-container"]/ul/li/sb-single-offer')
	for item in items:
		return_item = []
		return_item.append(item.find_element_by_xpath('.//div[2]/div[2]/div[1]').text)

		return_item.append(1)#get_stock(item))

		prices = item.find_elements_by_xpath('.//div/div[2]/div[4]/div[1]/div') +item.find_elements_by_xpath('.//div[2]/div[2]/div[6]')
		return_item.append(get_price(prices[0]))
		prices.reverse()
		return_item.append(get_price(prices[0]))

		cart_buttons = item.find_elements_by_xpath('.//div[2]/div[7]/sb-buy-button/div/div/button')
		return_item.append(cart_buttons[0])
		cart_buttons.reverse()
		return_item.append(cart_buttons[0])
		if return_item[4] == return_item[5]:
			return_item[5] = None
			return_item[3] = None

		return_items.append(return_item)
	return return_items

def get_advanced_items():
	return_items = []
	items = driver.find_elements_by_xpath('//*/li/sb-single-offer/div/div[2]')

	for item in items:
		return_item = []
		name = item.find_element_by_xpath('.//div[2]/div[1]').text
		return_item.append(name)

		price = item.find_element_by_xpath('.//div[6]')
		return_item.append(get_price(price))

		cart_button = item.find_element_by_xpath('.//div[7]/sb-buy-button/div/div/button')
		return_item.append(cart_button)

		wear = item.find_element_by_xpath('.//div[8]/p[2]').text
		wear = float(wear.replace('WEAR ','').replace('%',''))
		return_item.append(wear)

		return_items.append(return_item)
	return return_items

# Getting all items
def get_all_items():
	return_items = []
	# This while loop is going through all pages of items
	x = 4
	while True:
		return_items.append(get_simple_items())


		if check_exists_by_xpath(f'//*[@id="offer-container"]/div/sb-one-sided-pagination/ul/li[{x}]/button') == True:
			try:
				driver.find_element_by_xpath(f'//*[@id="offer-container"]/div/sb-one-sided-pagination/ul/li[{x}]/button').click()
			except StaleElementReferenceException:
				break
			except ElementClickInterceptedException:
				break
			time.sleep(1)
		else:
			break
		if x != 11:
			x += 1

	return return_items

# Starting the chromedriver
print('Starting driver...')
driver, action = start_driver()
print('Started driver')

# Loads the website
print('Loading Skinbaron...')
driver.get("https://skinbaron.de/")
time.sleep(3)

print('Closing popups...')
close_welcome_popup()
time.sleep(3)
accept_cookies()

print('Logging in...')
try:
	cookies = pickle.load(open("cookies.pkl", "rb"))
	for cookie in cookies:
		driver.add_cookie(cookie)
except Exception:
	login()

driver.get("https://skinbaron.de/")
time.sleep(2)
pickle.dump( driver.get_cookies() , open("cookies.pkl","wb"))
print('Logged in')

def clear_cart():
	driver.get('https://skinbaron.de')
	time.sleep(4)
	click_if_exists_by_xpath('/html/body/sb-root/div/sb-layout-header/sb-layout-header-default/div/header/nav/ul/li[3]/sb-shopping-cart-widget/div/div/div[1]')
	try:
		while True:
			rm_button = driver.find_element_by_xpath('/html/body/sb-root/div/sb-layout-header/sb-layout-header-default/div/header/nav/ul/li[3]/sb-shopping-cart-widget/div/div/div[2]/div/div[2]/div/div/sb-cart-step-review/div/div/div[1]/div[1]/div[3]').click()
			time.sleep(0.2)
	except Exception:
		total = 0
		return total

def checkout_cart(excepted_total):
	excepted_total = round(excepted_total,2)
	driver.find_element_by_xpath('/html/body/sb-root/div/sb-layout-header/sb-layout-header-default/div/header/nav/ul/li[3]/sb-shopping-cart-widget/div/div/div[1]').click()
	time.sleep(0.5)

	try:
		cart_total = driver.find_element_by_xpath('/html/body/sb-root/div/sb-layout-header/sb-layout-header-default/div/header/nav/ul/li[3]/sb-shopping-cart-widget/div/div/div[2]/div/div[2]/div/div/sb-cart-step-review/div/div/div[3]/div/div[1]/div[2]').text
		cart_total = float(cart_total.replace(' €','').replace(',','.'))
		if cart_total != excepted_total:
			print('Total of checkout is not matching')
			print('Saved total: ',excepted_total,'€')
			print('Real total: ',cart_total,'€')
			return clear_cart()

		driver.find_element_by_xpath('//*[@id="cart-container"]/div[2]/div/div/sb-cart-step-review/div/div/div[3]/div/div[2]/button[2]').click()
		time.sleep(1)
		# Choose balance as payment method
		driver.find_element_by_xpath('//*[@id="cart-container"]/div[2]/div[2]/sb-cart-step-payment-method/div[1]/div[2]/ul/li[1]').click()
		time.sleep(1)
		# Accept the Widerrufsrecht checkbox
		driver.find_element_by_xpath('//*[@id="cart-container"]/div[2]/div[2]/sb-cart-step-payment-method/div[1]/div[2]/label').click()
		time.sleep(1)
		# Clicking Pay Now
		driver.find_element_by_xpath('//*[@id="cart-container"]/div[2]/div[2]/sb-cart-step-payment-method/div[2]/div/div[2]/div/button[2]').click()
		time.sleep(1)
		# Clicking Store in Inventory
		driver.find_element_by_xpath('/html/body/modal-container/div/div/sb-select-buy-location-modal/div[3]/div/button').click()
		time.sleep(2)
		print('Checked out successfully')
		return 0
	except Exception as e:
		
		print('Failed to check out')
		print(e)
		return clear_cart()

def calculate_f(p):
	f = -0.083*pow(p,3) + 2.75*pow(p,2) - 30.667*p + 118
	return f

def add_item_to_cart(cart_button, name, price, total):
	try:
		action.move_to_element_with_offset(cart_button, 0, 0)
		action.perform()
		action.reset_actions()
		time.sleep(0.2)
		cart_button.click()
		click_if_exists_by_xpath('/html/body/div[5]/div/div') # Click on the notification to remove it
		print('Added ',name,' to cart')
		total += price
	except Exception as e:
		print(e)
		print('Failed to add ',name,' to cart')
	return total


searches = [
	# Accessories:
	# ['simple', 'https://skinbaron.de/de/csgo/Accessory/Sticker?sort=CF', 0.02], # Stickers
	['simple', 'https://skinbaron.de/de/csgo/Accessory/Music-Kit?sort=BP', 1.50], # Music kits
	# ['simple', 'https://skinbaron.de/?appId=730&v=2829&v=2904&sort=CF&language=de', 2.50], # Collectible
	# ['simple', 'https://skinbaron.de/?appId=730&v=2829&v=3076&sort=BP&language=de', 1.00], # Nametag
	# ['simple', 'https://skinbaron.de/?appId=730&v=2829&v=3084&sort=CF&language=de', 1.50], # Present
	['simple', 'https://skinbaron.de/de/csgo/Accessory?v=3355&sort=BP', 0.40], # Tool
	# Agents:
	['simple', 'https://skinbaron.de/de/csgo/Agents?sort=CF', 0.35], # All Agents
	# ['simple', 'https://skinbaron.de/?appId=730&v=3341&v=3350&sort=CF&language=de', 0.17], # Superior Agents
	# ['simple', 'https://skinbaron.de/?appId=730&v=3341&v=3351&sort=CF&language=de', 0.70], # Master Agents
	# ['simple', 'https://skinbaron.de/?appId=730&v=3341&v=3352&sort=CF&language=de', 0.15], # Distinguished Agents
	# ['simple', 'https://skinbaron.de/?appId=730&v=3341&v=3353&sort=CF&language=de', 0.20], # Exceptional Agents
	# Weapons:
	# ['advanced', 'https://skinbaron.de/?appId=730&pub=0.13&sort=BE&qf=4&language=de', 0.46, 20] # Industrial grade
]
# [['simple', link, max_price]]
# [['advanced', link, factor, pages_to_search_through]

def buy_simple_search(search):
	checkout = False
	total = 0
	link = search[1]
	max_price = search[2]
	if max_price != None:
		link = link + '&pub=' + f'{max_price}'
	driver.get(link)
	time.sleep(3)
	items = get_simple_items()
	for item in items:
		name = item[0]
		# stock = item[1]
		price1 = item[2]
		price2 = item[3]
		cart_button1 = item[4]
		cart_button2 = item[5]

		if price1 <= max_price:
			total = add_item_to_cart(cart_button1, name, price1, total)
			checkout = True
		elif (price2 != None and price2 <= max_price):
			total = add_item_to_cart(cart_button2, name, price2, total)
			checkout = True
	if checkout == True:
		total = checkout_cart(total)
	return checkout

def buy_advanced_item(search):
	checkout = False
	total = 0
	basic_link = search[1]
	factor = search[2]
	pages = search[3]
	for page in range(pages):
		link = f'{basic_link}&page={page}'
		driver.get(link)
		time.sleep(2)
		items = get_advanced_items()
		for item in items:
			name = item[0]
			price = item[1]
			cart_button = item[2]
			wear = item[3]

			max_float = calculate_f(price*100)
			if wear <= (max_float*factor):
				total = add_item_to_cart(cart_button, name, price, total)
				# buy_item(cart_button, name, price)
				checkout = True
		if checkout == True:
			total = checkout_cart(total)
	return checkout

def main(buy_loop = False):
	clear_cart()
	for search in searches:
		search_type = search[0]
		if search_type == 'simple':
			while True:
				if buy_simple_search(search) == False:
					break
				driver.get('https://www.myexternalip.com/raw')
				time.sleep(3)

		elif search_type == 'advanced':
			while True:
				if buy_advanced_item(search) == False:
					break
				driver.get('https://www.myexternalip.com/raw')
				time.sleep(3)
	driver.get('https://www.myexternalip.com/raw')


x = 0
while True:
	# try:
	print(f'{x}: Searching for offers...')
	main()
	x += 1
	# except Exception as e:
		# print(' -ERROR- ')
		# print(e)