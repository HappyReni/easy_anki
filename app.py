from selenium import webdriver
from selenium.webdriver.common.by import By

import chromedriver_autoinstaller
import genanki
import csv
import random
import requests
import os

class Anki():
    def __init__(self, csv_path, model_name):
        headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}
        chromedriver_filepath = chromedriver_autoinstaller.install()
        self.driver = webdriver.Chrome(chromedriver_filepath)
        self.csv = self._read_csv(csv_path)

        self.model = genanki.Model(
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
                        <audio controls>
                            <source src="{{Audio}}" type="audio/mpeg">
                            Your browser does not support the audio element.
                        </audio>
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

        # Define the Anki deck
        self.deck = genanki.Deck(
        random.randrange(1 << 30, 1 << 31),
        'Spanish Vocabulary')
    
    def __del__(self):
        self.driver.quit()

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
        for row in self.csv:
            word = row['word']
            definition_org = row['definition']
            try:
                audio_src,definition = self.get_audio_and_def_url(word)
            except Exception as e:
                print(e)
                audio_src = ''
                definition = definition_org
            try:
                image_src = self.get_image_url(word)
            except Exception as e:
                print(e)
                image_src = ''
            # Add the data to the Anki deck
            self.add_note_to_deck(self.deck, word, definition, image_src, audio_src)
    
    def write_to_apkg(self, file_name = "result"):
        # Export the deck to an .apkg file
        genanki.Package(self.deck).write_to_file(f'{file_name}.apkg')

    def _get_css(self):
        with open('style.css','r',encoding='utf-8') as c:
            res = c.read()
        return res

    def add_note_to_deck(self, deck, word, definition, image_url, audio_url):
        # Build the note
        note = genanki.Note(
            model=self.model,
            fields=[word, definition, '<img src="{}">'.format(image_url), '[sound:{}]'.format(audio_url)],
            tags=['Vocabulary'])

        # Add the note to the deck
        self.deck.add_note(note)

    def get_audio_and_def_url(self, word):
        word_url = f"https://dict.naver.com/eskodict/#/search?query={word}"
        # Navigate to the word URL
        self.driver.get(word_url)
        # Wait for the audio element to load
        self.driver.implicitly_wait(10)
        # Find the audio element on the page

        audio_path = f'audios/{word}.mp3'
        
        if not os.path.isfile(audio_path):
            audio_element = self.driver.find_element(By.CSS_SELECTOR,'#searchPage_entry > div > div:nth-child(1) > div > span.unit_listen.my_old_pron_area > button')
            # Get the URL of the audio file
            audio_url = audio_element.get_attribute('purl')

            response = requests.get(audio_url)

            with open(audio_path,'wb') as f:
                f.write(response.content)
            
        definition = self.get_definition(word_url)
        return os.path.abspath(audio_path), definition

    def get_image_url(self, word):
        url = f"https://pixabay.com/es/images/search/{word}/"

        self.driver.get(url)
        self.driver.implicitly_wait(10)
        img_element = self.driver.find_element(By.CSS_SELECTOR,'#app > div:nth-child(1) > div > div.container--wYO8e > div.results--mB75j > div > div > div:nth-child(1) > div:nth-child(1) > div > a > img')
        image_url = img_element.get_attribute('src')
        return image_url
    
    def get_definition(self,url):
        word = self.driver.find_element(By.CSS_SELECTOR,'#searchPage_entry > div > div:nth-child(1) > div > a')
        word.click()
        definition = self.driver.find_element(By.CSS_SELECTOR,'#content > div.section.section_entry._section_entry > div > div.entry_mean > div')
        return definition.text


if __name__=='__main__':
    anki = Anki(csv_path='words.csv',model_name='Spanish Terms')
    anki.begin()
    anki.write_to_apkg()


