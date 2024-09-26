# The Original Quran
This project demonstrates how the Quran has been preserved since the time the Prophet Muhammad, the Messenger of Allah, delivered it to humanity.

I have created a simple, single-page HTML version of the Quran for my personal use, and you are welcome to contribute, fork, or use it as you wish.

You can see the demo at https://kaansari.github.io/originalquran/.

## Features of this Quran:
The Quran displays the text in the original Kufic script, which was used when the Quran was first written.
It shows the morphology of each word.
Each verse has a play button for recitation.
Each verse is linked to the oldest Quran manuscripts available in the world.
Purpose
The purpose of this project is to show that the Quran we have today is exactly the same as it was during the time of the Prophet Muhammad. It allows users to easily compare the modern text with ancient manuscripts.

## Text of the Quran
The text, behind the font, is exactly the same as the Warsh/Uthmani and Pakistani/Indian scripts.

### Contribution
I need help in comparing the old manuscripts to this version of the Quran. In 99% of the cases, the script matches the Saudi/Egyptian scripts, but there are a few verses where I found minor differences. For example, "Malaika" is spelled with an Alif, and "Raai3a" is spelled with an Alif, where in the Saudi/Egyptian Quran the Alif is identified as a small Alif.

```
Directory Structure

originalquran/
├── .github/                # GitHub actions and workflows
│   └── workflows/
│       └── deploy.yml      # CI/CD workflow for building and deploying
├── data/                   # Source files for processing
│   ├── quran-morphology.txt
│   └── arabic.md           # Quran md file
│   └── english.md           # English translation

├── scripts/                # Python scripts for processing data
│   ├── arabic-corpus.py    # script to parse and make json file for the morphology
│   ├── ayahandword_parser.py  # this script takes the arabic.md file and parses the word
├── src/                    # Development source code (HTML, CSS, JS, generated JSON)
│   ├── index.html          # HTML file for development and the main page
│   ├── styles.css          # CSS
│   ├── app.js              # JS
│   └── json/               # JSON files for development use
│       ├── quran_morphology_output.json   #morphology file
│       └── sura.json  # list of sura
│       └── quran_words.json  # 77430 words of the quran
│       └── combinned_quran.json  # combines the quran and english translation
│       └── sura.json  # list of sura
├── build/                  # Build folder created during CI/CD (ignored by git)
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   └── json/               # Final JSON files for production
│       ├── quran_morphology_output.json
│       └── other_json_files.json
├── .gitignore              # Ignore build folder and other unnecessary files
├── requirements.txt        # Python dependencies
└── README.md               # Project information
```