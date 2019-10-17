# Naive Bili Pn Hash

A sub project of TianDian Daily which build local aid-tid-pubdate cache and provide pn value of 'awesome' api to get video info. 

[中文介绍](README_zh-cn.md)

## Introduction

In order to get archive info of bilibili video, we may use 'view' api(https://api.bilibili.com/x/web-interface/view?aid=456930) or 'stat' api(https://api.bilibili.com/x/web-interface/archive/stat?aid=456930). However, both api have call limitation and if keep calling them at high speed, your IP will be banned for hours. 

Conversely, 'awesome' api(https://api.bilibili.com/archive_rank/getarchiverankbypartion?jsonp=jsonp&tid=30&pn=1&ps=50) will not ban ip. This api get three params.

- tid: type id
- pn: page num
- ps: page size (max = 50)

With given tid, api will return all the video info belong to that type, order by pubtime('create' field in this api, which actually means publish time) desc. One page will show ps(max = 50) video info and by adding pn value, we can get all video info in this category.

If we could know the tid and pn value in which page aid appears, we can the video info of that aid. Apparently, pn depends on the number of video which published later than the video we query. If we cache all video belongs to this category, building local aid-tid-pubdate cache, we can quickly get tid and pn value and find what we want. This cache is what we do in this programe.

## Installation

### 01 Download program file

```
git clone https://github.com/bunnyxt/naive-bili-pn-hash
```

### 02 Set up environment

You need Python 3.5+ to run this program. We strongly suggest use virtualenv or anaconda to manage your virtual python environment! For example, if you use virtualenv, you can set up your virtual environment and install requirements like this.

```shell
virtualenv venv  # set up new virtual environment
source venv/bin/activate  # enable virtual environment
pip install -r requirements.txt  # install requirements
```

###  03 Edit config file

Open `conf/conf.ini` file, fill in your db connection info. 

```ini
[db_mysql]
user = root
password = root
host = localhost
port = 3306
dbname = nbph
```

By default, this program use MySQL and you can change it to any other database by yourself. 

## Usage

- For the first time use, run `00_create-db.py` to create table in db.

```shell
python 00_create-db.py
```

- Then, run `01_init-via-tid.py` to cache all video with specific tid given. You need to assign a valid tid param. For example, to cache video with tid 30, just enter: 

```shell
python 01_init-via-tid.py 30
```

- After that, run `02_routine-update-via-tid.py` to routine update new video with specific tid given. You need to assign a valid tid param. For example, to routine update new video with tid 30, just enter: 

```shell
python 02_routine-update-via-tid.py 30
```

- By default, 02 update new video per 10 minutes. To run routine update programme background on Linux, use `nohup` like this:

```shell
nohup python -u 02_routine-update-via-tid.py 30 > sh02.out 2>&1 &
```

## Calculate pn

In order to get pn with given aid, firstly just count video numbers which have the same tid with given aid and created later than or equal to the given aid. 

```SQL
/* 01 query row with given [aid] */
select * from nbph.video where aid = [aid];
/* get [tid] and [create] */

/* 02 count num */
select count(*) from nbph.video where tid = [tid] && `create` >= [create];
/* get [count] */
```

Then, the ceiling of count number div 50 is the pn we need.

```python
pn = math.ceil(count / 50)
```

You can use `get_pn(aid, session)` function to get pn via aid and test it via `test_pn(aid, tid, pn)` function. You can see the usage of them in `test.py` file.

```python
from db import Session
from nbph import *

if __name__ == '__main__':
    # get db session
    session = Session()

    # get pn via aid
    aid = 456930
    pn = get_pn(aid, session)
    print('aid = %d, pn = %d' % (aid, pn))

    # test pn
    index = test_pn(aid, 30, pn)
    if index == -1:
        print('test fail! aid = %d not in pn = %d!' % (aid, pn))
    else:
        print('test success! aid = %d in pn = %d with index %d!' % (aid, pn, index))
```

## Online demo

URL: [http://api.bunnyxt.com/nbph/nbph.php?aid=456930](http://api.bunnyxt.com/nbph/nbph.php?aid=456930)

Given aid via 'GET' method, it will return tid and pn value in json format.

```json
{
  "aid": 456930,
  "tid": 30,
  "pn": 3728
}
```

If any of them return `-1`, it means that cannot found that aid. **Notice**: This online demo only cache videos with tid 30!

Code of this naive api also included in this repo. See it here: [webapi/nbph.php](webapi/nbph.php)

## TODO

- Use logging module to manage log.
- Add script to delete invalid aid cached locally.
- Optimize SQL to improve performance.

Issues are welcome!

## About

All by [bunnyxt](https://www.bunnyxt.com)

Discussion QQ group: [537793686](https://jq.qq.com/?_wv=1027&k=588s7nw)

**DO NOT ABUSE BILIBILI API!!!**
