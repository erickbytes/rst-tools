# rst-url-validator
A Python script for validating reStructuredText Format URLs

**Install Python Dependencies**

```
pip install requests
pip install rich
```

**Run the RST URL Validator CLI**
```
python3.12 rst-url-validator.py your_file.rst
```

![console view of rst-url-validator.py](rst-url-validator-report.png "rst validator")

**External .rst Links**

The rst-url-validator.py script expects links to be in this format, with a single or double underscore at the end:

```
`free online courses on Coursera <https://www.coursera.org/learn/python>`__ 
```