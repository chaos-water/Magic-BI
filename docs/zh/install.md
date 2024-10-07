# 组件
## 已支持组件
执行docker compose -f deployment/docker-compose-components.yml up -d来启动Magic-BI依赖的所有组件。如果拉取镜像有问题，可以在
/etc/docker/daemon.json中添加如下docker代理
```
{
    "registry-mirrors": [
        "https://dockerpull.com",
        "https://docker.anyhub.us.kg",
        "https://dockerhub.jobcher.com",
        "https://dockerhub.icu",
        "https://docker.awsl9527.cn"
    ]
}
```
## 新增组件
如果用户替换部分组件的需求，可以自行替换并自行对应代码，或在社区中提出需求。
# 模型

# Magic-BI
通过pip或编译源码安装时，部分依赖组件可能需要较长时间下载和安装，请耐心等待。
## install by pip
sudo apt install -y gcc 
执行pip install magic-bi
## compile from source


# install by docker
执行docker compose -f deployment/docker-compsoe-magic-bi.yml up -d来启动Magic-BI。如果拉去镜像有问题，请参照上边的信息，
添加docker代理。