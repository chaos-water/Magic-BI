# Introduction
<a href="https://github.com/chaos-water/Magic-BI/blob/main/README_zh.md" style="color: blue; font-size: 18px;">中文请点这里</a><br/>
# Introduction
Magic-BI is an AI-based fully automated ChatBI product that currently supports SQL databases. Magic-BI is open-source and can be deployed in a fully private or semi-private manner, which maximizes user privacy protection while lowering 
the usage threshold.

# Competitor Comparison
|          | Magic-BI                                                                                                     |         Other Chat BI Products                                                                           |
|:---------|:-------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------|
| Data Security     | Magic-BI can operate entirely using a closed-source model, preventing internal data or metadata leakage.                                                                           | Some competitors use closed-source 
large models, which can lead to data and metadata leakage from business databases, introducing commercial risks.                                                |
| Build Cost     | Magic-BI can fine-tune the model with zero or minimal user input training data, significantly reducing usage costs.                                                            | Users or vendors need to build training 
data (such as question-SQL pairs) based on the business domain and database structure, typically in the hundreds or thousands, requiring substantial human and time resources.                          |
| Ease of Use      | Magic-BI provides complete functionality for training data generation, model fine-tuning, and deployment, allowing users to perform these tasks with simple page operations, significantly lowering the product usage 
threshold.                           | Professional technical personnel are required to build training data, select base models, fine-tune models, and deploy them, which is time-consuming, costly, and uncertain.                           
           |
| Data Governance Required | Magic-BI works directly on business databases without requiring data governance or data warehouse construction, offering the following advantages:<br/>1. No restrictions on question types;<br/>2. Avoids the 
need for data warehouse construction;<br/>3. Suitable for production deployment. | Some competitors use closed-source large models to improve accuracy. However, in real business systems, the accuracy of general-purpose large models is 
often insufficient for production use.                             |

# Operating Modes
Magic-BI currently supports two operating modes: Fine-Tuned Model Mode and Agent Mode.
## Agent Mode
This mode is implemented using a general-purpose large model + RAG (Retrieval-Augmented Generation) + agent approach. The advantage is low usage threshold, but the disadvantage is lower accuracy and higher inference cost. For beginners, 
it is recommended to use open-source large models of 70B+ or other large model cloud services.
## Fine-Tuned Model Mode
This mode is implemented using a fine-tuned large model + agent approach. The advantage is high accuracy and low inference cost, but the disadvantage is that it requires generating training data and fine-tuning the model, which slightly 
increases the usage threshold.

# Runtime Environment
Magic-BI can run on Ubuntu 22.04, RTX 4090, CUDA 12+, and PyTorch 2.0+. Other environments have not been rigorously tested, but similar environments should also work.
If you encounter any issues while using Magic-BI, you can contact us through the following contact information.

# Installation
Magic-BI supports three installation methods: pip installation, Docker deployment, and source code compilation. We recommend using the Docker deployment method.
## Pip Installation
Install the PostgreSQL development library:
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
Execute the following command to complete the installation of Magic-BI:
```
pip install magic-bi
```
## Docker Deployment
To deploy using Docker, you need to install Docker on your system and enable GPU support for Docker. The specific operations are not covered here.
Execute the following two commands to start Magic-BI and its related dependencies:
1. `cd $Magic-BI;`
2. `docker compose -f deployment/docker-compose.yml up -d.`

## Source Code Compilation
### Magic-BI
Enter the Magic-BI directory and execute the command `pip3 install -e .`

### Dependencies
Execute the following two commands to start the dependencies for Magic-BI:
1. `cd $Magic-BI;`
2. `docker compose -f deployment/docker-compose.yml up -d.`
3. `docker compose -f deployment/docker-compose-component.yml up -d.`

# Client
Magic-BI supports two types of clients: WEB GUI and Restful API. If you want to use Magic-BI directly, access it through the web interface. If you want to integrate Magic-BI into your system or use specific functionalities, access it via 
the Restful API.
## WEB GUI
Execute the command `python3 -m magic_bi.main --config config/system.yml` to start the system. Enter `http://127.0.0.1:6688` in a web browser (currently supported browsers are Chrome and Firefox) to access the system.
## Restful API
Execute the command `python3 -m magic_bi.main --config config/system.yml` to start the system. Use an API tool or another system to call Magic-BI.