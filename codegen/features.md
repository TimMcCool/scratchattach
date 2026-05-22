# Features

The features supported by the codegen module are as follows:

## Automatic formatting

Codegen automatically formats result files using ruff. This cannot currently be disabled.

## Dynamic checking

You can declare a variable `IS_ASYNC` like so (recommended to be in global scope):

```python
IS_ASYNC = True
```

It will be `True` in the async code and `False` in the sync code. This can be used to check dynamically where you currently are.

More specifically, any assignment of `IS_ASYNC` will be left as is in the async code and will be changed to assign `False` in the sync code.

## Static checking

### `"IS_ASYNC"`

If you use exactly `"IS_ASYNC"` as a condition (and nothing else) in an if, if else or if elif else statement, only paths with it being true will be included in the async code and only paths with it being false will be included in the sync code.

Example:

```python
if "IS_ASYNC":
    async_implementation()
else:
    sync_implementation()
```

Codegen will turn this into (respectively async and sync):

```python
async_implementation()
```
and
```python
sync_implementation()
```

### `"IS_PRE_CODEGEN"`

If you use exactly `"IS_PRE_CODEGEN"` as a condition (and nothing else) in an if, if else or if elif else statement, only paths with it being false will be included in the async and sync code. The purpose of this feature is to allow you to satisfy static code analysis without bloating the resulting code.

Example:

```python
if "IS_PRE_CODEGEN":
    import requests
    import aiohttp
else:
    if "IS_ASYNC":
        import aiohttp
    else:
        import requests
```

Codegen will turn this into (respectively async and sync):

```python
import aiohttp
```
and
```python
import requests
```

## Comment inclusion

Because the first pass of the codegen module will create an ast from the code, all comments in the original code will be removed. If you need comments, exempli gratia for explicitly ignoring type errors, you will need one of these.

### `COMMENT`

If you call a function `COMMENT` with exactly one argument that is a simple literal string, it will expand into a line comment.

Example:

```python
if "IS_PRE_CODEGEN":
    from typing import LiteralString

    def COMMENT(msg: LiteralString) -> None: ...

COMMENT("Hello there!")
```

Codegen will turn this into:

```python
# Hello there!
```

### `PREV_LINE_COMMENT`

`COMMENT` will likely not satisfy your needs. If you call a function `PREV_LINE_COMMENT` with exactly one argument that is a simple literal string, it will expand into a line comment that is located at the end of the previous statement.

Example:

```python
if "IS_PRE_CODEGEN":
    from typing import LiteralString

    def PREV_LINE_COMMENT(msg: LiteralString) -> None: ...

def func():
    PREV_LINE_COMMENT("typing: ignore")
    pass
```

Codegen will turn this into:

```python
def func():  # typing: ignore
    pass
```
