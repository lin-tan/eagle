## Document Collection & Parsing

- `get_url.py`: Collect a list/map of API title and their url (document) from https://www.tensorflow.org/versions/r2.1/api_docs/python. 
    - 4846 APIs collected (including aliases), 2588 unique URL(document)
    - saved the \<API:URL\> mapping into: `./stat/tf2.1_py_fromweb.yaml` (4846 keys)
    - saved the \<Unique URL:\ Aliases> mapping into `./stat/tf2.1_py_uniqueurl.yaml` (2588 keys)

- `save_doc.py`: Collect the html source of the documents, for each of the url in `./stat/tf2.1_py_uniqueurl.yaml`. 
    - Saved at `../../doc2.1source/*.html` (Not in bitbucket because it is too large). 
    - The script add `2` at the end of the title to avoid overwrite. 
    - Added the corresponding filename in the `./stat/tf2.1_py_uniqueurl.yaml` and saved into `./stat/tf2.1_py_uniqueurl_filename.yaml`


<!-- - `parse_utils.py`: Some methods used for parsing the web

- `yaml_file_cls.py`: Defines `yaml_file` class for parsing -->

- `parse_html.py`: Parse the web source collected from `../../doc2.1source/` , get input/output/exception information, and saved into `./doc2.1_parsed/*.yaml`.  
    - Part of the result saved at `./stat/except_url`
        - class
        - module
        - deprecated
        - warning (contains camel case in the title, possible class API, need further investigation)
        - collected (all collected/parsed url)
        - no_arg: no argument section
        - no_signature

    - For other exception message: `./stat/other_exception`
    - Order of filtering: module-> deprecated -> class API -> no signature -> some other class API ("inherits from"+having "attributes" section) -> no argument section


- `count.py`: Count the files and print out the breakdowns 


- `tmp_get_inconsistency.py`: Get all the **Signature-description inconsistency** case and save the result into `./stat/inconsistency.csv` for manual check and report.



**A breakdown of all APIs: **

- Total API (including aliases): 4846
- Unique URL (Document) : 2588
- Collected (Parsed): 1330  (including 49 warning)
- Not collected (Filtered out): 1243
    - Module: 254
    - class api: 549
    - Deprecated: 188
    - No argument section: 205
    - No signature found: 47
- Failed to collect/parse: 15:
    - Signature-description inconsistency: 12
    - others: 3
        - multiple arg/argument section: 1
        - multiple return/yield section: 1
        - multiple signature: 1





