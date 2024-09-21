

Directory Structure

my-website-project/
├── .github/                # GitHub actions and workflows
│   └── workflows/
│       └── deploy.yml      # CI/CD workflow for building and deploying
├── data/                   # Source files for processing
│   ├── quran-morphology.txt
│   └── quranic-corpus-morphology-0.4.txt
├── scripts/                # Python scripts for processing data
│   ├── script1.py
│   ├── script2.py
│   └── script3.py
├── src/                    # Development source code (HTML, CSS, JS, generated JSON)
│   ├── index.html          # Your HTML file for development
│   ├── styles.css          # Your CSS
│   ├── app.js              # Your JS
│   └── json/               # JSON files for development use
│       ├── quran_morphology_output.json
│       └── other_json_files.json
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
