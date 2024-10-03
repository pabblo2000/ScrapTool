# %% [markdown]
# # Librerias

# %%
import sys
import subprocess
import importlib.util
import io
try:
    to_search = sys.argv[1]
    products_to_visit = int(sys.argv[2])
    max_comment_pages_to_visit = int(sys.argv[3])
    max_images_to_download = int(sys.argv[4])
    show_search_engine = sys.argv[5] == "False"
    image_download = sys.argv[6] == "True"
    See_window = sys.argv[7] == "True"
    close_after_finish = sys.argv[8] == "True"
except:
    to_search = "ordenadores"
    # to_search = input("Que producto quieres buscar? ")
    products_to_visit = 2
    max_comment_pages_to_visit = 2
    max_images_to_download = 3
    show_search_engine = False
    See_window = True
    image_download = True
    close_after_finish = False

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# %%
import pandas as pd
import os
import time
import json
import shutil
import random
import requests
import subprocess
import zipfile
import re
from tkinter import Tk, messagebox
from selenium_stealth import stealth
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException

# %% [markdown]
# # Configuracion de Navegador

# %%
def get_chrome_version():
    
    # Detecta la versión de Google Chrome instalada en el sistema.
    try:
        output = subprocess.check_output(
            r'wmic datafile where name="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" get Version /value',
            shell=True
        )
        version = output.decode('utf-8').strip().split('=')[1]
        return version
    except Exception as e:
        print(f"Error obteniendo la versión de Chrome: {e}")
        return None

def get_chromedriver_download_url(version):
    
    # Obtiene la URL de descarga del ChromeDriver desde la web oficial de Chrome for Testing.
    
    major_version = version.split('.')[0]
    url = f"https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
    response = requests.get(url)
    data = response.json()

    for entry in data['versions']:
        if entry['version'].startswith(major_version):
            for download in entry['downloads']['chromedriver']:
                if download['platform'] == 'win64':  # Cambiado a win64
                    return download['url']
    
    print(f"No se encontró un ChromeDriver para la versión {major_version}")
    return None

def download_and_extract_chromedriver(download_url, extract_path):
    
    # Descarga y extrae el archivo ChromeDriver en la carpeta específica.
    
    response = requests.get(download_url)
    zip_path = os.path.join(extract_path, "chromedriver.zip")

    with open(zip_path, 'wb') as file:
        file.write(response.content)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    os.remove(zip_path)
    print(f"ChromeDriver descargado y extraído en: {extract_path}")

def get_installed_chromedriver_version(chromedriver_path):
    
    # Verifica la versión de ChromeDriver instalada en la ruta especificada.
    
    if os.path.exists(chromedriver_path):
        try:
            output = subprocess.check_output([chromedriver_path, "--version"], shell=True)
            version = output.decode('utf-8').strip().split(' ')[1]
            return version
        except Exception as e:
            print(f"Error obteniendo la versión de ChromeDriver: {e}")
            return None
    return None

# %%
# Obtener el directorio raíz del proyecto
ScrapTool_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Continuar con las rutas relativas
Chrome_dir = os.path.join(ScrapTool_dir, "Config", "Chrome")
ChromeVersions_dir = os.path.join(Chrome_dir, "Versions")

chrome_version = get_chrome_version()

if chrome_version:
    print(f"Versión de Chrome detectada: {chrome_version}")   

    # Crear la carpeta de versiones si no existe
    if not os.path.exists(ChromeVersions_dir):
        os.makedirs(ChromeVersions_dir, exist_ok=True)

    # Crear una carpeta con el nombre de la versión de Chrome dentro de ScrapTools\Config\Chrome\Versions
    version_folder = os.path.join(ChromeVersions_dir, chrome_version)

    if os.path.exists(version_folder):
        print(f"ChromeDriver ya está instalado en {version_folder} y es compatible, continuando con el programa.")
    else:
        os.makedirs(version_folder, exist_ok=True)
        download_url = get_chromedriver_download_url(chrome_version)
        
        if download_url:
            download_and_extract_chromedriver(download_url, version_folder)
        else:
            print("No se pudo obtener la URL de descarga de ChromeDriver.")
else:
    print("No se pudo obtener la versión de Chrome.")


# %%
# Especificar la ruta base para los perfiles de usuario dentro de ScrapTools
TempProfile_dir = os.path.join(Chrome_dir, "TempProfiles")

# Verificar si la ruta base existe
if not os.path.exists(TempProfile_dir):
    print(f"La ruta base {TempProfile_dir} no existe o no es válida.")
    # Crear la ruta base en la carpeta ScrapTools\Config\Chrome\TempProfiles
    os.makedirs(TempProfile_dir, exist_ok=True)
    print(f"Se ha creado la carpeta Temp_profile en: {TempProfile_dir}")

# Crear un nuevo directorio para el perfil de usuario temporal
user_data_dir = os.path.join(TempProfile_dir, "temp_profile")
try:
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
    print(f"Directorio de perfil de usuario creado en: {user_data_dir}")
except Exception as e:
    print(f"Error al crear el directorio del perfil de usuario: {str(e)}")

# Creamos la carpeta de descargas
Download_dir = os.path.join(ScrapTool_dir, "Downloads", to_search)
if not os.path.exists(Download_dir):
    os.makedirs(Download_dir, exist_ok=True)

# %%
# Opciones del navegador Chrome
options = webdriver.ChromeOptions()
options.add_argument(f"--user-data-dir={user_data_dir}")
options.add_argument("--no-first-run")
options.add_argument("--no-default-browser-check")
options.add_argument("--disable-default-apps")
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-extensions")
options.add_argument("--disable-infobars")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--remote-debugging-port=9222")
options.add_argument("--incognito")
options.add_argument("--disable-blink-features=AutomationControlled")

# Si se desea ver la ventana de Chrome durante la ejecución
if See_window == False:
    options.add_argument("--headless")

# Cambiar el User-Agent
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# Desactivar la automatización de Chrome para evitar detecciones de Selenium
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# Establecer el servicio de Chrome
Chromedriver_path = os.path.join(version_folder, 'chromedriver-win64', 'chromedriver.exe')
service = Service(Chromedriver_path)

# Inicializar el WebDriver de Chrome con las opciones y el servicio configurado, para crear el perfil de usuario temporal
driver = webdriver.Chrome(service=service, options=options)

# Pausa para mostrar que necesitas quitar elegir el navegador predeterminado
if show_search_engine and See_window == True:
    # Mostrar un messagebox en lugar de input
    messagebox.showinfo("Pausa", "Presiona Aceptar para continuar...")

driver.quit()

# %%
# Ruta al archivo de preferencias del perfil temporal
preferences_path = os.path.join(user_data_dir, 'Default', 'Preferences')

# Cargar el archivo de preferencias
try:
    with open(preferences_path, 'r', encoding='utf-8') as file:
        prefs = json.load(file)
except FileNotFoundError:
    driver = webdriver.Chrome(service=service, options=options)
    driver.quit()
    with open(preferences_path, 'r', encoding='utf-8') as file:
        prefs = json.load(file)


# HAY QUE MODIFICAR EL ARCHIVO DE PREFERENCIAS PARA CAMBIAR EL MOTOR DE BÚSQUEDA POR DEFECTO A GOOGLE 
# YA QUE POR UNA NUEVA LEY TE PIDE QUE ELIGAS UNA POR DEFECTO

# Modificar las preferencias para establecer el motor de búsqueda predeterminado
prefs['default_search_provider_data'] = {
    "template_url_data": {
        "short_name": "Google",
        "keyword": "google.com",
        "favicon_url": "https://www.google.com/favicon.ico",
        "url": "https://www.google.com/search?q={searchTerms}",
        "is_default": True,
        'credentials_enable_service': False,
        'profile.password_manager_enabled': False,
    }
}

# Guardar las preferencias modificadas
with open(preferences_path, 'w', encoding='utf-8') as file:
    json.dump(prefs, file, ensure_ascii=False, indent=4)

# Inicializar el WebDriver de Chrome con las opciones y el servicio configurado, para cargar el perfil de usuario temporal
driver = webdriver.Chrome(service=service, options=options)
time.sleep(random.uniform(1, 3))

# Poner el navegador en modo Stealth
stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

# %% [markdown]
# # Movimiento por el Navegador

# %%
# Funcion para obtener el HTML de la página actual
def get_html(feedback=False, html_print=False):  
    global soup  
    try:
        # Pausamos para permitir que la página cargue
        time.sleep(1)
        # Obtener la fuente HTML de la página
        html = driver.page_source
        # Analizar el HTML con BeautifulSoup
        soup = bs(html, 'html.parser')
        if feedback:
            print("HTML obtenido\n------------\n")
        if html_print:  
            print(soup.prettify())
        
    except Exception as e:
        print(f"Error al obtener HTML: {e}")
        return None
    
# Función para clicar en un elemento con movimiento aleatorio
def click_with_random_movement(element, steps=10, max_offset=100, feedback=True):
    
    actions = ActionChains(driver)

    # Asegurar que el elemento esté dentro de la vista (scroll si es necesario)
    # driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(0.5)  # Esperar un poco para que el scroll termine

    # Mover el ratón directamente al elemento
    actions.move_to_element(element).perform()
    if feedback:
        print(f"Ratón movido al elemento inicial.")
    time.sleep(0.5)  # Pausa para simular movimiento humano

    # Movimientos aleatorios alrededor del elemento antes de hacer clic
    for i in range(steps):
        offset_x = random.randint(-max_offset, max_offset)
        offset_y = random.randint(-max_offset, max_offset)
        
        try:
            actions.move_by_offset(offset_x, offset_y).perform()
            if feedback:
                print(f"Movimiento {i+1}/{steps}: offset_x={offset_x}, offset_y={offset_y}")
            time.sleep(random.uniform(0.02, 0.1))  # Pausa aleatoria para simular movimiento humano
        except WebDriverException:
            # Si se sale de los límites, imprimir un mensaje simple
            if feedback:
                print(f"Movimiento {i+1}/{steps} fuera de límites. Reposicionando al elemento.")
            actions.move_to_element(element).perform()
            time.sleep(0.5)  # Pausa para asegurar el reposicionamiento

    # Finalmente, hacer clic en el elemento
    actions.move_to_element(element).click().perform()
    if feedback:
        print("Clic realizado con éxito en el elemento.\n")

# %%
url = "https://www.amazon.es"
# url = str(input("Introduce el URL:"))
driver.get(url)

time.sleep(2)

get_html(feedback=True, html_print=False)

# %%
# Botón de rechazar cookies
try:
    reject_cookies = driver.find_element(By.XPATH, '//*[@id="sp-cc-rejectall-link"]')
    # reject_cookies.click()
    click_with_random_movement(reject_cookies)
    cookies_not_found = False
except:
    print("No se encontró el botón de rechazar cookies.")
    cookies_not_found = True

# Temporizador aleatorio para simular un comportamiento humano
time.sleep(random.uniform(0.5, 2))

# Buscar la barra de búsqueda
try:
    search_bar = driver.find_element(By.XPATH, '//*[@id="twotabsearchtextbox"]')
except:
    print("No se encontró la barra de búsqueda, probando alternativa...")
    search_bar = driver.find_element(By.ID, 'nav-bb-search')

# Hacer clic en la barra de búsqueda
click_with_random_movement(search_bar)

# Esperar un poco para simular una pausa antes de escribir
time.sleep(1)



# %%
# Si la variable to_search no está definida, solicitar al usuario que introduzca un producto
try:
    print(to_search)
except:
    to_search = input("Introduce el producto a buscar: ")

# Escribir el término de búsqueda letra por letra
for char in to_search:
    search_bar.send_keys(char)
    print(f"Escribiendo: {char}")
    time.sleep(random.uniform(0.05, 0.5))   # Pausa entre cada letra para simular escritura humana
# Presionar Enter para realizar la búsqueda
search_bar.send_keys(Keys.RETURN)

# Verificacion adicional del rechazo de cookies para evitar errores
if cookies_not_found == True:
    try:
        reject_cookies = driver.find_element(By.XPATH, '//*[@id="sp-cc-rejectall-link"]')
        click_with_random_movement(reject_cookies)
    except NoSuchElementException:
        print("No se encontró el botón de rechazar cookies.")

# %%
product_links = []
product_elements = driver.find_elements(By.XPATH, '//div[@data-component-type="s-search-result"]')

# Itera sobre cada elemento de producto y extrae el enlace
for product in product_elements:
    try:
        # Encuentra el enlace dentro del producto
        link = product.find_element(By.XPATH, './/a[@class="a-link-normal s-no-outline"]').get_attribute('href')
        product_links.append(link)
    except NoSuchElementException:
        continue 

print(f"Se han encontrado {len(product_links)} enlaces de productos.\n")

# Limitamos el número de enlaces a visitar
product_links = product_links[:products_to_visit]
print(f"Se ha reducido la lista a {len(product_links)} enlaces de productos para visitar.\n")

# Mostar los enlaces de los productos
for i, link in enumerate(product_links):
    print(f"Producto {i+1}: {link}")

# %% [markdown]
# # Funciones 

# %%
####################    EXTRACCION DE NUMEROS    ####################

# Inicializar las listas para almacenar los datos extraídos
price = []
currency = []
rating = []
n_reviews = []
n_bought = []

# Función para extraer el número de una etiqueta
def get_product_number(where_to_save, type_search, where_to_search, where_to_search_2=None, feedback=False):
    try:
        # Localizar la parte entera del número o el número completo
        element_number = driver.find_element(type_search, where_to_search)
        number_text = element_number.text.strip()

        # Si se proporciona un selector para la parte fraccionaria, combinar ambas partes
        if where_to_search_2:
            element_fraction = driver.find_element(type_search, where_to_search_2)
            number_text = f"{number_text}.{element_fraction.text.strip()}"
            final_number = float(number_text)
    
        elif where_to_save == n_reviews:
            number_text_cleaned = number_text.split(' ')[0]
            final_number = int(number_text_cleaned)

        else:
            number_text_cleaned = number_text.replace('€', '').replace(',', '.').replace('\n', '').strip()
            final_number = float(number_text_cleaned)
        
        # Guardar el número extraído en la lista
        where_to_save.append(final_number)

        if feedback:
            print(f"Número extraído: {final_number}")
        
    except Exception as e:
        # Manejo de excepciones según la lista donde se guardará
        default_value = "No disponible" if where_to_save == n_bought else 0
        where_to_save.append(default_value)
        if feedback:
            print(f"Error al obtener el número: {e}")


# %%
####################    EXTRACCION DE TEXTO    ####################

# Inicializar las listas para almacenar los datos extraídos
product_id = []
name = []
currency = []
n_bought = []
sent_by = []
sold_by = []
stock = []

def get_product_text(where_to_save, type_search, where_to_search, feedback=False):
    try:       
        element = driver.find_element(type_search, where_to_search)
        element_text = element.get_attribute('value') if where_to_save == product_id else element.text
        if element_text:
            where_to_save.append(element_text)
            if feedback:
                print(f"Texto extraído: {element_text}")
        else:
            where_to_save.append("No disponible")
            if feedback:
                print("Elemento no encontrado: No disponible")
    
    except NoSuchElementException:
            where_to_save.append("No disponible")
            if feedback:
                print("Elemento no encontrado: No disponible")

####################   EXTRACCION DE STOCK   ####################
def get_stock(feedback=False):
    get_html()
    availability_div = soup.find('div', id='availability')
    
    if availability_div:
        availability = availability_div.find('span')
        if availability:
            stock_text = availability.get_text(strip=True)
            if feedback:
                print(f"Disponibilidad: {stock_text}")
            return stock_text
        else:
            return "Stock information not found"
    else:
        return "Stock information not found"

# %%
####################    EXTRACCION DE TABLAS    ####################

def extract_table_data(type_search, table_xpath, feedback=False):

    try:
        # Intentar hacer clic en el botón "Ver más" si existe
        try:
            click_with_random_movement(driver.find_element(By.XPATH, '//*[@id="poToggleButton"]/a'), feedback=False)
        except:
            pass

        # Localizar la tabla usando el XPath proporcionado
        table = driver.find_element(type_search, table_xpath)
        
        # Extraer todas las filas de la tabla
        rows = table.find_elements(By.XPATH, './/tr')
        
        # Inicializar un diccionario para almacenar las características
        data_dict = {}
        
        # Recorrer cada fila y extraer la característica y su valor
        for row in rows:
            feature_name = row.find_element(By.XPATH, './/td[@class="a-span3"]/span').text.strip()
            feature_value = row.find_element(By.XPATH, './/td[@class="a-span9"]/span').text.strip()
            
            # Agregar la característica y su valor al diccionario
            data_dict[feature_name] = feature_value

            if feedback:
                print(f"{feature_name}: {feature_value}")
        
        return data_dict
    
    except Exception as e:
        if feedback:
            print(f"Error al extraer datos de la tabla: {e}")
        return {}

# %%
# Listas para almacenar los datos de los productos
product_index = []
product_id = []
name = []
price = []
currency = []
rating = []
n_bought = []
sent_by = []
sold_by = []
stock = []
n_reviews= []
image_urls = []
categories = []

# Creamos la función para extraer los detalles del producto
def get_product_details(feedback=False):
    try:
        # Obtener el HTML de la página
        time.sleep(1)
        get_html(feedback=False)
        time.sleep(1)
        # ID del producto
        get_product_text(product_id, By.XPATH, '//*[@id="ASIN"]', feedback=False)

        # Nombre del producto
        get_product_text(name, By.XPATH, '//*[@id="productTitle"]', feedback=False)

        # Precio del producto
        get_product_number(price, By.XPATH, '//*[@class="a-price-whole"]', '//*[@class="a-price-fraction"]', feedback=False)

        # Moneda del producto
        get_product_text(currency, By.CLASS_NAME, 'a-price-symbol', feedback=False)

        # Rating del producto
        get_product_number(rating, By.XPATH, '//*[@id="acrPopover"]//span[@class="a-size-base a-color-base"]', feedback=False)

        # Número de compras
        get_product_text(n_bought, By.XPATH, '//*[@id="social-proofing-faceout-title-tk_bought"]/span', feedback=False)

        # Enviado por
        get_product_text(sent_by, By.XPATH, '//div[@class="offer-display-feature-text a-spacing-none "]//span[@class="a-size-small offer-display-feature-text-message"]', feedback=False)

        # Vendido por
        get_product_text(sold_by, By.XPATH, '//div[@class="offer-display-feature-text a-spacing-none "]//span[@class="a-size-small offer-display-feature-text-message"]', feedback=False)

        # Stock
        stock.append(get_stock(feedback=False))
    
        # Numero de reseñas
        get_product_number(n_reviews, By.XPATH, '//*[@id="acrCustomerReviewText"]', feedback=False)
    except Exception as e:
        if feedback:
            print(f"Error al obtener detalles del producto: {e}")

# Creamos la funcion para extraer las categorias del producto
def get_categories(feedback=False):
    try:
        elements_categories = driver.find_elements(By.XPATH, '//ul[@class="a-unordered-list a-horizontal a-size-small"]/li/span/a')
        categories_cleaned = [category.text for category in elements_categories]
        categories.append(categories_cleaned)
        if feedback:
            print(f"Categorías: {categories_cleaned}")
    except NoSuchElementException:
        categories.append("No disponible")
        if feedback:
            print("Categorías no encontradas.")

# %%
def preload_images(wait_time=0.2, feedback=False):
    try:
        # Localiza el contenedor de las miniaturas de imágenes
        alt_images_container = driver.find_element(By.ID, "altImages")

        # Encuentra todos los elementos de las imágenes dentro de ese contenedor
        image_thumbnails = alt_images_container.find_elements(By.CSS_SELECTOR, "li.item.imageThumbnail")

        # Inicializa ActionChains para simular acciones del ratón
        actions = ActionChains(driver)

        # Recorrer cada miniatura y simular el movimiento del ratón sobre ella
        for index, thumbnail in enumerate(image_thumbnails, start=1):
            # Mueve el ratón hacia la miniatura y espera un momento para que la imagen se cargue
            actions.move_to_element(thumbnail).perform()
            time.sleep(wait_time)  # Ajusta el tiempo según sea necesario para dar tiempo a que la imagen se cargue

            if feedback:
                print(f"Imagen {index} precargada.")

        if feedback:
            print("Todas las imágenes han sido procesadas.")
    except Exception as e:
        if feedback:
            print(f"Error al intentar precargar las imágenes: {e}")

# Definir listas globales para almacenar las URLs de las imágenes
image_urls = []
all_images_index = []
all_images_urls = []
all_image_urls_id = []

head_image_url = []  # Esta lista no se limpiará, se irá acumulando la primera imagen de cada ejecución


# Inicializar el contador de enlaces de productos para que no de problemas
counter_links = 0
# Creamos las listas para almacenar las imagenes
product_id_images = []
all_product_images = []
head_image_url = []
# Funcion para extraer las imagenes de los productos
def get_images(download=image_download, max_photos=max_images_to_download, feedback=False):

    # Creamos las carpetas para guardar las imágenes
    if download == True:
        # Crear carpeta de imágenes
        Image_dir = os.path.join(Download_dir, 'Images')
        if not os.path.exists(Image_dir):
            os.makedirs(Image_dir)

        # Crear la carpeta específica para el producto
        product_folder = os.path.join(Image_dir, f'product_{counter_links}')
        if not os.path.exists(product_folder):
            os.makedirs(product_folder)

    # Ejecutar la función preload_images
    preload_images(wait_time=0.2, feedback=False)

    # Buscar todas las imágenes con data-old-hires (alta resolución)
    image_elements = driver.find_elements(By.CSS_SELECTOR, 'img[data-old-hires]')

    # Inicializar listas para almacenar URLs
    product_images_url = []
    
    # Agregamos las URLs de las imágenes a la lista
    for img in image_elements:
        try:
            image_url = img.get_attribute('data-old-hires')
            if image_url:
                product_images_url.append(image_url)
                all_images_index.append(counter_links)
        except Exception as e:
            if feedback:
                print(f"Error al extraer la URL de la imagen: {e}")

    # Guardamos la primera imagen del producto en alta resolución
    head_image_url.append(product_images_url[0])
    
    # Ponemos un maximo de fotos a descargar
    product_images_url = product_images_url[:max_photos]

    # Guardamos las imagenes en all_product_images y asociamos el ID del producto
    all_product_images.append(product_images_url)
    product_id_images.append(product_id[-1])

    # Descargar las imágenes por carpeta de producto si download es True
    if download == True:
        for index, img_url in enumerate(product_images_url):
            try:
                response = requests.get(img_url)
                if response.status_code == 200:
                    image_path = os.path.join(product_folder, f'image_{index + 1}.jpg')
                    with open(image_path, 'wb') as file:
                        file.write(response.content)
                    if feedback:
                        print(f"Imagen {index + 1} descargada: {image_path}")
                else:
                    if feedback:
                        print(f"Error al descargar la imagen {index + 1}: {response.status_code}")
            except Exception as e:
                if feedback:
                    print(f"Error al descargar la imagen {index + 1}: {e}")

    if feedback:
        print(f"Se han encontrado {len(product_images_url)} imágenes.")

    

# %%
five_star_percentages = []
four_star_percentages = []
three_star_percentages = []
two_star_percentages = []
one_star_percentages = []
star_percentages = [five_star_percentages, four_star_percentages, three_star_percentages, two_star_percentages, one_star_percentages]

# Funcion para obtener los porcentajes de estrellas
def get_star_percentages(feedback=False):
    # Encontrar el elemento que contiene el histograma
    histogram = soup.find('ul', {'id': 'histogramTable'})

    # Extraer los porcentajes y asignarlos a las listas correspondientes
    for index, li in enumerate(histogram.find_all('li')):
        # Extraer el porcentaje del texto dentro del div con role="progressbar"
        percentage = li.find('div', {'role': 'progressbar'}).get('aria-valuenow')
        
        # Asignar el porcentaje a la lista correspondiente
        if index == 0:
            five_star_percentages.append(float(percentage))
            if feedback:
                print(f"5 estrellas: {percentage}%")
        elif index == 1:
            four_star_percentages.append(float(percentage))
            if feedback:
                print(f"4 estrellas: {percentage}%")
        elif index == 2:
            three_star_percentages.append(float(percentage))
            if feedback:
                print(f"3 estrellas: {percentage}%")
        elif index == 3:
            two_star_percentages.append(float(percentage))
            if feedback:
                print(f"2 estrellas: {percentage}%")
        elif index == 4:
            one_star_percentages.append(float(percentage))
            if feedback:
                print(f"1 estrella: {percentage}%")
    
    # Retornar las listas con los porcentajes
    return five_star_percentages, four_star_percentages, three_star_percentages, two_star_percentages, one_star_percentages

# %%
# Iniciamos la lista para almacenar las características de los productos
all_product_features = []
# Función para extraer las características de un producto
def get_characteristics(feedback=False):
    try:
        product_features = extract_table_data(By.XPATH, '//tbody', feedback=False)
        product_features["Product_index"] = counter_links
        product_features["Product_ID"] = product_id[-1]  # Agregar el último ID de producto
        if feedback == True:
            print(f"Características extraídas para el producto {counter_links}:\n{product_features}\n")
        # Agregar las características del producto a la lista
        all_product_features.append(product_features)
    except Exception as e:
        if feedback == True:
            print(f"Error al extraer características del producto: {e}")

# %%
reviewproduct_index = []
reviewproduct_code = []
review_ids = []
authors = []
titles = []
dates = []
verified_purchases = []
was_helpful_votes = []
texts = []
review_stars = []

#Ponemos reviews = [] para que no nos de error
reviews = []

def get_reviews(feedback=False):
    global votes
    global review
    for review in reviews:

        # Extraer el ID del comentario
        try:
            review_id = review.get('id', None)
        except:
            pass

        # Verificamos si el comentario ya ha sido extraído
        if review_id not in review_ids:

            # Añadir el índice del producto
            reviewproduct_index.append(counter_links)

            # Asignamos ID de comentario a producto
            try:
                review_ids.append(review_id)
                if feedback:
                    print(f"-----------------\nID de comentario: {review_id}")
            except Exception as e:
                if feedback:
                    print(f"Error al obtener el ID de comentario: {e}")
                review_ids.append("Error")
          
            # Asignar código de producto a comentario
            try:
                reviewproduct_code.append(product_id[-1])
                # if feedback:
                #     print(f"Código de producto: {product_id[-1]}")
            except Exception as e:
                # if feedback:
                #     print(f"Error al obtener el código de producto: {e}")
                reviewproduct_code.append("Error")

            # Extraer el autor
            try:
                author = review.find('span', {'class': 'a-profile-name'}).text.strip()
                authors.append(author)
                # if feedback:
                #     print(f"Autor: {author}")
            except Exception as e:
                if feedback:
                    print(f"Error al obtener el autor: {e}")
                authors.append("Error")

            # Extraer el título de la reseña
            try:
                title_element = review.find('a', {'data-hook': 'review-title'}) or review.find('span', {'data-hook': 'review-title'})
                title = title_element.text.strip()
                if 'de 5 estrellas' in title:
                    title = title.split('\n', 1)[-1].strip()
                titles.append(title)
                if feedback:
                    print(f"Título: {title}")
            except Exception as e:
                if feedback:
                    print(f"Error al obtener el título: {e}")
                titles.append("None")

            # Extraer la fecha de la reseña
            try:
                date_text = review.find('span', {'data-hook': 'review-date'}).text.strip()
                date = date_text.split('el')[-1].strip()
                dates.append(date)
                # if feedback:
                #     print(f"Fecha: {date}")
            except Exception as e:
                if feedback:
                    print(f"Error al obtener la fecha: {e}")
                dates.append("None")

            # Verificar si la compra fue verificada
            try:
                verified = review.find('span', {'data-hook': 'avp-badge'}) is not None
                verified_purchases.append(verified)
                # if feedback:
                #     print(f"Compra verificada: {verified}")
            except Exception as e:
                if feedback:
                    print(f"Error al verificar la compra: {e}")
                verified_purchases.append(False)

            # Extraer el número de votos útiles
            try:
                helpful = review.find('span', {'data-hook': 'helpful-vote-statement'}).text.strip()
                votes = int(helpful.split()[1].replace(',', '')) if helpful.split()[1].isdigit() else 0
                was_helpful_votes.append(votes)
                # if feedback:
                #     print(f"Votos útiles: {votes}")
            except Exception as e:
                # if feedback:
                #     print(f"Votos útiles: {votes}")
                was_helpful_votes.append(0)

            # Extraer las estrellas de la reseña
            try:
                # Primer intento de extracción
                star_element = review.find('i', {'data-hook': 'review-star-rating'})
                
                # Si no se encuentra, intentar con el segundo método
                if not star_element:
                    star_element = review.find('i', {'data-hook': 'cmps-review-star-rating'})
                
                # Si se encuentra el elemento de estrellas
                if star_element:
                    # Extraer el texto de las estrellas
                    stars_text = star_element.text.strip()
                    # Obtener el número de estrellas (ej: "5,0 de 5 estrellas")
                    stars = stars_text.split()[0]
                    try:
                        # Convertimos las estrellas a número entero
                        stars = int(float(stars.replace(',', '.')))
                    except Exception as e:
                        if feedback:
                            print(f"Error al convertir las estrellas a entero: {stars} {e}\n")
                    review_stars.append(stars)
                    # if feedback:
                    #     print(f"Estrellas: {stars}\n")
                else:
                    if feedback:
                        print("No se encontraron estrellas en la reseña.\n")
                    review_stars.append("No stars")
            except Exception as e:
                if feedback:
                    print(f"Error al obtener las estrellas: {e}\n")
                review_stars.append("Error")


            # Extraer el texto de la reseña
            try:
                # Buscar el contenedor principal de la reseña
                review_body = review.find('span', {'data-hook': 'review-body'})
                
                # Inicializar la variable de texto vacío
                text = ""
                
                if review_body:
                    # Intentar extraer el texto del primer span anidado
                    text_element = review_body.find('span')
                    if text_element and text_element.text.strip() and "Video Player is loading." not in text_element.text:
                        text = text_element.text.strip()
                    else:
                        # Si no encuentra texto, buscar en otros elementos hijos del review_body
                        text_elements = review_body.find_all('span', recursive=False)
                        # Filtrar los textos no deseados
                        filtered_texts = [element.text.strip() for element in text_elements if element.text.strip() and "Video Player is loading." not in element.text]
                        text = " ".join(filtered_texts)
                
                texts.append(text)
                if feedback:
                    print(f"Texto de la reseña: {text[:10]}...")
            except Exception as e:
                texts.append("")
                if feedback:
                    print(f"Error al obtener el texto de la reseña: {e}")
            
        else:
            if feedback:
                print("Comentario duplicado, omitiendo...")

# %%
# Definiendo la excepción personalizada
class NoMorePagesException(Exception):
    pass

# Función para hacer clic en la página siguiente
def click_next_page(feedback=False):
    try:
        next_button = driver.find_element(By.XPATH, '//*[@id="cm_cr-pagination_bar"]/ul/li[2]')
        if "a-disabled" in next_button.get_attribute("class"):
            if feedback:
                print("No hay más páginas")
            # Generamos una excepción "NoMorePagesException" para salir del bucle
            raise NoMorePagesException
        else:
            click_with_random_movement(next_button, feedback=False)
            if feedback:
                print("Página siguiente clicada.")
            
    except:
        if feedback:
            print("No se encontró el botón de 'Siguiente página'. Paginación completa.")


# Función para extraer todas las reseñas de un producto
def get_all_reviews(feedback=False, max_pages=max_comment_pages_to_visit):

    global reviews
    get_html(feedback=False, html_print=False)

    # Hacemos click en Ver más opiniones
    try:
        click_with_random_movement(driver.find_element(By.XPATH, '//*[@id="cr-pagination-footer-0"]/a'), feedback=False)
    except:
        if feedback:
            print("No se encontró el botón de 'Ver más opiniones', probando alternativa...")
        try:
            click_with_random_movement(driver.find_element(By.CSS_SELECTOR, 'a[data-hook="see-all-reviews-link-foot"]'), feedback=False)
        except:
            if feedback:
                print("No se encontró el botón de 'Ver todas las opiniones'.ERROR")
            
    for page in range(max_pages):
        
        # Obtener el HTML de la página actual
        time.sleep(random.uniform(1, 2))
        get_html(feedback=False, html_print=False)

        # Actualizar la lista de reseñas para la página actual
        reviews = soup.find_all('div', {'data-hook': 'review'})
        if feedback:
            print(f"Reseñas encontradas: {len(reviews)}")
        
        try:
            get_reviews(feedback=True)
            if feedback:
                print(f"Comentarios totales extraídos: {len(review_ids)}")
        except Exception as e:
            if feedback:
                print(f"ERROR: {e}")
        
        # Pasar a la siguiente página
        try:
            if feedback:
                print(f"----------------Página {page + 1} de {max_pages} completada.----------------\n")
            if page + 1 >= max_pages:
                break

            click_next_page(feedback=False)
        except NoMorePagesException:
            break


# %%
def clear_lists(feedback= False):
    #Borrar listas
    try:
        #Detalles del producto
        product_index.clear()
        product_id.clear()
        name.clear()
        price.clear()
        currency.clear()
        rating.clear()
        n_bought.clear()
        sent_by.clear()
        sold_by.clear()
        stock.clear()
        n_reviews.clear()

        #Imágenes
        product_id_images.clear()
        all_product_images.clear()
        head_image_url.clear()

        #Categorías
        categories.clear()

        #Reseñas
        five_star_percentages.clear()
        four_star_percentages.clear()
        three_star_percentages.clear()
        two_star_percentages.clear()
        one_star_percentages.clear()
        star_percentages.clear()

        #Comentarios
        reviewproduct_index.clear()
        reviewproduct_code.clear()
        review_ids.clear()
        authors.clear()
        titles.clear()
        dates.clear()
        verified_purchases.clear()
        was_helpful_votes.clear()
        texts.clear()
        review_stars.clear()
        if feedback:
            print("Listas limpiadas.")
    except Exception as e:
        if feedback:
            print(f"Error al limpiar las listas: {e}")

clear_lists(feedback=True)

# %% [markdown]
# # Codigo

# %%
clear_lists(feedback=False)
counter_links = 0
for link in product_links:

    counter_links += 1
    print(f"Visitando enlace {counter_links} de {len(product_links)}: {link}")

    # Indice del producto
    product_index.append(counter_links)

    # Visitar el enlace del producto
    driver.get(link)
    time.sleep(random.uniform(0.5, 2))

    # Obtener los detalles del producto
    get_product_details(feedback=False)

    # Obtener las categorías del producto
    get_categories(feedback=False)

    # Obtener las imágenes del producto
    get_images(feedback=False)

    # Obtener las características del producto
    get_characteristics(feedback=False)

    # Obtener los porcentajes de estrellas
    get_star_percentages(feedback=False)
    
    # Obtener todas las reseñas del producto
    get_all_reviews(feedback=True, max_pages=max_comment_pages_to_visit)
    

# %%
print("------DETALLES DEL PRODUCTO------")
print("INDICE", len(product_index),product_index)
print("ID_PRODUCTO", len(product_id),product_id)
print("NOMBRE", len(name),name)
print("PRECIO", len(price),price)
print("MONEDA", len(currency),currency)
print("RATING", len(rating),rating)
print("COMPRAS", len(n_bought),n_bought)
print("ENVIADO POR", len(sent_by),sent_by)
print("VENDIDO POR", len(sold_by),sold_by)
print("STOCK", len(stock),stock)
print("URL_HEAD", len(head_image_url),head_image_url, "\n")

print("------IMAGENES------")
print("PRODCT_ID_IMAGEN", len(product_id_images),product_id_images)
print("URL_IMAGENES",len(all_product_images),all_product_images, "\n")

print("------CATEGORIAS y CARACTERISTICAS------")   
print("CATEGORIAS", len(categories),categories)
print("CARACTERISTICAS", len(all_product_features),all_product_features ,"\n")

print("------ESTRELLAS------")
print("5ESTRELLAS", len(five_star_percentages),five_star_percentages)
print("4ESTRELLAS", len(four_star_percentages),four_star_percentages)
print("3ESTRELLAS", len(three_star_percentages),three_star_percentages)
print("2ESTRELLAS", len(two_star_percentages),two_star_percentages)
print("1ESTRELLAS", len(one_star_percentages),one_star_percentages)

print("------RESEÑAS------")
print("INDICE_PRODUCTO", len(reviewproduct_index),reviewproduct_index)
print("CODIGO_PRODUCTO", len(reviewproduct_code),reviewproduct_code)
print("ID_RESEÑA", len(review_ids),review_ids)
print("AUTOR", len(authors),authors)
print("TITULO", len(titles),titles)
print("FECHA", len(dates),dates)
print("COMPRA_VERIFICADA", len(verified_purchases),verified_purchases)
print("VOTOS_UTILES", len(was_helpful_votes),was_helpful_votes)
print("TEXTO", len(texts),texts[:10])
print("ESTRELLAS", len(review_stars),review_stars)


# %% [markdown]
# # DATAFRAMES

# %%
# Creamos un dir llamado CSV para guardar los archivos
CSV_dir = os.path.join(Download_dir, 'CSV')
if not os.path.exists(CSV_dir):
    os.makedirs(CSV_dir, exist_ok=True)

# %%
# DATAFRAME DE PRODUCTOS
# Crear un DataFrame con los datos de los productos
products_df = pd.DataFrame({
    "Product_index": product_index,
    "Product_ID": product_id,
    "Name": name,
    "Price": price,
    "Currency": currency,
    "Rating": rating,
    "N_bought": n_bought,
    "Sent_by": sent_by,
    "Sold_by": sold_by,
    "Stock": stock,
    "N_reviews": n_reviews,
    "Categories": categories,
    "Head_image_URL": head_image_url
})

# Guardar el DataFrame en un archivo CSV
products_df.to_csv(os.path.join(CSV_dir, 'products_data.csv'), index=False)

#Imprimimos el dataframe
products_df

# %%
# DATAFRAME DE IMAGENES
# Unimos cada product_image con su product_id y separamos la lista
separated_product_images = []
for index, product_images in enumerate(all_product_images):
    for image in product_images:
        separated_product_images.append([product_id_images[index], image])

# Creamos un DataFrame con las imágenes separadas
images_df = pd.DataFrame(separated_product_images, columns=["Product_ID", "Image_URL"])

# Guardar el DataFrame en un archivo CSV
images_df.to_csv(os.path.join(CSV_dir, 'images_data.csv'), index=False)

#Imprimimos el dataframe
images_df

# %%
# Crear un DataFrame a partir de las listas de porcentajes de estrellas
df_star_percentages = pd.DataFrame({
    'Product_Index': product_index,
    'Product_ID': product_id,
    'Five_Star': five_star_percentages,
    'Four_Star': four_star_percentages,
    'Three_Star': three_star_percentages,
    'Two_Star': two_star_percentages,
    'One_Star': one_star_percentages
})

# Guardar el DataFrame en un archivo CSV
df_star_percentages.to_csv(os.path.join(CSV_dir, 'star_percentages_data.csv'), index=False)

#Imprimimos el dataframe
df_star_percentages

# %%
# Crear un DataFrame a partir de las listas de reseñas
df_reviews = pd.DataFrame({
    'Product_ID': reviewproduct_code,
    'Review_ID': review_ids,
    'Author': authors,
    'Title': titles,
    'Date': dates,
    'Verified_Purchase': verified_purchases,
    'Was_Helpful_Votes': was_helpful_votes,
    'Review_Stars': review_stars,
    'Texto' : texts
})

# Guardar el DataFrame en un archivo CSV
df_reviews.to_csv(os.path.join(CSV_dir, 'reviews_data.csv'), index=False)

#Imprimimos el dataframe
df_reviews

# %%
# Definir las listas de categorías
category_lists = [[] for _ in range(8)]

# Llenar las listas de categorías
for cat in categories:
    for i in range(8):  # Iterar hasta 8, que es el número máximo de categorías
        if i < len(cat):
            category_lists[i].append(cat[i])
        else:
            category_lists[i].append("")

# Asignar los resultados a las variables category_1, category_2, ..., category_8
category_1, category_2, category_3, category_4, category_5, category_6, category_7, category_8 = category_lists

# Crear un DataFrame con las categorías
categories_df = pd.DataFrame({
    "Product_index": product_index,
    "Product_ID": product_id,
    "Category_1": category_1,
    "Category_2": category_2,
    "Category_3": category_3,
    "Category_4": category_4,
    "Category_5": category_5,
    "Category_6": category_6,
    "Category_7": category_7,
    "Category_8": category_8
})

# Guardar el DataFrame en un archivo CSV
categories_df.to_csv(os.path.join(CSV_dir, 'categories_data.csv'), index=False)

#Imprimimos el dataframe
categories_df

# %%
if close_after_finish:
    driver.quit()
else:
    cerrar = input("Presiona Y y Enter para cerrar el navegador: ")
    if cerrar == "Y":
        driver.quit()
    else:
        pass

time.sleep(2)

# Borrar el perfil temporal después de su uso
try:
    shutil.rmtree(user_data_dir)
    print("Perfil temporal eliminado.")
except Exception as e:
    print(f"Error al eliminar el perfil temporal: {e}")


