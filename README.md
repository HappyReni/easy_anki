# easy_anki

The easy_anki is a Python script that creates an Anki deck from a CSV file containing vocabulary words and their definitions. 

## Features

- Retrieves audio pronunciation files
- Downloads images related to the vocabulary from Pixabay
- Pulls the definitions from the Naver Dictionary
- Stores the generated Anki deck as an .apkg file

## Dependencies

- Selenium
- Genanki
- Requests

## Installation

1. Install dependencies with:
```
$ pip install selenium genanki requests
```

2. Download and install the [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads)
   to work with the current version of the Google Chrome browser. Add the downloaded ChromeDriver executable to the PATH.

3. Clone or download the repository.

4. Edit the `words.csv` file, adding vocabulary words to be included in the deck.

## Usage

1. Run the script:

```python
python app.py
```

2. The generated Anki deck file will be saved as `res.apkg`.

3. Import the deck into Anki to start studying!

## Example

Given a CSV file with the following content:

```
word,definition
casa,house
perro,dog
```

The script will produce an Anki deck named "Spanish Vocabulary" with cards containing the vocabulary words (casa, perro), their definitions (house, dog), example images, and their pronunciations.

**Front of card:**

- Vocabulary word: casa
- Image corresponding to the word
- [sound:casa.mp3]

**Back of card:**

- Definition: house

## Notes

- The Selenium WebDriver might require updates depending on the updates in the target websites, Pixabay and Naver Dictionary.

- This script scraps data from Pixabay and Naver Dictionary; only use for the code and data for private purpose.