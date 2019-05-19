## PySloth

### What is PySloth ?

PySloth is a programmable web bot. PySLoth can simulate user behavior. Can search web pages with use javascript and without javascript.
Can limited multithread process.

### Ho To Install ?

Install pySloth requirements.

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

![login functionalty](https://github.com/ebubekirtabak/scrappy/blob/master/media/gif/login.gif "Login function")

#### Script Actions

![login functionalty](https://github.com/ebubekirtabak/scrappy/blob/master/media/gif/script_actions.gif "Login function")
