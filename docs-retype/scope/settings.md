---
Title: Settings
---

### What is Settings?  
  
Settings is an object that represents main configuration for scraper.
  

#- Settings
- type `Object`
- Describe your main configuration.


#- Settings
- enable_javascript `boolean`
- Whether to enable javascript rendering in scraper.
- driver `json`
- Web driver settings
- thread_limit `number`
- Multi thread limit.
- thread_time_out `number`
- Thread time out limit as seconds.
- database `json`
- Database definitions.

```json
{
        "search_time_sleep": 5,
        "download_time_sleep": 5,
        "thread_time_out": 300,
        "thread_limit": 15,
        "thread_controller": "mongo",
        "session_id": "alamy_dollar",
        "role": "main",
        "is_go_again_history": false,
        "multi_process": {
            "time_out": 300,
            "limit": 10,
            "base": "mongo"
        },
        "driver": {
            "driver_path": "/usr/lib/chromium-browser/chromedriver",
            "driver_arguments": []
        },
        "database": {
            "type": "MongoDB",
            "name": "BotDatabase",
            "history_collection_name": "history_collection",
            "log_collection_name": "log_collection",
            "thread_collection_name": "thread_collection",
            "collection_name": "main_collection",
            "uri": "mongodb://localhost:27017/",
            "user_name": "admin"
        },
        "file_settings": {
            "max_file_length": 150
        }
    }
```