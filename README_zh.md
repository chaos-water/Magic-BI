把下边的内容翻译成英文：

# 简介
Magic-BI是一款基于AI的全自动化Data Agent产品，支持SQL/NO-SQL数据库、文本、图片和业务系统。Magic-BI是开源的，可以进行全私有化或半私有化部署，既最大限度的保护用户隐私，又降低用户使用门槛。
目前支持的数据类型包括：SQL数据库、文本、图片和业务系统。

# 竞品对比
|          |                                Magic-BI                                 |                                                                                     	其它Chat BI产品 |
| :---        |    :---   |          :--- |
| 是否上手即用   |                 Magic-BI在探索者模式下，自主学习数据库结构库，完成学习后，即可使用。                  |                            需要进行下列一个或多个操作:<br/>1、由专业技术人员进行数据治理；<br/>2、由业务同事和技术人员针对数据库编写问题和对应的SQL。 |
| 是否限定问题范围 | Magic-BI在自主学习数据库结构后，不限定用户问题范围；同时，Magic-BI也支持用户编写问题和对应SQL，对这类问题的回答，会更精准。 |                                                       现有Chat BI产品通常将问题限定在数据治理支持的范围内或与已编写问题类似的问题。 |
| 支持的数据类型  | Magic-BI支持SQL数据库、NO-SQL数据库、文本、图片和业务系统，用户可以单独与某类数据对话，也可以同时与多类或全部类别数据对话。  |  现有Chat BI产品，大部分只支持SQL和NO SQL数据库。如果要支持文档，就要再部署RAG类的知识库系统。不仅增加了成本和复杂度，还导致了系统的割裂，用户无法同时从其全部数据获得见解。 |

## SQL数据库
对于SQL类型数据，Magic-BI支持3种模式：新手模式、专家模式、探索者模式。
### 智能体模式
新手模式基于通用大模型+RAG+智能体的方式实现，优点是使用门槛低，缺点是准确率偏低且推理成本高，不论是本地大模型还是。在新手模式下，推荐使用70B+的开源大模型或其它大模型云服务。
### 微调模型模式
专家模式基于微调大模型+智能体的方式实现，优点是准确率高和推理成本低，缺点是需要进行模型微调，使用门槛稍高，有模型微调成本。在专家模式下，推荐使用8B+的开源模型进行微调。
### 探索者模式
在探索者模模式下，Magic-BI将自动学习对应的数据库的结构和特点。学习结果，既可以用于新手模式，也可以用于探索者模式。在探索者模式下，推荐使用70B+的开源大模型或其它大模型云服务。
## 文本
对于文本类型数据，Magic-BI采用通用大模型+RAG的模式。
## 图片
对于图片类型数据，采用多模态RAG的方式技术解析并提供对话服务。
## 业务系统
对于业务系统，采用Agent的技术理解业务系统能力，使用户可以通过对话的方式与业务系统交互，避免WEB页面的繁琐操作。

针对上诉数据类型，用户既单独与某一类数据对话，也可以与多个类别数据同时对话。
# 运行环境
Magic-BI可以在ubuntu22.04、rtx4090、cuda12+和pytorch2.0+上运行。其它环境未经过严格测试，但类似的环境，应该也可以运行。
如果你在使用Magic-BI的过程中遇到任何问题，可以通过下边的联系方式联系我们。

# 安装
Magic-BI支持三种安装方式：pip安装、docker部署和源码编译，建议选用docker方式部署。
## pip安装
安装postgrel开发库
### Ubuntu/Debian
```
sudo apt-get update
sudo apt-get install libpq-dev
```
### CentOS/Fedora/RHEL
```
sudo yum install postgresql-devel
```
### macOS
```
brew install postgresql
```
执行如下命令完成Magic-BI的安装。
```
pip install magic-bi
```
## docker部署
通过docker方式部署，需要在系统上安装docker，并开启docker的显卡支持。相关操作本文不包含，自行解决。
执行如下2个命令，完成magic-bi及相关依赖工具的启动。
1、cd $Magic-BI;<br />
2、docker compose -f deployment/docker-compose.yml up -d.<br />

## 源码编译
### Magic-BI
进入Magic-BI目录，执行pip3 install -e .命令

### 依赖工具
执行如下2个命令，完成magic-bi相关依赖工具的启动。
1、cd $Magic-BI;<br />
2、docker compose -f deployment/docker-compose.yml up -d.<br />
docker compose -f deployment/docker-compose-component.yml up -d

# 客户端
Magic-BI 支持两种类型的客户端：WEB GUI和 Restful API。如果你想直接使用Magic-BI，那么就通过WEB页面访问；如果你想将Magic-BI融入你的系统或
只使用部分功能，那么就通过Restful API访问。
## WEB GUI
执行命令"python3 -m magic_bi.main --config config/magic_bi.yml"来启动系统。 在浏览器中输入http://$url:6688来访问系统。目前支持的web
浏览器主要是Chrome和Firefox。
## Restful Api
执行命令"python3 -m magic_bi.main --config config/magic_bi.yml"来启动系统。通过API工具或其它系统，来调用Magic-BI。API文档请见xxx。

# 模型
## 大模型
目前主要通过Openai API兼容的方式采用大模型（语言和多模态），支持通用模型和微调模型。文本、图片和业务系统目前仍采用通用大模型；对于SQL数据库，
微调模型的效果要比通用大模型的效果好。

对应的base_url、model和api_key在config/magic_bi.yml中配置。
### 通用大模型
文本、图片和业务系统目前仍采用通用大模型；对于SQL数据库，采用通用大模型时，Magic-BI主要以RAG的方式提供Chat-BI服务。
#### 本地大模型
本地大模型可以通过ollama或vllm进行部署，以openai api兼容的方式对外提供服务。
#### 大模型服务
几乎所有的大模型服务，都会通过Openai API的方式提供服务。
### 微调大模型
微调大模型，目前主要针对SQL数据库。模型的微调方式详见xxx。

# 辅助数据
辅助数据，主要用于提升Magic-BI响应用户的效果。分为RAG和微调两种形式。
## RAG数据
RAG数据由用户向Magic-BI添加，用于辅助提升Magic-BI的响应效果。具体添加办法，请参考xxx。
RAG数据
## 微调数据
微调数据用来对语言模型进行微调，提升Magic-BI的响应效果。微调数据的生成及模型的微调办法，请参考xxx。

