# bgstats-wrapped

A data visualisation for bgstats data. Idea by [Talita James](https://www.github.com/TalitaJames)

## How to generate your own visual 

install the requirements with

```pip install -r requirements.txt```

Make sure you have a copy of the json data supplied from bgstats

then run: 

Linux: 

```python3 gen_wrap.py```

Windows:

```python gen_wrap.py```

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

the path the wrapped image will be output to, default is ./wrapped\<year\>.png

