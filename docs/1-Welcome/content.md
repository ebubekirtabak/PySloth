---
Title: Welcome
---

Welcome to the PySloth wiki!


### What is PySloth ?  
  
PySloth is a programmable web bot. PySLoth can simulate user behavior. Can search web pages with use Javascript and without Javascript.  Can limited multithread process.  
  

#- Scope File
- type `json`
- Describe your scraper configuration and actions.

The value returned will represent te internal Task object used by the API,
which will contain two extra fields besides `title`:

#- Scope
- settings `json`
- Scraper settings ; database, driver etc.
- scope_name `string`
- Scraper Name
- script_actions `array`
- List of scraper actions.