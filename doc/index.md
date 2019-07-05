Welcome to the PySloth wiki!


### What is PySloth ?  
  
PySloth is a programmable web bot. PySLoth can simulate user behavior. Can search web pages with use Javascript and without Javascript.  Can limited multithread process.  
  
### How To Install ?  
  
Install PySloth requirements.  
  
```pip install -r requirements.txt```  

### USAGE

Create  a file from named ```myconf.json``` in project directory.  
  
Copy content of ```conf.json``` file to your ```myconf.json``` file.  

Starting Web crawling:  
  
``` python main.py 'scope'  'scope_name'' ```  
  
  ### Ready Configurations
  - instagram
  - Pinterest
  - Freepik
  
  Table Of Content
  
  - SCOPE
      - Settings
        - Multi Process
        - Database
        - File Settings
        - Pagination
        
      - History
      - Script Actions
      
### How To Programming PySloth ? 

#### Script Actions

Script Actions are emulated by taking commands in Json format.

#### $type

Action item type

type list:

- click
- excute_script
- download
- download_loop
- event
- event*`


``json
  "script_actions": [
    {
      "type": "excute_script",
      "sleep": 5,
      "actions": [
        {
          "type": "excute_script",
          "script": "window.scrollTo(0, document.body.scrollHeight);",
          "delay": 1
        }
      ]
    }
    ]
```

... coming soon.