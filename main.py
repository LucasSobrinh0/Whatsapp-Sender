from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import urllib.parse

from selenium.webdriver.support.wait import WebDriverWait


# Função para carregar os números de telefone de um arquivo
def carregar_numeros(arquivo):
    with open(arquivo, "r") as file:
        linhas = file.readlines()
    # Remover vírgulas extras e separar os números
    numeros = []
    for linha in linhas:
        numeros.extend([num.strip() for num in linha.split(",") if num.strip()])
    return numeros

# Arquivos de entrada
arquivo_numeros = "clientes_atualizado.txt"  # Contém os números formatados

# Carregar números
phones_number = carregar_numeros(arquivo_numeros)

# Mensagem fixa
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
driver.maximize_window()

without_number = 0  # Contador de números inválidos

# Loop pelos números
for phone_number in phones_number:
    attempts = 0  # Contador de tentativas por número
    max_attempts = 3  # Limite de tentativas

    while attempts < max_attempts:
        try:
            # Selecionar mensagem e codificá-la
            selected_message = random.choice(messages)
            encoded_message = urllib.parse.quote(selected_message)

            # Criar o link com o número de telefone e a mensagem codificada
            link_https = f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_message}"
            driver.get(link_https)

            # Verificar se a mensagem de número inválido aparece
            try:
                invalid_number_message = driver.find_element(By.XPATH,
                                                             "//div[contains(text(),'O número de telefone compartilhado por url é inválido.')]")
                print(f"Número {phone_number} é inválido. Pulando...")
                without_number += 1
                break  # Pular para o próximo número

            except NoSuchElementException:
                # Se não encontrou a mensagem de erro, podemos continuar
                pass

            try:
                # Localizar e clicar no campo de mensagem
                message_box = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@contenteditable="true" and @data-tab="1"]'))
                )
                message_box.click()

                # Localizar o botão de envio
                send_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[2]/button'))
                )
                send_button.click()
                print(f"Mensagem enviada para {phone_number}.")
            except Exception as e:
                print(f"Erro ao enviar mensagem para {phone_number}: {e}")

            # Aguarda para ter certeza de que a mensagem foi enviada
            time.sleep(5)
            break  # Sai do loop após o envio bem-sucedido

        except (ElementNotInteractableException, NoSuchElementException) as e:
            print(f"Erro ao enviar mensagem para {phone_number} (tentativa {attempts + 1}/{max_attempts}): {e}")
            attempts += 1  # Incrementa a contagem de tentativas
            time.sleep(10)  # Espera antes de tentar novamente

        except Exception as e:
            print(f"Erro inesperado para {phone_number}: {e}")
            break  # Sai do loop para evitar loop infinito em caso de erro grave

    if attempts == max_attempts:
        print(f"Falha ao enviar mensagem para {phone_number} após {max_attempts} tentativas.")

    # Pausar antes de ir para o próximo número
    random_time = random.randint(5, 10)
    time.sleep(random_time)

# Mostrar o total de números inválidos ao final
print(f"Total de números inválidos: {without_number}")

# Fechar o navegador ao terminar
driver.quit()
