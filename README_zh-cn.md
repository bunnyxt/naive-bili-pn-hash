# 朴素比利劈恩哈希

天钿Daily的一个子项目，用来创建本地aid-tid-pubdate缓存，提供pn值以调用"无敌"api获取视频信息。

[English Version](README.md)

## 介绍

为了获取哔哩哔哩视频的档案信息，通常使用"view"api(https://api.bilibili.com/x/web-interface/view?aid=456930) 或者"stat"api(https://api.bilibili.com/x/web-interface/archive/stat?aid=456930) 。然而，这两个api都会限制访问频率。如果访问频率过高，IP将会被锁定若干小时。

相反，"无敌"api(https://api.bilibili.com/archive_rank/getarchiverankbypartion?jsonp=jsonp&tid=30&pn=1&ps=50) 不会锁IP。这个api接收三个参数：

- tid: 类型id
- pn: 页码
- ps: 每一页显示数量（最大50）

根据给定的tid，api会返回该类型下的所有视频信息，按照发布时间（api中的create字段）逆序排列，一页显示ps个视频信息（ps最大为50）。通过递增pn数值，我们可以获得该类别下的所有视频信息。

如果我们可以知道我们需要获得信息的视频在"无敌"api中出现的位置，即aid号对应的tid与pn（为了一页获取最多的数据，通常ps默认取50），我们就可以直接访问"无敌"api获取信息。显然，pn取决于所有同类的且发布时间更晚的视频个数。因此，如果我们本地缓存一份aid-tid-pubdate的表，即可快速计算视频个数，进而计算出pn的值，访问"无敌"api获取需要的信息。该缓存即为项目实现的内容。

## 安装

### 01 下载项目代码

```
git clone https://github.com/bunnyxt/naive-bili-pn-hash
```

### 02 安装环境

本项目需要Python 3.5+并且强烈建议使用virtualenv或anaconda进行虚拟环境管理。例如，使用virtualenv安装虚拟环境并且安装依赖的方式如下：

```shell
virtualenv venv  # 创建新的虚拟环境
source venv/bin/activate  # 激活环境
pip install -r requirements.txt  # 安装依赖
```

###  03 编辑配置文件

打开`conf/conf.ini`文件，填入数据库连接信息。

```ini
[db_mysql]
user = root
password = root
host = localhost
port = 3306
dbname = nbph
```

本项目默认使用MySQL数据库。用户可以根据需要修改源码更改为自己所需要的数据库。

## 使用方式

- 初次使用，执行`00_create-db.py`以创建数据库表格。

```shell
python 00_create-db.py
```

- 之后，执行`01_init-via-tid.py`以初次缓存某类型下所有视频。需要作为参数指定类型tid，例如需要初始化缓存tid为30的视频，执行：

```shell
python 01_init-via-tid.py 30
```

- 再然后，执行`02_routine-update-via-tid.py`以定期更新添加某类型下的新视频。需要作为参数指定类型tid，例如需要定期更新添加类型30下的新视频，执行：

```shell
python 02_routine-update-via-tid.py 30
```

- 默认每10分钟更新一次。在Linux系统下，可以使用`nohup`指令将程序放置在后台运行，执行：

```shell
nohup python -u 02_routine-update-via-tid.py 30 > sh02.out 2>&1 &
```

## 计算pn

首先，根据aid获取其tid和create值。之后，计算同属于该类的create值大于等于该视频的create值的视频个数。

```SQL
/* 01 通过给定的[aid] */
select * from nbph.video where aid = [aid];
/* 获得[tid]和[create] */

/* 02 计算数量 */
select count(*) from nbph.video where tid = [tid] && `create` >= [create];
/* 获得[count] */
```

之后，计算大于等于count值除以50的最小整数，即为pn。

```python
pn = math.ceil(count / 50)
```

可以使用`get_pn(aid, session)`函数根据给定的aid获取pn，使用`test_pn(aid, tid, pn)`函数进行测试。示例代码参考`test.py`。

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

## 在线示例

URL: [http://api.bunnyxt.com/nbph/nbph.php?aid=456930](http://api.bunnyxt.com/nbph/nbph.php?aid=456930)

通过GET方法给出aid，api以json格式返回tid与pn。

```json
{
  "aid": 456930,
  "tid": 30,
  "pn": 3728
}
```

如果某字段返回`-1`，说明并没有找到该aid的缓存。**注意**，这个在线示例只缓存了tid为30的视频！

此API程序的代码同样包含在本项目中，请参考[webapi/nbph.php](webapi/nbph.php)

## TODO

- 使用logging模块管理日志。
- 添加自动删除失效视频的脚本。
- 优化SQL语句，提高系统效率。

欢迎提issue！

## 关于

制作：[bunnyxt](https://www.bunnyxt.com)

QQ群: [537793686](https://jq.qq.com/?_wv=1027&k=588s7nw)

**禁止滥用BILIBILI API！！！**
