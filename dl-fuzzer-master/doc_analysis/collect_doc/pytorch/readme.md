- `get_docsource.py`: collect the map < document link ->  filename stored>
    - store the map in `stat/save_src.yaml`
    - the soup(source file) are stored at `/Users/danning/Desktop/deepflaw/web_source/pt_1.6_source/`
    - each document link contains several APIs


- `./stat1.6/new_format.yaml`: Documents (file name) that has new format (instead of a webpage contains multiple APIs, it contains multiple links which link to each API documents)

- `get_docsource_newformat.yaml`: Collect the document with new format. And update the `save_src.yaml` with API document webpage, which is saved in `stat1.6/save_src_new_format.yaml`



