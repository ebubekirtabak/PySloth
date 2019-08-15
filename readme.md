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
-  zip
-  exe
- Blob stream
- .etc

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

