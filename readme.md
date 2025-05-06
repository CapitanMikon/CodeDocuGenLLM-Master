Väčšina zo skriptov má -h pre zobrazenie pomoci.

## Ako používať:
1. Index repozitára
`repo_indexer.py --dir <PATH> --ext java`
2. Generovanie dokumentácie 1. iterácia
`documentation_generator.py --dir "data_index\REPO_NAME"`
3. Generovanie dokumentácie 2. iterácia
`improved_documentation_generator.py --dir "data_generated_doc\REPO_NAME"`
4. Pridanie dát do vektorovej DB
`vectordb_manager.py --add "data_generated_doc_improved\REPO_NAME"`
alebo
`vectordb_manager.py --add "data_generated_doc\REPO_NAME"`
5. 
	a) Spustenie webapp (svetlá téma)
`run app.py --theme.primaryColor="#FF4B4B" --theme.backgroundColor="#FFFFFF" --theme.secondaryBackgroundColor="#F0F2F6" --theme.textColor="#31333F"`
	b) Spustenie webapp  (tmavá téma)
`run app.py`
alebo spustenie v PyCharm
Názov modulu: `streamlit.web.cli`
Parametre: `run app.py --theme.primaryColor="#FF4B4B" --theme.backgroundColor="#FFFFFF" --theme.secondaryBackgroundColor="#F0F2F6" --theme.textColor="#31333F"` alebo `run app.py`

#### Metriky:
1. kosínusová podobnosť
`calculate_cosine_similarity.py --human "src\data_index\REPO_NAME" --ai "src\data_generated_doc_improved\REPO_NAME"`
2. F1 skriptom
`f1_measure.py --ai "src\data_generated_doc_improved\REPO_NAME"`
3. LOD
`lod metric.py --ai "src\data_generated_doc_improved\REPO_NAME"`

Most of the scripts have -h to show help.

## How to use:
1. Repository index
`repo_indexer.py --dir <PATH> --ext java`
2. Generate documentation 1st iteration
`documentation_generator.py --dir "data_index\REPO_NAME"`
3. Generating documentation 2nd iteration
`improved_documentation_generator.py --dir "data_generated_doc\REPO_NAME"`
4. Adding data to the vector DB
`vectordb_manager.py --add "data_generated_doc_improved\REPO_NAME"`
or
`vectordb_manager.py --add "data_generated_doc\REPO_NAME"`
5. 
	a) Running the webapp (light theme)
`run app.py --theme.primaryColor="#FF4B4B" --theme.backgroundColor="#FFFFFF" --theme.secondaryBackgroundColor="#F0F2F6" --theme.textColor="#31333F"`
	b) Launch the webapp (dark theme)
`run app.py`
or running in PyCharm
Module name: `streamlit.web.cli`
Parameters: `run app.py --theme.primaryColor="#FF4B4B" --theme.backgroundColor="#FFFFFF" --theme.secondaryBackgroundColor="#F0F2F6" --theme.textColor="#31333F"` or `run app.py`

#### Metrics:
1. cosine similarity
`calculate_cosine_similarity.py --human "src\data_index\REPO_NAME" --ai "src\data_generated_doc_improved\REPO_NAME"`
2. F1 using script
`f1_measure.py --ai "src\data_generated_doc_improved\REPO_NAME"`
3. LOD
`lod metric.py --ai "src\data_generated_doc_improved\REPO_NAME"`
