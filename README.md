# bgstats-wrapped

A data visualisation for bgstats data

## How to generate your own visual 

install the requirements with

```pip install -r requirements.txt```

then run: 

Linux: 

```python3 main.py```

Windows:

```python main.py```

## Optional arguments
```-n```

```--new```

use this flag if you have recently updated the data file otherwise it will continue to use the old data

```-y <year>```

```-year <year>```

the year for the data you want to generate the wrapped from, default is the current year

```-p <path>```

```--path <path>```

The path to your bgstats json file, default is ./BGStatsExport.json

```-o <path>```

```-output <path>```

the path the wrapped image will be output to, default is ./wrapped\<year\>

