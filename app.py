from selenium import webdriver
from selenium.webdriver.common.by import By

import chromedriver_autoinstaller
import genanki
import csv
import random
import requests
import os

class Anki():
    def __init__(self, csv_path, model_name, deck_name):
        if not os.path.isdir('audio'):
            os.mkdir('audio')
        
        self.note_data = {}
        self.media_files = list()

        self.driver= self._get_driver()
        self.csv = self._read_csv(csv_path)
        self.model = self._generate_model(model_name)
        self.deck = self._generate_deck(deck_name)
    
    def __del__(self):
        self.driver.quit()

    def _get_driver(self):
        headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}
        chromedriver_filepath = chromedriver_autoinstaller.install()
        driver = webdriver.Chrome(chromedriver_filepath)
        return driver
    def _get_css(self):
        with open('style.css','r',encoding='utf-8') as c:
            res = c.read()
        return res
    def _generate_model(self,model_name):
        model = genanki.Model(
        random.randrange(1 << 30, 1 << 31),
        model_name,
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
            {'name': 'Image'},
            {'name': 'Audio'}
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '''
                <!-- 앞면(front) 템플릿 -->
                <div class="card-front">
                    <!-- 단어 -->
                    <div class="card-word">{{Question}}</div>

                    <!-- 그림 -->
                    <div class="card-image">
                        {{Image}}
                    </div>

                    <!-- 발음 사운드 -->
                    <div class="card-audio">
                        {{Audio}}
                    </div>
                </div>
                ''',
                'afmt': '''
                <!-- 뒷면(back) 템플릿 -->
                <div class="card-back">
                    <!-- 뜻 -->
                    <div class="card-meaning">{{Answer}}</div>
                </div>
                ''',
            },
        ],
        css=self._get_css(),)
        return model
    def _generate_deck(self,deck_name):
        # Define the Anki deck
        deck = genanki.Deck(
        random.randrange(1 << 30, 1 << 31),
        deck_name)
        return deck
    def _read_csv(self,csv_path):
        '''
        Read a CSV file and return its rows as a list of dictionaries

        Args:
        csv_path (str): Path to the CSV file

        Returns:
        list: List of dictionaries representing each row in the CSV file

        '''
        with open(csv_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
        return rows
    
    def begin(self):
        for idx,row in enumerate(self.csv):
            word = row['word']
            definition_org = row['definition']

            data = {   'word' : '',
                        'definition' : '',
                        'image_src' : '',
                        'audio_src' : '',   }
            
            self.note_data[word] = data
            self.note_data[word]['word'] = word

            naver_url = ""
            try:
                naver_url = self._get_audio(word)
            except Exception as e:
                print(e)
                self.note_data[word]['audio_src'] = ''
            
            try:
                self._get_definition(word,naver_url)
            except Exception as e:
                print(e)
                self.note_data[word]['definition'] = definition_org

            try:
                self._get_image_url(word)
            except Exception as e:
                print(e)
                self.note_data[word]['image_src'] = ''

            # Add the data to the Anki deck
            self._add_note_to_deck(self.note_data[word])

    def write_to_apkg(self, file_name = "anki_deck"):
        # Export the deck to an .apkg file
        package = genanki.Package(self.deck)
        self._add_media_files(package)
        package.write_to_file(f'{file_name}.apkg')

    def _add_note_to_deck(self, data):
        word = data['word']
        definition = data['definition']
        image_url = data['image_src']
        audio_url = data['audio_src']
        print(word,definition,image_url,audio_url)
        # Build the note
        note = genanki.Note(
            model=self.model,
            fields=[word, definition, f'<img src="{image_url}">', f'[sound:{audio_url}]'],
            tags=['Vocabulary'])

        # Add the note to the deck
        self.deck.add_note(note)
    
    def _add_media_files(self,package):
        print(self.media_files)
        package.media_files = self.media_files

    def _get_audio(self, word):
        word_url = f"https://dict.naver.com/eskodict/#/search?query={word}"
        # Navigate to the word URL
        self.driver.get(word_url)
        # Wait for the audio element to load
        self.driver.implicitly_wait(10)
        # Find the audio element on the page

        file = f'{word}.mp3'
        audio_path = f'audio/{file}'

        if not os.path.isfile(audio_path):
            audio_element = self.driver.find_element(By.CSS_SELECTOR,'#searchPage_entry > div > div:nth-child(1) > div > span.unit_listen.my_old_pron_area > button')
            # Get the URL of the audio file
            if audio_element :
                audio_url = audio_element.get_attribute('purl')
            else:
                audio_url = ""
            
            response = requests.get(audio_url)

            with open(audio_path,'wb') as f:
                f.write(response.content)
        
        self.media_files.append(audio_path)
        self.note_data[word]['audio_src'] = file

        return word_url

    def _get_image_url(self, word):
        url = f"https://pixabay.com/es/images/search/{word}/"

        self.driver.get(url)
        self.driver.implicitly_wait(10)
        img_element = self.driver.find_element(By.CSS_SELECTOR,'#app > div:nth-child(1) > div > div.container--wYO8e > div.results--mB75j > div > div > div:nth-child(1) > div:nth-child(1) > div > a > img')
        if img_element :
            image_url = img_element.get_attribute('src')
        else:
            image_url = ""
        
        self.note_data[word]['image_src'] = image_url
    
    def _get_definition(self,word,url):
        word_element = self.driver.find_element(By.CSS_SELECTOR,'#searchPage_entry > div > div:nth-child(1) > div > a')
        word_element.click()
        definition = self.driver.find_element(By.CSS_SELECTOR,'#content > div.section.section_entry._section_entry > div > div.entry_mean > div')
        if definition :
            defi = definition.text
        else:
            defi = ''

        self.note_data[word]['definition'] = defi


if __name__=='__main__':
    anki = Anki(csv_path='words.csv',model_name='Spanish Terms', deck_name='Spanish Vocabulary')
    anki.begin()
    anki.write_to_apkg(file_name='res')


