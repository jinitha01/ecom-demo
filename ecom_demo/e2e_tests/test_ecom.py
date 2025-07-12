
import os
import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from products.models import Product
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from django.test import Client

class EcommerceE2ETest(StaticLiveServerTestCase):
    """
    End-to-end tests for basic functionality.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        cls.selenium = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        cls.selenium.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        self.product1 = Product.objects.create(
            name="Test Laptop",
            description="Powerful laptop",
            price=999.99,
            image_url="https://example.com/laptop.jpg"
        )
        self.product2 = Product.objects.create(
            name="Test Mouse",
            description="Wireless mouse",
            price=19.99,
            image_url="https://example.com/mouse.jpg"
        )
        
        client = Client()
        session = client.session
        session['cart'] = {}
        session.save()
        
        self.selenium.get(self.live_server_url)
        self.wait_for_page_load()

    def wait_for_page_load(self, timeout=10):
        """Wait for the page to fully load"""
        WebDriverWait(self.selenium, timeout).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
        )

    def debug_page(self, test_name):
        """Save debug information """
        debug_dir = os.path.join(os.getcwd(), "test_debug")
        os.makedirs(debug_dir, exist_ok=True)
        

        screenshot_path = os.path.join(debug_dir, f"{test_name}.png")
        self.selenium.save_screenshot(screenshot_path)
    
        page_source_path = os.path.join(debug_dir, f"{test_name}.html")
        with open(page_source_path, "w", encoding="utf-8") as f:
            f.write(self.selenium.page_source)
        
    def test_product_listing(self):
        """Verify products are displayed on the product listing page"""
        try:
            WebDriverWait(self.selenium, 10).until(
                lambda driver: any(
                    product.name in driver.page_source 
                    for product in [self.product1, self.product2]
                )
            )
            
            page_content = self.selenium.page_source
            self.assertIn(self.product1.name, page_content)
            self.assertIn(self.product2.name, page_content)
        except Exception as e:
            self.debug_page("test_product_listing_failed")
            raise

    def test_add_to_cart_from_product_list(self):
        """Test adding a product to cart from the product list page"""
        try:
            self.selenium.get(self.live_server_url + reverse('product_list'))
            
            WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".add-to-cart-button"))
            )
            
            add_buttons = self.selenium.find_elements(By.CSS_SELECTOR, ".add-to-cart-button")
            self.assertGreater(len(add_buttons), 0, "No add to cart buttons found")
            
            product_name = self.selenium.find_element(By.CSS_SELECTOR, ".text-xl.font-semibold").text
            add_buttons[0].click()
            
            try:
                WebDriverWait(self.selenium, 10).until(
                    lambda driver: "cart" in driver.current_url.lower() or 
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".cart-item, [class*='cart'], [id*='cart']"))
                )
            except:
                WebDriverWait(self.selenium, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success, .message-success"))
                )
            page_text = self.selenium.find_element(By.TAG_NAME, "body").text
            self.assertIn(product_name, page_text)
            
        except Exception as e:
            self.debug_page("test_add_to_cart_from_product_list_failed")
            raise

    def test_add_to_cart_from_product_detail(self):
        """Test adding a product to cart from the product detail page"""
        try:
            self.selenium.get(self.live_server_url + reverse('product_list'))
            product_link = WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".text-xl.font-semibold a"))
            )
            product_name = product_link.text
            product_link.click()
            
            WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))
            )
            
            add_button = self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']")
            self.assertIn("Add to Cart", add_button.text)
            add_button.click()

            try:
                WebDriverWait(self.selenium, 10).until(
                    lambda driver: "cart" in driver.current_url.lower() or 
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".cart-item, [class*='cart'], [id*='cart']"))
                )
            except:
                WebDriverWait(self.selenium, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success, .message-success"))
                )

            page_text = self.selenium.find_element(By.TAG_NAME, "body").text
            self.assertIn(product_name, page_text)
            
        except Exception as e:
            self.debug_page("test_add_to_cart_from_product_detail_failed")
            raise


    def test_quantity_adjustment(self):
        """Test the quantity increment and decrement """
        try:
            add_url = f"{self.live_server_url}{reverse('add_to_cart', args=[self.product1.pk])}"
            self.selenium.get(add_url)
            self.wait_for_page_load()

            try:
                WebDriverWait(self.selenium, 10).until(
                    lambda d: "cart" in d.current_url.lower() or 
                    "added" in d.page_source.lower()
                )
            except TimeoutException:
                self.debug_page("test_failed_at_add_to_cart")
                raise Exception("Failed to add product to cart - no redirect or confirmation")

            cart_url = f"{self.live_server_url}{reverse('view_cart')}"
            self.selenium.get(cart_url)
            self.wait_for_page_load()
            self.debug_page("test_cart_page_loaded")

            try:
                product_row = WebDriverWait(self.selenium, 15).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, f"//tr[contains(., '{self.product1.name}')]")
                    )
                )
            except TimeoutException:
                page_text = self.selenium.find_element(By.TAG_NAME, "body").text
                print(f"Current page content:\n{page_text}")
                self.debug_page("test_product_not_in_cart")
                raise Exception(f"Product '{self.product1.name}' not found in cart")

            quantity_display = WebDriverWait(product_row, 15).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "span.quantity-display")
                )
            )

            increase_btn = WebDriverWait(product_row, 15).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button.increase-quantity-btn")
                )
            )

            decrease_btn = WebDriverWait(product_row, 15).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button.decrease-quantity-btn")
                )
            )

            initial_quantity = int(quantity_display.text)
            self.assertGreater(initial_quantity, 0, "Initial quantity should be > 0")
            increase_btn.click()
            WebDriverWait(self.selenium, 15).until(
                lambda d: int(quantity_display.text) == initial_quantity + 1
            )
            new_quantity = int(quantity_display.text)
            self.assertEqual(new_quantity, initial_quantity + 1)

            decrease_btn.click()

            WebDriverWait(self.selenium, 15).until(
                lambda d: int(quantity_display.text) == new_quantity - 1
            )
            final_quantity = int(quantity_display.text)
            self.assertEqual(final_quantity, new_quantity - 1)
        except Exception as e:
            self.debug_page("test_quantity_adjustment_failed")
            print(f"Test failed: {str(e)}")
            raise

    def test_remove_from_cart(self):
        """Test removing a product from the cart"""
        try:
            self.selenium.get(f"{self.live_server_url}{reverse('add_to_cart', args=[self.product1.pk])}")
            self.wait_for_page_load()
            
            remove_btn = WebDriverWait(self.selenium, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, ".remove-item, [class*='remove'], [class*='delete'], button.danger, a.remove")
                )
            )
            
            remove_btn.click()
            self.wait_for_page_load()
            
            try:
                empty_msg = WebDriverWait(self.selenium, 5).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".empty-cart, [class*='empty'], [class*='message']")
                    )
                )
                self.assertTrue(empty_msg.is_displayed())
            except TimeoutException:
                page_text = self.selenium.find_element(By.TAG_NAME, "body").text
                self.assertNotIn(self.product1.name, page_text)
        except Exception as e:
            self.debug_page("test_remove_from_cart_failed")
            raise