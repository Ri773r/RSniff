# RSniff ![](https://img.shields.io/badge/language-Python3.7+-brightgreen.svg)  
Web background scanning tool based on Python coroutine 
# Install
`pip install -r requirements.txt`
# Usage
`python ScanTool.py [OPTIONS]`
## Options  
* -u, --baseUrl TEXT            Basice URL of splicing  [required]  
* -p, --dictPath TEXT           Dictionary path  [required]  
* -h, --customerHeaders TEXT    Customer headers  
* -c, --maxConcurrency INTEGER  Maximum concurrent  [default: 10]  
* -t, --timeout INTEGER         Timeout time  [default: 2]  
* -q, --queueCap INTEGER        Queeu capacity  [default: 50]  
* --help                        Show this message and exit.  
## Show
![](https://github.com/Ri773r/RSniff/blob/master/show.png)
# Todo
- [x] ~~Customer headers~~  
- [x] ~~Asynchronous read file~~    
# License
![](https://img.shields.io/badge/License-MIT-blue.svg)
