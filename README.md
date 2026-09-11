# **try-again**

Lightweight, zero-dependency Python decorator for automatic function retries with exponential backoff and fallbacks.

## **Installation**

pip install git+https://github.com/Loocik666/try-again.git

## **Quick Start**

### **Basic Usage**

Retries the function up to 3 times with a 1-second delay if an exception occurs:  
from try\_again import retry

@retry(tries=3, delay=1.0)  
def fetch\_data():  
    return requests.get("https://api.example.com/data")

### **Exponential Backoff**

Increases the delay multiplier after each failed attempt (1s \-\> 2s \-\> 4s):  
from try\_again import retry

@retry(tries=4, delay=1.0, backoff=2.0)  
def unstable\_request():  
    return connect\_to\_service()  
\#\#\# Fallback & Specific Exceptions  
Catch specific errors and return a safe fallback value if all retries fail:  
from try\_again import retry

def get\_cached\_data():  
    return {"status": "offline", "data": \[\]}

@retry(  
    tries=3,  
    delay=0.5,  
    exceptions=(ConnectionError, TimeoutError),  
    fallback=get\_cached\_data  
)  
def get\_live\_data():  
    return fetch\_from\_remote()

## **Parameters**

| Parameter | Type | Default | Description   |
| :---- | :---- | :---- | :---- |
| tries | int | 3 | Maximum execution attempts |
| delay | float | 1.0 | Initial delay between attempts (seconds) |
| backoff | float | 2.0 | Delay multiplier applied after each failed attempt |
| exceptions | tuple | (Exception,) | Exceptions that trigger a retry |
| fallback | callable | None | Backup function called when all attempts fail |

## **License**

MIT