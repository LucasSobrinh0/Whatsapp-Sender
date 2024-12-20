from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    TimeoutException
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import urllib.parse

def carregar_numeros(arquivo):
    with open(arquivo, "r", encoding="utf-8") as file:
        linhas = file.readlines()
    numeros = []
    for linha in linhas:
        numeros.extend([num.strip() for num in linha.split(" ") if num.strip()])
    return numeros

arquivo_numeros = "clientes_atualizado.txt"
phones_number = carregar_numeros(arquivo_numeros)

messages = ["""
COMUNICADO OFICIAL

Prezados clientes e amigos:

Nos últimos dias o Escritório Vilarouca tem sido vítima de uma tentativa de golpe na qual uma quadrilha, se passando por nossos funcionários, solicita valores para a liberação de alvará em nome do Doutor Felipe Vilarouca.

O Escritório Vilarouca informa que JAMAIS solicita valores para seus clientes para a liberação de alvará ou qualquer outra facilidade. Esclarecemos que todas as informações dos processos são públicas e podem ser acessadas por qualquer pessoa e a qualquer momento através dos sites dos Tribunais de Justiça, o que, infelizmente, facilita a prática de golpes.

O Núcleo Trabalhista do Escritório Vilarouca orienta seus clientes a jamais depositarem qualquer valor a pedido de qualquer pessoa que se diga funcionário e que, na hipótese excepcional de cobrança de custas, o assunto será tratado pessoalmente ou por videoconferência. Ressalta que todas as comunicações são feitas exclusivamente através dos seguintes meios:
Telefone fixo: (65) 2127-8496
Whatsapp: (65) 2127-8496

Instagram: advocaciavilarouca
Email: trabalhista.mt@fvdvocacia.com.br

As autoridades já foram comunicadas para as devidas providências. 
Colocamo-nos à disposição para maiores esclarecimentos pelos canais oficiais.

Atenciosamente
VILAROUCA ADVOCACIA E CONSULTORIA
"""]

chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)

without_number = 0

for phone_number in phones_number:
    selected_message = random.choice(messages)
    encoded_message = urllib.parse.quote(selected_message)

    link_https = f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_message}"
    driver.get(link_https)

    time.sleep(10)

    # Verifica se aparece mensagem de número inválido
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/span[2]/div/span/div/div/div/div/div/div[1]'))
        )
        print(f"Número {phone_number} é inválido. Pulando...")
        without_number += 1
        continue
    except TimeoutException:
        # Não encontrou mensagem de número inválido
        pass

    max_attempts = 3
    attempt = 0
    sent = False

    while attempt < max_attempts and not sent:
        try:
            # Espera o botão de envio ficar clicável (ajuste o seletor conforme necessário)
            send_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[2]/button'))  # Ajuste para o seletor correto
            )
            send_button.click()
            print(f"Mensagem enviada para {phone_number}.")
            sent = True
        except (TimeoutException, ElementClickInterceptedException) as e:
            attempt += 1
            if attempt < max_attempts:
                print(f"Erro ao clicar no botão de envio para {phone_number}, tentando de novo ({attempt}/{max_attempts})...")
                # Recarrega a página e tenta novamente
                driver.refresh()
                time.sleep(5)  # Aguarda um pouco após recarregar
            else:
                print(f"Falha ao enviar mensagem para {phone_number} após {max_attempts} tentativas.")

    # Pausa entre o envio para cada número
    time.sleep(random.randint(1, 2))

print(f"Total de números inválidos: {without_number}")
driver.quit()
