## MYCONF.JSON

Bu json dosyası scope adında json array formatında web sitesi  ayarlarını içeren bir obje barındırır.
Ayarlar **scope** objesi içersinde array formatında tutulur.Array içerisindeki her bir obje ayrı bir web sitesini tarama ayarlarıdır.
Bu şekilde aynı anda birden fazla web sitesi ya da aynı web sites, farklı ayarlara göre taranılabilir.

### $scope_name"" 

* *Required.

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

### SETTINGS {}

```json
"settings": {
    "search_time_sleep": 60,
    "download_time_sleep": 5,
    "thread_limit": 3,
    "session_id": "Button event tester",
    "driver": {
        "driver_path": "your browser driver path",
        "driver_arguments": [
          "--no-sandbox",
          "--headless"
        ]
    }
},
```

##### $search_time_sleep

Herbir web sayfası tarandığında parçacığın bir sonraki parçağı açana kadarki bekleme süresi.
Sayfaların tarama hızını ayarlamak için kullanılır. Bu şekilde web sitesine 1 saat içerisinde gönderilen istek sayısı kontrol altına alınır.
Bu şekilde botun kara listeye girme sorunu şözülür.


##### $download_time_sleep

Herhangi bir dosya indirildiğinde parçacığın bir sonraki parçağı açana kadarki bekleme süresi.

##### $thread_limit

Tarama için açılacak maksimum parçacık limitidir.
Bu şekilde program işlemci gücüne göre çalışacak şekilde ayarlanır.

##### $session_id

Yapılan tarama işleminni idsidir Bu id ile **session** klasörü altında session kaydı oluşturulur.İşlem sırasında herhangi bir kesilme olursa işlem
session kaydı sayesinde kaldığı yerden devam ettirilir.

#### $driver {}

Web driver için konfigürasyon ayalarını barındırır.

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