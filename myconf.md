## MYCONF.JSON

This json file contains an object that contains web site settings in the json array format named "scope".
The settings are kept in array format in the "scope" object. Each object in the array is a separate web site scan settings.
In this way, multiple websites or the same website can be scanned according to different settings.

### $scope_name

*Required.

Your scope name.

### page 

```json
"page": {
    "url": "https://example.com/list",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36 OPR/54.0.2952.64",
    "data": ""
},
```
#### $url

Start address. The scan starts from here.

#### $user_agent

User agent.

### $reporting 

````json
"reporting": {
    "page_count": 0,
    "download_counter": 0
},
````

*required 

### SETTINGS {}

```json
"settings": {
    "search_time_sleep": 60,
    "download_time_sleep": 5,
    "multi_process": {
     "time_out": 300,
     "limit": 3,
     "base": "mongo || memory"
    },
    "session_id": "Button event tester",
    "role": "main || scanner || downloader",
    "is_go_again_history": false,
    "driver": {
        "driver_path": "your browser driver path",
        "driver_arguments": [
          "--no-sandbox",
          "--headless"
        ]
    }
},
```
##### $multi_process

Multi process limit and configurations.

###### $time_out

Process milisecond time out limit. 

##### $search_time_sleep

Herbir web sayfası tarandığında parçacığın bir sonraki parçağı açana kadarki bekleme süresi.
Sayfaların tarama hızını ayarlamak için kullanılır. Bu şekilde web sitesine 1 saat içerisinde gönderilen istek sayısı kontrol altına alınır.
Bu şekilde botun kara listeye girme sorunu şözülür.


##### $download_time_sleep

Herhangi bir dosya indirildiğinde parçacığın bir sonraki parçağı açana kadarki bekleme süresi.

##### $session_id

Yapılan tarama işleminni idsidir Bu id ile **session** klasörü altında session kaydı oluşturulur.İşlem sırasında herhangi bir kesilme olursa işlem
session kaydı sayesinde kaldığı yerden devam ettirilir.

#### $driver {}

Configuration settings for Web Driver.

##### $driver_path

Selenium Framework kullanıcı deneyimini taklit edebilmek için browser driverına ihtiyaç duyar. Buraya kullanmak istediğiniz 
tarayıcı driver yolunu eklemeniz gerekmektedir. 

Şuanda sadece ChromeDriver desteği vardır. [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads)

##### $driver_arguments

WebDriver için argüman parametlerini içerir.

[Selenium Arguments](http://www.assertselenium.com/java/list-of-chrome-driver-command-line-arguments/)

##### $driver_emulations

WebDriver için emilatör parametlerini içerir.

[Selenium Options](https://seleniumhq.github.io/selenium/docs/api/rb/Selenium/WebDriver/Chrome/Options.html#add_emulation-instance_method)