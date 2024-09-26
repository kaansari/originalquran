

Directory Structure

originalquran/
├── .github/                # GitHub actions and workflows
│   └── workflows/
│       └── deploy.yml      # CI/CD workflow for building and deploying
├── data/                   # Source files for processing
│   ├── quran-morphology.txt
│   └── quranic-corpus-morphology-0.4.txt
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
