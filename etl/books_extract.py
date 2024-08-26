import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException

strat_time = time.time()

# Configuration du webdriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=options)

URL = "https://www.amazon.fr/s?i=stripbooks&rh=n%3A301061&fs=true"

# Fonction pour accepter les cookies si la bannière est présente
def accept_cookies():
    try:
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'sp-cc-accept'))
        )
        accept_button.click()
        print("Bannière de cookies acceptée.")
    except (NoSuchElementException, TimeoutException):
        print("Aucune bannière de cookies trouvée ou elle n'est pas cliquable.")

# Fonction pour récupérer les informations des livres sur plusieurs pages
def get_all_books():
    all_books = []
    current_url = URL  # Utilisation de la variable globale URL
    for page in range(1, 21):  # Naviguer jusqu'à la 20ème page
        try:
            print(f"Accès à la page {page}...")
            driver.get(current_url)
            accept_cookies()  # Accepter les cookies avant de continuer
            time.sleep(5)  # Attendre que la page soit complètement chargée
            book_elements = WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[@data-component-type="s-search-result"]'))
            )
            print(f"Page {page} - Nombre de livres trouvés: {len(book_elements)}")

            for index, book in enumerate(book_elements):
                book_data = {}
                try:
                    # Récupérer chaque élément de manière indépendante pour éviter les erreurs de référence obsolète
                    title_element = book.find_element(By.XPATH, './/h2/a/span')
                    price_element = book.find_element(By.XPATH, './/span[@class="a-price-whole"]')
                    price_fraction_element = book.find_element(By.XPATH, './/span[@class="a-price-fraction"]')
                    rating_element = book.find_element(By.XPATH, './/span[@aria-label and contains(@aria-label, "étoiles")]')
                    reviews_element = book.find_element(By.XPATH, './/span[@class="a-size-base s-underline-text"]')
                    author_element = book.find_element(By.XPATH, './/div[@class="a-row"]')
                    image_element = book.find_element(By.XPATH, './/img[@class="s-image"]')
                    book_url_element = book.find_element(By.XPATH, './/h2/a')

                    # Récupérer le titre du livre
                    book_data['title'] = title_element.text

                    # Récupérer le prix du livre
                    book_data['price'] = price_element.text + "," + price_fraction_element.text + "€"

                    # Récupérer la note d'évaluation du livre
                    book_data['rating'] = rating_element.get_attribute('aria-label').strip().split(" ")[0]

                    # Récupérer le nombre d'évaluations du livre
                    book_data['reviews'] = reviews_element.text.strip().replace("\u202f", "").replace("\u00a0", "").replace(" ", "")

                    # Récupérer l'auteur du livre
                    book_data['author'] = author_element.text

                    # Récupérer l'image du livre
                    book_data['image_url'] = image_element.get_attribute('src')

                    # Récupérer l'URL du livre
                    book_data['book_url'] = book_url_element.get_attribute('href')

                    # Ajouter les détails supplémentaires et les avis des clients plus tard
                    all_books.append(book_data)
                except (NoSuchElementException, TimeoutException) as e:
                    print(f"Erreur lors du traitement du livre {index + 1} sur la page {page}: {e}")

            print(f"Page {page} récupérée avec succès")
            if page < 20:
                try:
                    # Construire l'URL de la page suivante
                    current_url = f"https://www.amazon.fr/s?i=stripbooks&rh=n%3A301061&fs=true&page={page+1}&qid=1721380579&ref=sr_pg_{page+1}"
                    print(f"URL de la page suivante: {current_url}")
                except Exception as e:
                    print(f"Erreur lors de la récupération de la page suivante: {e}")
                    break
        except (NoSuchElementException, TimeoutException, WebDriverException) as e:
            print(f"Erreur lors de la récupération de la page {page}: {e}")
            break
    return all_books

# Fonction pour récupérer les détails supplémentaires d'un livre
def get_additional_info(book_url):
    details_dict = {}
    try:
        driver.get(book_url)
        time.sleep(3)  # Attendre que la page soit complètement chargée

        ul_element = driver.find_element(By.XPATH, '//*[@id="detailBullets_feature_div"]/ul')

        # Récupérer tous les éléments <li>
        li_elements = ul_element.find_elements(By.TAG_NAME, 'li')

        # Extraire et afficher le texte de chaque élément <li>
        for li in li_elements:
            key = li.find_element(By.CSS_SELECTOR, 'span.a-text-bold').text.strip()
            value = li.find_elements(By.TAG_NAME, 'span')[-1].text.strip()
            details_dict[key] = value

    except (NoSuchElementException, TimeoutException) as e:
        print(f"Erreur lors de la récupération des détails pour {book_url}: {e}")
        details_dict["Détails non disponibles"] = str(e)

    return details_dict

# Nouvelle fonction pour récupérer les avis des clients
def get_reviews(book_url):
    all_reviews = []
    driver.get(book_url)
    time.sleep(5)  # Attendre que la page soit complètement chargée

    try:
        # Attendre que l'élément soit cliquable et cliquer dessus
        reviews_button_xpath = '//*[@id="reviews-medley-footer"]/div[2]/a'
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, reviews_button_xpath))).click()
        
        while True:
            # Attendre que les avis soient présents
            all_reviews_xpath = '//*[@id="cm_cr-review_list"]//div[contains(@id, "customer_review")]'
            review_elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, all_reviews_xpath)))

            # Vérifier s'il y a des avis clients
            if not review_elements:
                print("Aucun avis client trouvé.")
                break

            # Récupérer le texte de chaque avis
            for review_element in review_elements:
                review_data = {}
                try:
                    review_data['title'] = review_element.find_element(By.CSS_SELECTOR, 'a.review-title').text.strip()
                except:
                    review_data['title'] = "N/A"

                try:
                    review_data['text'] = review_element.find_element(By.CSS_SELECTOR, 'span.review-text-content span').text.strip()
                except:
                    review_data['text'] = "N/A"

                try:
                    review_data['author'] = review_element.find_element(By.CSS_SELECTOR, 'span.a-profile-name').text.strip()
                except:
                    review_data['author'] = "N/A"

                try:
                    review_data['date'] = review_element.find_element(By.CSS_SELECTOR, 'span.review-date').text.strip()
                except:
                    review_data['date'] = "N/A"

                all_reviews.append(review_data)

            # Vérifier s'il y a une page de pagination suivante
            try:
                next_page = driver.find_element(By.XPATH, '//*[@id="cm_cr-pagination_bar"]/ul/li[@class="a-last"]/a')
                next_page.click()
                time.sleep(5)  # Attendre que la page suivante soit complètement chargée
            except NoSuchElementException:
                break  # Pas de page suivante

    except (NoSuchElementException, TimeoutException) as e:
        print(f"Erreur: {e}")

    return all_reviews

# Fonction principale pour orchestrer le processus
def main():
    books = []

    # Étape 1 : Récupérer les informations des livres sur toutes les pages
    try:
        books = get_all_books()
        print(f"Nombre total de livres récupérés: {len(books)}")
    except Exception as e:
        print(f"Erreur lors de la récupération des informations des livres: {e}")

    # Vérifier que toutes les pages ont été récupérées avant de continuer
    if len(books) == 0:
        print("Aucun livre récupéré. Arrêt du script.")
        driver.quit()
        return

    # Étape 2 : Ajouter les détails supplémentaires et les avis des clients pour chaque livre
    try:
        for book in books:
            print(f"Récupération des détails pour le livre: {book['title']}")
            book['additional_info'] = get_additional_info(book['book_url'])
            book['customer_reviews'] = get_reviews(book['book_url'])
    except Exception as e:
        print(f"Erreur lors du traitement des livres: {e}")

    # Enregistrer les données dans un fichier JSON
    with open('books.json', 'w', encoding='utf-8') as f:
        json.dump(books, f, ensure_ascii=False, indent=4)


    # Afficher les informations des livres récupérés
    for book in books:
        book.setdefault('additional_info', "Détails non disponibles")
        book.setdefault('customer_reviews', [])
        print(f"Titre: {book['title']}, Prix: {book['price']}, Note: {book['rating']}, Nombre d'évaluations: {book['reviews']}, Auteur: {book['author']}, Image: {book['image_url']}, URL: {book['book_url']}, Détails: {book['additional_info']}, Avis: {book['customer_reviews']}")

    # Fermer le driver Selenium
    driver.quit()


# Exécution du script principal
if __name__ == "__main__":
    main()


end_time = time.time()
elapsed_time = end_time - strat_time

hours = int(elapsed_time // 3600)
minutes = int((elapsed_time % 3600) // 60)
seconds = elapsed_time % 60

print(f"Le script a mis {hours} heures, {minutes} minutes et {seconds:.2f} secondes à s'exécuter.")