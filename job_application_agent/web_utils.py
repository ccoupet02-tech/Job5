import random
import time
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from loguru import logger


def get_random_delay(min_seconds: float = 2.0, max_seconds: float = 5.0) -> float:
    """
    Génère un délai aléatoire pour simuler un comportement humain
    
    Args:
        min_seconds: Délai minimum en secondes
        max_seconds: Délai maximum en secondes
        
    Returns:
        Délai aléatoire en secondes
    """
    delay = random.uniform(min_seconds, max_seconds)
    return delay


def sleep_random(min_seconds: float = 2.0, max_seconds: float = 5.0):
    """
    Attend un délai aléatoire
    
    Args:
        min_seconds: Délai minimum en secondes
        max_seconds: Délai maximum en secondes
    """
    delay = get_random_delay(min_seconds, max_seconds)
    logger.debug(f"Sleeping for {delay:.2f} seconds")
    time.sleep(delay)


def get_user_agent() -> str:
    """
    Retourne un User-Agent réaliste
    
    Returns:
        User-Agent string
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15"
    ]
    return random.choice(user_agents)


def setup_selenium_driver(headless: bool = True, user_data_dir: Optional[str] = None) -> webdriver.Chrome:
    """
    Configure et retourne un WebDriver Selenium avec options anti-détection
    
    Args:
        headless: Exécuter en mode headless
        user_data_dir: Répertoire pour sauvegarder le profil Chrome (cookies, sessions)
        
    Returns:
        WebDriver Chrome configuré
    """
    options = Options()
    
    # Mode headless
    if headless:
        options.add_argument("--headless=new")
    
    # Options anti-détection
    options.add_argument(f"user-agent={get_user_agent()}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # Options de performance et stabilité
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    
    # Désactiver les notifications et popups
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    
    # Profil utilisateur pour persistance des cookies
    if user_data_dir:
        options.add_argument(f"--user-data-dir={user_data_dir}")
    
    # Préférences
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    
    try:
        # Installer et configurer le driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Script pour masquer l'automation
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logger.info("Selenium WebDriver initialized successfully")
        return driver
        
    except Exception as e:
        logger.error(f"Error setting up Selenium WebDriver: {e}")
        raise


def scroll_page(driver: webdriver.Chrome, scroll_pause_time: float = 1.0):
    """
    Scroll progressif de la page pour charger le contenu dynamique
    
    Args:
        driver: WebDriver Selenium
        scroll_pause_time: Temps de pause entre chaque scroll
    """
    # Obtenir la hauteur de la page
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Scroll vers le bas
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Attendre le chargement
        time.sleep(scroll_pause_time)
        
        # Calculer la nouvelle hauteur
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        # Sortir si on a atteint le bas
        if new_height == last_height:
            break
            
        last_height = new_height
    
    # Scroll vers le haut
    driver.execute_script("window.scrollTo(0, 0);")
    logger.debug("Page scrolled completely")


def safe_find_element(driver: webdriver.Chrome, by, value, timeout: int = 10):
    """
    Trouve un élément avec gestion d'erreur
    
    Args:
        driver: WebDriver Selenium
        by: Type de sélecteur (By.ID, By.XPATH, etc.)
        value: Valeur du sélecteur
        timeout: Timeout en secondes
        
    Returns:
        Element trouvé ou None
    """
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except (TimeoutException, NoSuchElementException) as e:
        logger.warning(f"Element not found: {by}={value}")
        return None


def safe_click(driver: webdriver.Chrome, element):
    """
    Clique sur un élément avec gestion d'erreur
    
    Args:
        driver: WebDriver Selenium
        element: Element à cliquer
        
    Returns:
        True si succès, False sinon
    """
    from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException
    
    try:
        # Scroll vers l'élément
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        sleep_random(0.5, 1.0)
        
        # Cliquer
        element.click()
        return True
        
    except (ElementClickInterceptedException, ElementNotInteractableException) as e:
        logger.warning(f"Could not click element: {e}")
        
        # Essayer avec JavaScript
        try:
            driver.execute_script("arguments[0].click();", element)
            return True
        except Exception as e2:
            logger.error(f"JavaScript click also failed: {e2}")
            return False
