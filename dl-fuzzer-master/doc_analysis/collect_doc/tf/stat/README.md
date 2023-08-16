- `tf2.1_py_fromweb.yaml`: \<API title:URL\> map collected from https://www.tensorflow.org/versions/r2.1/api_docs/python.  Contraints 4846 maps.




- `tf2.1_py_uniqueurl.yaml`: \<Unique URL: Aliases\> map of 2588 unique url.




- `tf2.1_py_uniqueurl_filename.yaml`: The script `save_doc.py` add `2` at the end of the title to avoid overwrite and saved into `../../doc2.1source/*.html`. The corresponding filename is added in the `./stat/tf2.1_py_uniqueurl.yaml` and saved into this file. 




- `except_url`: Part of the result of `parse_html.py`. \<Category: URL\>. The category including:  

    - class
    - module
    - deprecated
    - warning (contains camel case in the title, possible class API, need further investigation)
    - collected (all collected/parsed url)

    

- `other_exception`: The printed out exception message while running `parse_html.py`




- `inconsistency.csv`: All the **Signature-description inconsistency** case collcted here for manual check and report.