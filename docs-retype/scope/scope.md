---
Title: Scope
---

### What is Scope?  
  
Scope is a file contains scraper configurations. Can pass file or json directly.
  

### Scope File
- type `json`
- Describe your scraper configuration and actions.

The value returned will represent te internal Task object used by the API,
which will contain two extra fields besides `title`:

### Scope
- settings `json`
- Scraper settings ; database, driver etc.
- scope_name `string`
- Scraper Name
- script_actions `array`
- List of scraper actions.