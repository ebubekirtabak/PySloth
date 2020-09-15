## PySloth  
  
### What is PySloth ?  
  
PySloth is a programmable web bot. PySLoth can simulate user behavior. Can search web pages with use Javascript and without Javascript.  Can limited multithread process.  
  
### How To Install ?  
  
Install PySloth requirements.  
  
```pip install -r requirements.txt```  

### USAGE

Create  a file from named ```myconf.json``` in project directory.  
  
Copy content of ```conf.json``` file to your ```myconf.json``` file.  

Starting Web crawling:  

From file:

``` python main.py scope_file folder_name scope_name.json ```    

From myconf:

``` python main.py scope  scope_name' ```  
  
### $scope_name  
  
```json  
{  
  "scope_name": "example.com scope",  
  "settings": { ... }  
}  

```  
  
### Main features  

#### Variable Helpers

PySloth can read and save variable from web element. PySloth is then used in the variable that it saves on any website. 
In this example, you can see how you subscribe to another website by getting a temporary email address.
  
![Variable Helpers](https://github.com/ebubekirtabak/scrappy/blob/master/media/gif/variable_helpers.gif "Variable Helpers")

#### Conditional Scraping

PySloth can process dynamic conditions.

````json
{
  "type": "condition",
  "conditions": [
    {
      "type": "if_selector",
      "if_selector": "//table[1]/tbody/tr[2]/td/font/b[text() = 'Error']",
      "if": [
        {
          "type": "driver_event",
          "action": "refresh_page",
        },
        {
          "type": "rerun_actions"
        },
        {
          ....
        }
      ],
      "else": [
        ...,
        {
          ....
        },
        ....
      ]
    }
  ]
}
````

#### Database Actions (MongoDB)

You can use MongoDB in PySloth.
Example Databse Action:
```
 {
   "type": "database",
   "action": "upsert_to_database",
   "query_keys": [
     "company_name"
   ],
   "collection_name": "company_informations",
   "variable_type": "$_GET_VARIABLE",
   "variable_names": [
     { "key":  "name", "value": "search_text" },
     { "key":  "company_name", "value": "wiki.company_name" },
     { "key":  "company_logo", "value": "wiki.company_logo" },
     { "key":  "description_text", "value": "wiki.description_text" },
     { "key":  "company_description", "value": "wiki.company_description" },
     { "key":  "related_search", "value": "wiki.related_search" },
     { "key":  "profile_urls", "value": "wiki.profile_urls" },
     { "key":  "values", "value": "wiki.values" },
     { "key":  "url", "value": "wiki.url" },
     { "key":  "website_url", "value": "wiki.website_url" }
   ]
 }
```
#### Login   

PySloth can login any website.

![login functionalty](https://github.com/ebubekirtabak/scrappy/blob/master/media/gif/login.gif "Login function")  
  
#### User Actions  
  
![User Actions](https://github.com/ebubekirtabak/scrappy/blob/master/media/gif/script_actions.gif "User Actions")

#### Download File

PySloth can download file from web site.

##### Downloadable file types.
- mp3
- mp4
- image (jpeg, png, jpg, .etc)
- zip
- exe
- Blob stream
- .etc

#### Custom Script Support

````json
"script_actions": [
    { ... },
    {
      "type": "run_custom_script",
      "delay": 0,
      "sleep": 0,
      "custom_script": {
        "type": "python",
        "script": "custom_scripts/proxy_tester.py"
      }
    },
    { ... }
]
````

#### Passing Parameters From VariableHelpers

When you use "${variable_name}" Pysloth will use own VariableHelpers. In this way you can replace Pysloth's data from in your custom script.

````json
"script_actions": [
    { ... },
    {
      "type": "run_custom_script",
      "delay": 0,
      "sleep": 0,
      "custom_script": {
      "variable_name": "current_experience",
      "params": [
        "${variable_name}"
      ]
      "type": "python",
      "script": "custom_scripts/proxy_tester.py"
      }
    },
    { ... }
]
````

#### Redirect to url function. (New)
````json
"script_actions": [
  { ... },
  {
    "type": 'navigate_to',
    "to": 'https://github.com'
  },
  { ... }
]
````

#### Convert Table to xlsx. (Coming) 

