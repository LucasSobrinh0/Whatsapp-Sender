from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock

from kivymd.uix.button import MDFlatButton

from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivymd.uix.menu import MDDropdownMenu

from threading import Thread
import time
import random
import urllib.parse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# Load the KV string
Builder.load_file('main.kv')
from kivymd.uix.boxlayout import MDBoxLayout

class EditDialogContent(MDBoxLayout):
    pass


class PhoneManagerScreen(Screen):
    phones_number = ListProperty([])
    selected_number = StringProperty()

    def add_numbers(self):
        input_text = self.ids.phone_input.text.strip()
        if not input_text:
            return

        new_numbers = [num.strip() for num in input_text.split(',') if num.strip().isdigit()]
        invalid_entries = [num.strip() for num in input_text.split(',') if not num.strip().isdigit()]

        if new_numbers:
            for number in new_numbers:
                if number not in self.phones_number:
                    self.phones_number.append(number)
            self.update_number_list()

        if invalid_entries:
            self.show_error_dialog(f"Entradas inválidas ignoradas: {', '.join(invalid_entries)}\nPor favor, insira apenas números separados por vírgulas.")

        self.ids.phone_input.text = ""

    def update_number_list(self):
        self.ids.phone_list.clear_widgets()
        for number in self.phones_number:
            item = OneLineListItem(text=number)
            item.bind(on_release=lambda instance, num=number: self.open_number_menu(num, instance))
            self.ids.phone_list.add_widget(item)

    def open_number_menu(self, number, instance_item):
        self.selected_number = number
        menu_items = [
            {
                "text": "Editar",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.edit_number(),
            },
            {
                "text": "Remover",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.remove_number(),
            },
        ]
        self.menu = MDDropdownMenu(
            caller=instance_item,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()

    def edit_number(self):
        self.menu.dismiss()
        self.edit_dialog = MDDialog(
        title="Editar Número",
        type="custom",
        content_cls=EditDialogContent(),
        buttons=[
            MDFlatButton(
                text="Salvar",
                on_release=lambda x: self.save_edited_number()
            ),
            MDFlatButton(
                text="Cancelar",
                on_release=lambda x: self.edit_dialog.dismiss()
            ),
        ],
    )

        self.edit_dialog.open()

    def save_edited_number(self):
        new_number = self.edit_dialog.content_cls.ids.edit_number_input.text.strip()
        if new_number.isdigit():
            index = self.phones_number.index(self.selected_number)
            self.phones_number[index] = new_number
            self.update_number_list()
            self.edit_dialog.dismiss()
        else:
            self.show_error_dialog("Número inválido! Apenas números são permitidos.")

    def remove_number(self):
        self.menu.dismiss()
        self.phones_number.remove(self.selected_number)
        self.update_number_list()

    def show_error_dialog(self, message):
        self.dialog = MDDialog(
            title="Aviso",
            text=message,
            buttons=[MDFlatButton(text="Fechar", on_release=lambda x: self.dialog.dismiss())],
        )
        self.dialog.open()


class MessageManagerScreen(Screen):
    messages = ListProperty([])
    selected_message = StringProperty()

    def add_message(self):
        message = self.ids.message_input.text.strip()
        if not message:
            return

        if message in self.messages:
            self.show_error_dialog("Esta mensagem já foi adicionada.")
            return

        self.messages.append(message)
        self.update_message_list()
        self.ids.message_input.text = ""


    def update_message_list(self):
        self.ids.message_list.clear_widgets()
        for msg in self.messages:
            item = TwoLineListItem(text=msg)
            item.bind(on_release=lambda instance, m=msg: self.open_message_menu(m, instance))
            self.ids.message_list.add_widget(item)

    def open_message_menu(self, message, instance_item):
        self.selected_message = message
        menu_items = [
            {
                "text": "Editar",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.edit_message(),
            },
            {
                "text": "Remover",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.remove_message(),
            },
        ]
        self.menu = MDDropdownMenu(
            caller=instance_item,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()

    def edit_message(self):
        self.menu.dismiss()
        self.edit_dialog = MDDialog(
            title="Editar Mensagem",
            type="custom",
            content_cls=Builder.load_string('''
BoxLayout:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(150)
    MDTextField:
        id: edit_message_input
        hint_text: "Digite a nova mensagem"
        text: app.root.get_screen('message_manager').selected_message
        multiline: True
'''),
            buttons=[
                MDFlatButton(
                    text="Salvar",
                    on_release=lambda x: self.save_edited_message()
                ),
                MDFlatButton(
                    text="Cancelar",
                    on_release=lambda x: self.edit_dialog.dismiss()
                ),
            ],
        )
        self.edit_dialog.open()

    def save_edited_message(self):
        new_message = self.edit_dialog.content_cls.ids.edit_message_input.text.strip()
        if new_message:
            index = self.messages.index(self.selected_message)
            self.messages[index] = new_message
            self.update_message_list()
            self.edit_dialog.dismiss()
        else:
            self.show_error_dialog("A mensagem não pode ser vazia.")

    def remove_message(self):
        self.menu.dismiss()
        self.messages.remove(self.selected_message)
        self.update_message_list()

    def show_error_dialog(self, message):
        self.dialog = MDDialog(
            title="Aviso",
            text=message,
            buttons=[MDFlatButton(text="Fechar", on_release=lambda x: self.dialog.dismiss())],
        )
        self.dialog.open()


class SettingsScreen(Screen):
    min_time = NumericProperty(5)
    max_time = NumericProperty(10)

    def validate_times(self):
        try:
            self.min_time = int(self.ids.min_time_input.text)
            self.max_time = int(self.ids.max_time_input.text)
            if self.min_time > self.max_time:
                self.show_error_dialog("O tempo mínimo não pode ser maior que o tempo máximo.")
                return False
            if self.min_time < 0 or self.max_time < 0:
                self.show_error_dialog("Os tempos não podem ser negativos.")
                return False
            return True
        except ValueError:
            self.show_error_dialog("Por favor, insira valores válidos para os tempos.")
            return False

    def show_error_dialog(self, message):
        self.dialog = MDDialog(
            title="Aviso",
            text=message,
            buttons=[MDFlatButton(text="Fechar", on_release=lambda x: self.dialog.dismiss())],
        )
        self.dialog.open()


class MainScreen(Screen):
    pass


class Manager(ScreenManager):
    pass


class MessagingApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        return Manager()
    

    def change_screen(self, screen_name):
        """Muda para a tela especificada."""
        self.root.current = screen_name

    def start_sending_messages(self):
        phone_screen = self.root.get_screen('phone_manager')
        message_screen = self.root.get_screen('message_manager')
        settings_screen = self.root.get_screen('settings')

        if not phone_screen.phones_number:
            self.show_error_dialog("A lista de números de telefone está vazia.")
            return
        if not message_screen.messages:
            self.show_error_dialog("A lista de mensagens está vazia.")
            return
        if not settings_screen.validate_times():
            return

        self.min_time = settings_screen.min_time
        self.max_time = settings_screen.max_time
        self.phone_numbers = phone_screen.phones_number
        self.messages = message_screen.messages

        self.confirm_dialog = MDDialog(
            title="Atenção",
            text="Você tem 30 segundos para escanear o QR Code antes do início do envio das mensagens.",
            buttons=[
                MDFlatButton(text="Cancelar", on_release=lambda x: self.confirm_dialog.dismiss()),
                MDFlatButton(text="Iniciar", on_release=lambda x: self.begin_sending()),
            ],
        )
        self.confirm_dialog.open()

    def begin_sending(self):
        self.confirm_dialog.dismiss()
        Thread(target=self.send_messages_thread).start()
        if len(self.phone_numbers) == 0:
            self.show_error_dialog("A lista de números está vazia. Não é possível iniciar o envio.")
            return

        self.progress_bar = self.progress_dialog.content_cls
        self.progress_dialog.open()

    def send_messages_thread(self):
        driver = webdriver.Chrome()
        driver.get("https://web.messages.com/")
        time.sleep(30)

        without_number = 0
        sent_count = 0

        for index, phone_number in enumerate(self.phone_numbers):
            selected_message = random.choice(self.messages)
            encoded_message = urllib.parse.quote(selected_message)
            link_https = f"https://web.messages.com/send?phone={phone_number}&text={encoded_message}"
            driver.get(link_https)

            try:
                try:
                    driver.find_element(By.XPATH, "//div[contains(text(),'O número de telefone compartilhado por url é inválido.')]")
                    self.update_status(f"Número {phone_number} é inválido. Pulando...")
                    without_number += 1
                    continue
                except NoSuchElementException:
                    pass

                time.sleep(5)
                message_box = driver.find_element(By.XPATH, "//div[@contenteditable='true']")
                message_box.click()
                send_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Enviar"]')
                send_button.click()
                self.update_status(f"Mensagem enviada para {phone_number}.")
                sent_count += 1
                time.sleep(5)

            except Exception as e:
                self.update_status(f"Erro ao enviar mensagem para {phone_number}: {e}")
                without_number += 1

            Clock.schedule_once(lambda dt: self.update_progress(sent_count + without_number))
            try:
                random_time = random.randint(self.min_time, self.max_time)
            except ValueError:
                random_time = 10  # Tempo padrão

            self.update_status(f"Aguardando {random_time} segundos antes do próximo envio...")
            time.sleep(random_time)

        self.update_status(f"Total de números inválidos ou com erro: {without_number}")
        self.update_status("Envio de mensagens concluído.")
        driver.quit()
        Clock.schedule_once(lambda dt: self.progress_dialog.dismiss())
        Clock.schedule_once(lambda dt: self.show_summary_dialog(sent_count, without_number))

    def update_status(self, message):
        print(message)

    def update_progress(self, value):
        self.progress_bar.value = value

    def show_error_dialog(self, message):
        self.dialog = MDDialog(
            title="Erro",
            text=message,
            buttons=[MDFlatButton(text="Fechar", on_release=lambda x: self.dialog.dismiss())],
        )
        self.dialog.open()

    def show_summary_dialog(self, sent_count, error_count):
        total_numbers = len(self.phone_numbers)
        message = f"""
Envio de mensagens concluído.

Total de números processados: {total_numbers}
Mensagens enviadas com sucesso: {sent_count}
Números inválidos ou com erro: {error_count}
"""
        self.summary_dialog = MDDialog(
            title="Resumo do Envio",
            text=message.strip(),
            buttons=[MDFlatButton(text="Fechar", on_release=lambda x: self.summary_dialog.dismiss())],
        )
        self.summary_dialog.open()


if __name__ == "__main__":
    MessagingApp().run()
