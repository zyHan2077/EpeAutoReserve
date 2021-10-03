## 反爬机制

### Login 阶段

- 拿到IAAA token
- 用IAAA token请求体质健康网站ggtypt/dologin，该网站将向cookie写入sso_pku_token
- 向智慧场馆 venue-server/api/login 携带 sso_pku_token 请求，返回json中包含cgAuthorization字段
- 用上一步的 cgAuthorization 加上个人身份，请求智慧场馆 venue-server/roleLogin，返回最终的cgAuthorization，此为查询场地、预订所需的身份证明。

### sign 验证

智慧场馆使用额外的sign防止爬虫，例如查询场地阶段需要url参数：

```
params = {
    venueSiteId: 60
    searchDate: 2021-10-01
    nocache: 1xxxxxxxxxxxxxx  # 时间戳 
}
```

则

```
sign = MD5(S + 当前路径（/api/reservation/day/info）+ params 按字典序排列 + 时间戳 + “ ” + S)
```

其中有magic number S，**为防止爬虫滥用，本程序中填入了错误的字符串S，会导致401 Unauthorized错误，请填入正确的S后使用**

## 使用方法
config.sample.ini中填入个人信息、参数设置，修改文件名为config.ini后，python运行main.py

## Known Issues
- 命令行使用SOCKS代理可能会造成问题，HTTP/HTTPS则无问题（不确定原因）

## 声明

本脚本为喜欢运动、约不上场、且懂点儿技术的同学节省一点儿开发时间，希望各位用户在可控范围内传播，避免爬虫内卷，☆⌒(*＾-゜)v THX!!