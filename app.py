from selenium import webdriver
from selenium.webdriver.common.by import By

import chromedriver_autoinstaller
import genanki
import csv

headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}
# Define the path to your Chrome webdriver
chromedriver_filepath = chromedriver_autoinstaller.install()
# Create a new Chrome webdriver instance
driver = webdriver.Chrome(chromedriver_filepath)

def get_css():
    with open('style.css','r',encoding='utf-8') as c:
        res = c.read()
    return res

# Define the Anki model
model = genanki.Model(
    1540535300,
    'Spanish Terms',
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
    css=get_css(),)

# Define the Anki deck
deck = genanki.Deck(
    1399908496,
    'Spanish Vocabulary')

def add_note_to_deck(deck, word, definition, image_url, audio_url):
    # Build the note
    note = genanki.Note(
        model=model,
        fields=[word, definition, '<img src="{}">'.format(image_url), '[sound:{}]'.format(audio_url)],
        tags=['Vocabulary'])
    
    # Add the note to the deck
    deck.add_note(note)

def get_audio_and_def_url(word):
    word_url = f"https://dict.naver.com/eskodict/#/search?query={word}"
    # Navigate to the word URL
    driver.get(word_url)
    # Wait for the audio element to load
    driver.implicitly_wait(10)
    # Find the audio element on the page
    audio_element = driver.find_element(By.CSS_SELECTOR,'#searchPage_entry > div > div:nth-child(1) > div > span.unit_listen.my_old_pron_area > button')
    # Get the URL of the audio file
    audio_url = audio_element.get_attribute('purl')

    definition = get_definition(word_url)
    return audio_url, definition

def get_definition(url):
    word = driver.find_element(By.CSS_SELECTOR,'#searchPage_entry > div > div:nth-child(1) > div > a')
    word.click()
    definition = driver.find_element(By.CSS_SELECTOR,'#content > div.section.section_entry._section_entry > div > div.entry_mean > div')
    return definition.text

def get_image_url(word):
    url = f"https://pixabay.com/es/images/search/{word}/"

    driver.get(url)
    driver.implicitly_wait(10)
    img_element = driver.find_element(By.CSS_SELECTOR,'#app > div:nth-child(1) > div > div.container--wYO8e > div.results--mB75j > div > div > div:nth-child(1) > div:nth-child(1) > div > a > img')
    image_url = img_element.get_attribute('src')
    return image_url

with open('words.csv', newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        word = row['word']
        definition_org = row['definition']

        try:
            audio_src,definition = get_audio_and_def_url(word)
        except Exception as e:
            print(e)
            audio_src = ''
            definition = definition_org

        try:
            image_src = get_image_url(word)
        except Exception as e:
            print(e)
            image_src = ''
        
        # Add the data to the Anki deck
        add_note_to_deck(deck, word, definition, image_src, audio_src)

# Export the deck to an .apkg file
genanki.Package(deck).write_to_file('spanish_vocabulary.apkg')

driver.quit()
