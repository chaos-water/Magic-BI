# 简介
<a href="https://github.com/chaos-water/Magic-BI/blob/main/README.md" style="color: blue; font-size: 18px;">For English, please click here.</a><br/>
Magic-BI是一款基于AI的全自动化ChatBI产品，目前支持SQL类数据库。Magic-BI是开源的，可以进行全私有化或半私有化部署，既最大限度的保护用户隐私，又降低用户使用门槛。

# 竞品对比
|          | Magic-BI                                                                                                     | 	其它Chat BI产品                                                                           |
|:---------|:-------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------|
| 数据安全     | Magic-BI可以完全使用闭源模型工作，避免内部数据或元数据泄漏。                                                                           | 部分竞品，采用闭源大模型服务，导致业务数据库的数据和元数据外泄，引入商业风险。                                                |
| 构建成本     | Magic-BI可以在用户零输入或少量输入训练数据的情况下，进行模型微调，大幅降低用户的使用成本。                                                            | 用户或供应商需要根据业务领域和数据库结构，构建训练数据（如问题-SQL对），通常在百甚至千量级，需要大量的人力和时间成本。                          |
| 易用性      | Magic-BI完整的提供了训练数据生成、模型微调和模型部署的功能，只需要在页面上进行简单的操作，即可完成训练数据生成、领域模型训练和部署，大幅降低了产品使用门槛。                           | 需要专业技术人员进行训练数据构建、基座模型选择、模型微调和模型部署，时间长、成本高，且不确定性大。                                      |
| 是否需要数据治理 | Magic-BI直接在业务数据库上工作，不需要进行数据治理和构建数仓，具有如下优势：<br/>1、不限制问题类型；<br/>2、避免了数仓的建设和部署成本；<br/>3、数据是实时的，避免因为数据陈旧而影响业务决策。 | 现有大量ChatBI产品，需要对业务数据库进行数据治理，构建数仓，对ChatBI的问题也限定在数仓库及训练数据支持的范围内。存在成本高、效果差、数据不即时和系统复杂的问题。 |
| 准确率      | Magic-BI在“微调模型模式”下工作时，准确率在95%+以上，可以进行生产部署。                                                                   | 部分竞品，为了提升准确率，采用闭源大模型服务。但是，在真实的业务系统上，通用大模型的准确率，很难达到生产可用的程度。                             |

# 工作模式
Magic-BI目前有两种工作模式：微调模型模式和智能体模式
## 智能体模式
该模式基于通用大模型+RAG+智能体的方式实现，优点是使用门槛低，缺点是准确率偏低且推理成本高。在新手模式下，推荐使用70B+的开源大模型或其它大模型云服务。
## 微调模型模式
该模式基于微调大模型+智能体的方式实现，优点是准确率高和推理成本低，缺点是需要生成训练数据和微调模型，使用门槛稍高。

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
执行命令"python3 -m magic_bi.main --config config/system.yml"来启动系统。 在浏览器中输入http://127.0.0.1:6688来访问系统。目前支持的web
浏览器主要是Chrome和Firefox。
## Restful Api
执行命令"python3 -m magic_bi.main --config config/system.yml"来启动系统。通过API工具或其它系统，来调用Magic-BI。
