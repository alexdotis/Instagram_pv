# Instagram_pv
Download Images and Videos from specific profile in instagram


# About project
Instagram_pv is a very simple Instagram Bot that can download images and videos of the user, like Gallery with photos or videos. It saves the data in the folder of your choice. It will not download posts from tag. Even though it was just a way to learn a bit the [Selenium](https://selenium-python.readthedocs.io/), the main thing it was the data scraping, but became a simple 'download posts' bot.

# How to start
To run the bot, just download it and run it through **cmd**. 

Simple usage of code:

```Instagram_PV.py -u example@hotmail.com -p mypassword -f myfile -n stackoverjoke```

**Notes**
it doesn't require the link of the instagram, but the name that you want to search. In this case is **stackoverjoke**

# Requirements
You will need **Seleniun** to run it. In my case, it operates via Chrome

*All other libraries used come pre-installed with Python 3.7*

# Common Error
If you have an error for **chromedriver** you can pass the **chromedriver.exe** in my code

```
self.driver = webdriver.Chrome(\path\to\chromedriver.exe)
```

Also, you can download [chromedriver.exe](https://chromedriver.chromium.org)

