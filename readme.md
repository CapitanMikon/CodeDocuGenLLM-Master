Väčšina zo skriptov má -h pre zobrazenie pomoci.

## Ako používať:
1. Pripraviť si vektorovú databázu.
	a) Získane javadoc z Java kódu `repo_indexer.py --dir <PATH> --ext java`
	b) Naloženie vektorovej databázy `populate_vectordb_from_jsons.py --dir <ROOT_PATH_TO_JSON>`
2. Zavolať metódu `query_llm(question)` v `codegen_prototype.py`.
a) alebo spustiť web app
	1. Spustenie webapp (svetlá téma)
`run app.py --theme.primaryColor="#FF4B4B" --theme.backgroundColor="#FFFFFF" --theme.secondaryBackgroundColor="#F0F2F6" --theme.textColor="#31333F"`
	2. Spustenie webapp  (tmavá téma)
`run app.py`
alebo spustenie v PyCharm
Názov modulu: `streamlit.web.cli`
Parametre: `run app.py --theme.primaryColor="#FF4B4B" --theme.backgroundColor="#FFFFFF" --theme.secondaryBackgroundColor="#F0F2F6" --theme.textColor="#31333F"` alebo `run app.py`

Most of the scripts have -h to show help.

## How to use:
1. Prepare a vector database.
	a) Get the javadoc from the Java code `repo_indexer.py --dir <PATH> --ext java`
	b) Load the vector database `populate_vectordb_from_jsons.py --dir <ROOT_PATH_TO_JSON>`
2. Call the `query_llm(question)` method in `codegen_prototype.py`.
a) or run the web app
	1. Run the webapp (light theme)
`run app.py --theme.primaryColor="#FF4B4B" --theme.backgroundColor="#FFFFFF" --theme.secondaryBackgroundColor="#F0F2F6" --theme.textColor="#31333F"`
	2. Launch the webapp (dark theme)
`run app.py`
or running in PyCharm
Module name: `streamlit.web.cli`
Parameters: `run app.py --theme.primaryColor="#FF4B4B" --theme.backgroundColor="#FFFFFF" --theme.secondaryBackgroundColor="#F0F2F6" --theme.textColor="#31333F"` or `run app.py`

Translated with DeepL.com (free version)
