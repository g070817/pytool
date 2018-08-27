# -*- encoding:utf-8 -*-

# 分析某个网页，获取网页内链接列表，然后下载该链接指向页面里面的pdf文档
# 现在urllib中 urlopen已经不需要request了，

import urllib

import re, os, sys


# 设置运行编码环境
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')


# 获取指定页面内容，并返回该内容
def getHtml(url):
    page = urllib.urlopen(url)
    html = page.read()
    page.close()
    return html


# 根据公司页面内容，用正则表达式分析并获取页面指定类型链接地址 （这里获取的是pdf类型的文件下载地址）
def getDownloadUrl(html):

    # 匹配pdf链接
    url_reg = r'(?:href|HREF)="?((?:http://)?.+?\.pdf)'

    url_re = re.compile(url_reg)
    url = url_re.findall(html.decode('utf-8'))[0]
    return url


# 根据公司列表页面内容，用正则表达式分析并获取全部公司介绍页面链接
def getCopUrl(html):

    cop_urls = []

    # 匹配链接格式，此处为相对路径，需在面的for循环中重新组合为完整页面链接
    cop_reg = r'v-\d+-\d+-\d+.html'
    cop_re = re.compile(cop_reg)
    cop_url = cop_re.findall(html.decode('utf-8'))

    # 组合为完整链接
    for i in cop_url[:]:
        # cop_url = '此处要替换为完整url的前半部分' + i
        cop_url = 'http://xxxxxxxx.com/' + i

        cop_urls.append(cop_url)
    return cop_urls

# 获取公司标题，用于存储pdf文件，原链接是由首字母进行命名
def getTitle(html):
    # 匹配公司标题
    title_reg = r'(?:headline)">(.*?)<'
    title_re = re.compile(title_reg)
    title = title_re.findall(html.decode('utf-8'))[0]
    return title

# 获取公司页面组别
def getGroupName(html):

    # 获取所属组别，获取的html中多了个空格，所以这里匹配也多一个空格，否则匹配不到
    group_reg = '="/(.*?)/" >(.*?)<'
    group_re = re.compile(group_reg)
    group = group_re.findall(html.decode('utf-8'))
    group_name = ''

    # 由于发现获取组别的表达式会获取到其它信息，根据分析每个页面均包含该信息，但只有长度大于3的，才是真正的组名
    try:
        for i in group[:]:
            if i[0].__len__() > 3:
                group_name = i[1]
    except Exception as e:
        print e, len(group)

    # 将获取的组别中的 '/' 替换为'-'，防止按类别创建文件夹时出错
    group_name = re.sub('/', '-', group_name)
    return group_name

# 获取公司组别、公司名称、下载链接，并返回该数据
def getDownloadInfo(html):

    url = getDownloadUrl(html)
    title = getTitle(html)
    group_name = getGroupName(html).encode('utf-8')

    return url, title, group_name

# 进行文件下载方法1
def getFile(url, title, group_name):

    # 进行文件下载，需捕捉异常，发现其中又一个链接http协议不完整（页面上只有ttp，丢了'h'），导致无法进行下载
    try:
        u = urllib.urlopen(url)
    except Exception as e:
        print 'Error info: ', e

    # 文件写入本地进行存储
    try:
        f = open(unicode(title)+'.pdf', 'wb')

        # 每次取8192个字节，反复写入文件
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break
            f.write(buffer)
        f.close()

        print 'Success to download: ' + group_name + ' ' + title + '.pdf'
    except Exception as e:
        print e

# 文件下载方法2
def getFile2(url, title, group_name):

    # 进行文件下载，需捕捉异常，发现其中又一个链接http协议不完整（页面上只有ttp，丢了'h'），导致无法进行下载
    try:
        u = urllib.urlopen(url)
        data = u.read()
    except Exception as e:
        print e

    # 另一种方法进行文件存储到本地
    try:
        with open(unicode(title) + '.pdf', 'wb') as f:
            f.write(data)
            print 'Success to download: ' + group_name + ' ' + title + '.pdf'
    except Exception as e:
        print e

# 记录下载总数
count_cop = 0

# 执行下载过程，该否循环为页面的页数，因为目标页面链接列表并不是完全在一页上面，所以需要按页面获取链接，然后进入链接后下载目标pdf文档
for i in range(33, 34):

    # 打印所属页面
    print i

    # 组合当前页面链接，获取该页面下的全部链接内容
    list_url = 'http://xxxxxxxxxxx.com/dlb/list_'+ str(i) + '.html'

    # 获取当前列表页面的内容
    page = getHtml(list_url)

    # 根据获取的页面内容，分析并获得该页面上全部公司链接
    cop_urls = getCopUrl(page)

    # 循环当前页面获得的全部公司链接，并分析页面内容后，获得公司分组，公司名称，下载链接，并完成下载后，存储到本地目录，完成后返回工作目录。
    for cop_url in cop_urls:

        html = getHtml(cop_url)

        url, title, group_name = getDownloadInfo(html)

        # 需先进行判断按公司分组命名的目录是否存在，如果存在则进入该目录，否则创建该组别的文件目录，后续下载文件会保存到该目录
        if os.path.exists(group_name):
            os.chdir(os.path.join(os.getcwd(), group_name))
        else:
            os.mkdir(group_name)
            os.chdir(os.path.join(os.getcwd(), group_name))

        #下载文件并保存
        getFile2(url, title, group_name)
        count_cop += 1

        # 下载完成后将文件保存到组别下的路径后，需要返回上一级目录，这里简单通过获取当前目录，并取当前目录所属的文件夹来实现
        os.chdir(os.path.dirname(os.getcwd()))
