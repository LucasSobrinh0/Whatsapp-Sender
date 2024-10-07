#  Whatsapp Sender.

## Bibliotecas que precisam ser instaladas:

pip install selenium

## É necessário instalar o driver do do chrome.

https://developer.chrome.com/docs/chromedriver/downloads/version-selection?hl=pt-br

## Nos números de telefone, é necessário utilizar o exemplo abaixo, devido a API do whatsapp. Utilize no máximo 300 números para não ser banido no whatsapp.

(codigo do pais) (codigo do estado) (numero de telefone)

phones_number = [5511999995555, 5511988885555]

## No campo de mensagens, é obrigatório colocar três aspas no começo e no fim, depois virgula. É interessante deixar pelo menos 5 mensagens diferentes.

messages = ["""Mensagem um""", """Mensagem dois"""]

## No tempo para prosseguir para a próxima mensagem, é interessante colocar um tempo entre 1 à 5 minutos.

random_time = random.randint(60, 300)
time.sleep(random_time)



