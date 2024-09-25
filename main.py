from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import random
import urllib.parse

# Lista de números de telefone
phones_number = []

# Lista de mensagens
messages = []

# Inicializar o driver do navegador
driver = webdriver.Chrome()

without_number = 0  # Contador de números inválidos

# Loop pelos números
for phone_number in phones_number:
    # Selecionar mensagem aleatória e codificá-la
    selected_message = random.choice(messages)
    encoded_message = urllib.parse.quote(selected_message)
    
    # Criar o link com o número de telefone e a mensagem codificada
    link_https = f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_message}"
    driver.get(link_https)
    
    # Esperar a página carregar (tempo para você escanear o QR code na primeira vez)
    time.sleep(20)
    
    try:
        # Verificar se a mensagem de número inválido aparece
        try:
            invalid_number_message = driver.find_element(By.XPATH, "//div[contains(text(),'O número de telefone compartilhado por url é inválido.')]")
            print(f"Número {phone_number} é inválido. Pulando...")
            without_number += 1
            continue  # Pular para o próximo número

        except NoSuchElementException:
            # Se não encontrou a mensagem de erro, podemos continuar
            pass

        # Aguarda até o campo de envio de mensagens estar presente
        message_box = driver.find_element(By.XPATH, "//div[@contenteditable='true']")
        
        # Focar no campo de mensagem
        message_box.click()

        # Localizar o botão de envio pelo 'aria-label'
        send_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Enviar"]')
        
        # Clicar no botão de envio
        send_button.click()
        print(f"Mensagem enviada para {phone_number}.")
        
        # Aguarda para ter certeza de que a mensagem foi enviada
        time.sleep(5)
    
    except Exception as e:
        print(f"Erro ao enviar mensagem para {phone_number}: {e}")
    
    # Pausar antes de ir para o próximo número (com tempo aleatório)
    random_time = random.randint(60, 300)
    time.sleep(random_time)

# Mostrar o total de números inválidos ao final
print(f"Total de números inválidos: {without_number}")

# Fechar o navegador ao terminar
driver.quit()
