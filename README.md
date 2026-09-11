# try-again

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.1.0-green.svg)](https://github.com/Loocik666/try-again)

A lightweight, zero-dependency Python decorator for automatic function retries with exponential backoff and fallback support. Works seamlessly with both **synchronous** and **asynchronous** functions.

---

## ✨ Features

- 🔄 **Automatic Retries** — Automatically re-executes functions on failure
- ⏱️ **Exponential Backoff** — Intelligently increases delay between attempts
- 🎲 **Jitter** — Randomizes delays to prevent request storms
- 🛑 **Max Delay** — Caps maximum wait time between retries
- 🛡️ **Exception Filtering** — Retry only on specific exceptions
- 🔄 **Fallback Support** — Return backup values when all attempts fail
- 📦 **Zero Dependencies** — Pure Python, no external libraries required
- ⚡ **Async Ready** — Built-in support for async/await
- 📝 **Logging** — Integrated attempt logging for debugging

---

## 📦 Installation

```bash
pip install git+https://github.com/Loocik666/try-again.git
```

---

## 🚀 Quick Start Guide

### What Does It Do?

The `@retry` decorator automatically re-runs a function if it raises an exception. This is ideal for handling unreliable APIs, network requests, or any operations that might temporarily fail.

### Basic Example

The function will attempt to execute up to 3 times with a 1-second delay between attempts:

```python
from try_again import retry

@retry(tries=3, delay=1.0)
def fetch_data():
    return requests.get("https://api.example.com/data")
```

**How It Works:**
1. First call → fails → wait 1 second
2. Second attempt → fails → wait 1 second  
3. Third attempt → success OR raise exception

---

## 📖 Comprehensive Usage Guide

### 1️⃣ Exponential Backoff

Each subsequent attempt waits longer than the previous one. Formula: `delay × (backoff ^ (attempt - 1))`

```python
from try_again import retry

@retry(tries=4, delay=1.0, backoff=2.0)
def unstable_request():
    return connect_to_service()
```

**Execution Timeline:**

| Attempt | Delay Before Attempt |
|---------|---------------------|
| 1       | 0 sec (immediate)   |
| 2       | 1 sec               |
| 3       | 2 sec (1 × 2)       |
| 4       | 4 sec (2 × 2)       |

---

### 2️⃣ Filter Specific Exceptions

Don't retry on every error — specify exactly which exceptions should trigger a retry:

```python
from try_again import retry

@retry(tries=3, delay=0.5, exceptions=(ConnectionError, TimeoutError))
def get_live_data():
    return fetch_from_remote()
```

Now `ValueError` or `KeyError` won't trigger retries — they'll propagate immediately.

---

### 3️⃣ Fallback — Plan B

When all attempts are exhausted, return a fallback value instead of raising an exception:

```python
from try_again import retry

def get_cached_data():
    return {"status": "offline", "data": []}

@retry(
    tries=3,
    delay=0.5,
    exceptions=(ConnectionError, TimeoutError),
    fallback=get_cached_data
)
def get_live_data():
    return fetch_from_remote()
```

**Outcome:**
- ✅ Success within 3 attempts → returns API data
- ❌ All 3 attempts fail → calls `get_cached_data()` and returns cached data

---

### 4️⃣ Random Jitter

Prevent "thundering herd" problems (when many clients wait the same duration) by adding randomness:

```python
from try_again import retry

@retry(tries=3, delay=1.0, jitter=0.5)
def api_call():
    return requests.get("https://api.example.com/data")
```

`jitter=0.5` means ±50% randomness:
- A 1-second delay can become **0.5 to 1.5 seconds**

---

### 5️⃣ Maximum Delay Cap

Prevent excessively long waits even with high `backoff` values:

```python
from try_again import retry

@retry(tries=5, delay=1.0, backoff=2.0, max_delay=10.0)
def slow_service():
    return connect_to_legacy_system()
```

Even if calculated delay reaches 16 seconds, actual wait will be capped at 10 seconds.

---

### 6️⃣ Logging

Attach a custom logger for debugging:

```python
import logging
from try_again import retry

logger = logging.getLogger("my_app")

@retry(tries=3, delay=1.0, logger=logger)
def flaky_operation():
    return do_something_unreliable()
```

You'll see in logs:
```
DEBUG:my_app:Attempt 1/3 failed for flaky_operation
DEBUG:my_app:Attempt 2/3 failed for flaky_operation
```

---

## ⚡ Async Support

The decorator automatically detects async functions:

```python
import asyncio
from try_again import retry

@retry(tries=3, delay=0.5)
async def fetch_async():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.example.com") as resp:
            return await resp.json()

# Usage
async def main():
    data = await fetch_async()
    print(data)

asyncio.run(main())
```

---

## 📊 Complete Parameters Table

| Parameter   | Type             | Default        | Description                                                   |
|-------------|------------------|----------------|---------------------------------------------------------------|
| `tries`     | `int`            | `3`            | Maximum number of execution attempts                          |
| `delay`     | `float`          | `1.0`          | Initial delay between attempts (in seconds)                   |
| `backoff`   | `float`          | `2.0`          | Multiplier applied to delay after each failure                |
| `exceptions`| `tuple`          | `(Exception,)` | Tuple of exception types that trigger retries                 |
| `fallback`  | `callable`       | `None`         | Function called when all attempts are exhausted               |
| `jitter`    | `float`          | `0.0`          | Random delay variation (0.0–1.0, where 1.0 = ±100%)           |
| `max_delay` | `float` or `None`| `None`         | Maximum delay cap between attempts                            |
| `logger`    | `logging.Logger` | `None`         | Logger for debug messages                                     |

---

## 🛠 Advanced Examples

### Combining All Features

```python
from try_again import retry
import logging

logger = logging.getLogger("payment_service")

def refund_fallback(user_id, amount):
    logger.warning(f"Refund queued for later: user={user_id}, amount={amount}")
    return {"status": "queued", "user_id": user_id}

@retry(
    tries=5,
    delay=0.5,
    backoff=2.0,
    max_delay=30.0,
    jitter=0.3,
    exceptions=(ConnectionError, TimeoutError, ConnectionResetError),
    fallback=refund_fallback,
    logger=logger
)
def process_payment(user_id, amount):
    return payment_gateway.charge(user_id, amount)
```

### Retry with Function Arguments

```python
from try_again import retry

@retry(tries=3, delay=1.0)
def divide(a, b):
    return a / b

# Call like a normal function
result = divide(10, 2)  # OK
result = divide(10, 0)  # Tries 3 times, then raises ZeroDivisionError
```

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License — feel free to use in your projects.

---

## 👨‍💻 Author

**Alexander Romanuk**  
GitHub: [@Loocik666](https://github.com/Loocik666)

---

**💡 Tip:** If you like this library, give it a ⭐️ on GitHub!
