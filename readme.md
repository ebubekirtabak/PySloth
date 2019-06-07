## PySloth  
  
### What is PySloth ?  
  
PySloth is a programmable web bot. PySLoth can simulate user behavior. Can search web pages with use Javascript and without Javascript.  Can limited multithread process.  
  
### How To Install ?  
  
Install PySloth requirements.  
  
```pip install -r requirements.txt```  
  
Create  a file from named ```myconf.json``` in project directory.  
  
Copy content of ```conf.json``` file to your ```myconf.json``` file.  
  
Starting Web crawling:  
  
``` python main.py 'scope'  'scope_name'' ```  
  
### $scope_name  
  
```json  
{  
  "scope_name": "example.com scope",  
  "settings": { ... }  
}  
```  
  
### Main features  
  
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
- .etc

#### Convert Table to xlsx. (Coming) 

