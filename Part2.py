import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService, Service
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


# "edge",
@pytest.fixture(params=["edge", "chrome", "firefox"], scope="class")
def driver(request):
    browser = request.param
    if browser == "edge":
        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service)
    elif browser == "chrome":
        s = Service('drivers/chromedriver.exe')
        driver = webdriver.Chrome(service=s)
    elif browser == "firefox":
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service)

    request.cls.driver = driver
    yield driver
    driver.quit()


@pytest.mark.usefixtures("driver")
class TestFlaskApp:
    # Done
    @pytest.mark.smoke
    def test_click_homepage(self, driver):
        driver.get('http://127.0.0.1:5000/')
        try:
            list_of_links = driver.find_elements(By.TAG_NAME, 'a')
            homepage_link = next(
                link for link in list_of_links if 'Homepage' in link.text)
            homepage_link.click()
            WebDriverWait(driver, 10).until(EC.title_contains('Homepage'))
        except Exception as e:
            pytest.fail(f"Failed to click Homepage link: {e}")

    # Done
    @pytest.mark.functional
    def test_click_new_movie(self, driver):
        driver.get('http://127.0.0.1:5000/')
        try:
            list_of_links = driver.find_elements(By.TAG_NAME, 'a')
            new_movie_link = next(
                link for link in list_of_links if 'New' in link.text)
            new_movie_link.click()
            WebDriverWait(driver, 10).until(EC.title_contains('New Movie'))
        except Exception as e:
            pytest.fail(f"Failed to click New Movie link: {e}")

    @pytest.mark.regression
    def test_add_new_movie(self, driver):
        driver.get('http://127.0.0.1:5000/')
        try:
            list_of_links = driver.find_elements(By.TAG_NAME, 'a')
            new_movie_link = next(
                link for link in list_of_links if 'New' in link.text)
            new_movie_link.click()

            values_to_insert = {
                'Title:': 'King Mory',
                'Director:': 'Hot Director',
                # 'Year of Release:': '2023',
                'Actor 1:': 'Silvester',
                'Actor 2:': 'Sharon Stone',
                'Actor 3:': 'Pamela Anderson',
                'Actor 4:': 'Mr Bean'
            }

            text_boxes = driver.find_elements(By.XPATH, "//input[@type='text']")

            for text_box in text_boxes:
                k = text_box.accessible_name
                text_box.send_keys(values_to_insert[k])

            # Find all <button> elements
            buttons = driver.find_elements(By.TAG_NAME, "button")
            if len(buttons) == 1:
                buttons[0].click()

        except Exception as e:
            pytest.fail(f"Failed to add new movie: {e}")

# if __name__ == '__main__':
#     # click_homepage_test()
#     # click_new_movie_test()
#     add_new_movie()
