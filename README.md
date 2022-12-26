# bgstats-wrapped

A data visualisation for [BG Stats](https://www.bgstatsapp.com/) data. Idea by [Talita James](https://www.github.com/TalitaJames)

## How to generate your own visual 

Run:  
```
git clone git@github.com:sqrtxander/bgstats-wrapped
```

cd into the directory you cloned it into
```
cd bgstats-wrapped
```

install the requirements with  

```
pip install -r requirements.txt
```

Make sure you have a copy of the json data supplied from bgstats then run: 

```
python gen_wrap.py
```

## Optional Arguments
| Argument                      | Use                                                                                                     | Default Value                    |
|-------------------------------|---------------------------------------------------------------------------------------------------------|----------------------------------|
| `-n`, `--new`                 | Use this flag if you have recently updated the data file otherwise it will continue to use the old data | False                            |
| `-y <year>`, `--year <year>`  | Specifies the year you want to data you want to generate the wrapped from. Leave out for all time.      | All Time                         |
| `-p <path>`, `--path <path>`  | The path to your BGStats json file                                                                      | `"./BGStatsExport.json"`         |
| `-o <path>` `--output <path>` | The path of the directory the wrapped images will be output to                                          |`"./wrapped<year>/"` |

