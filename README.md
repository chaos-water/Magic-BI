# Introduction
Magic-BI is an AI-based fully automated Data Agent product that supports SQL/NoSQL databases, text, images, and business systems. Magic-BI is open-source and can be deployed in a fully private or semi-private environment, which maximizes 
user privacy protection while lowering the usage threshold for users.
Currently supported data types include: SQL databases, text, images, and business systems.

# Competitor Comparison
|           |                                Magic-BI                                 |                                                                                             Other Chat BI Products |
| :---        |    :---   |          :--- |
| Ease of Use  | In Explorer mode, Magic-BI autonomously learns the database structure, and after learning is complete, it can be used immediately. | Requires one or more of the following operations:<br/>1. Data governance by 
professionals;<br/>2. Business colleagues and technical personnel write questions and corresponding SQL queries for the database. |
| Question Scope Limitation | After autonomously learning the database structure, Magic-BI does not limit the scope of user questions; simultaneously, Magic-BI supports users writing questions and corresponding SQL queries, providing 
more accurate answers to such questions. | Existing Chat BI products typically restrict questions within the scope supported by data governance or similar to pre-written questions. |
| Supported Data Types  | Magic-BI supports SQL databases, NoSQL databases, text, images, and business systems. Users can interact with a single type of data individually or simultaneously with multiple types or all categories of data. | 
Most existing Chat BI products only support SQL and NoSQL databases. To support documents, an additional RAG (Retrieval-Augmented Generation) knowledge base system needs to be deployed. This increases costs and complexity, leading to 
fragmented systems where users cannot gain insights from all their data simultaneously. |

## SQL Databases
For SQL type data, Magic-BI supports three modes: Beginner Mode, Expert Mode, and Explorer Mode.
### Agent Mode
Beginner Mode is implemented using a general large model + RAG (Retrieval-Augmented Generation) + agent approach. The advantage is low usage threshold, but the disadvantage is lower accuracy and higher inference cost, whether using local 
large models or cloud services for large models. In Beginner Mode, it is recommended to use an open-source large model of 70B+ parameters or other large model cloud services.
### Fine-Tuned Model Mode
Expert Mode is implemented using a fine-tuned large model + agent approach. The advantage is higher accuracy and lower inference cost, but the disadvantage is the need for initial training data. For SQL databases, Expert Mode generally 
outperforms Beginner Mode. In Expert Mode, it is recommended to use an open-source large model of 70B+ parameters or other large model cloud services.
### Explorer Mode
Explorer Mode is implemented using a general large model + RAG (Retrieval-Augmented Generation) + agent approach. This mode is designed for exploratory data analysis and can provide more flexible query capabilities.

## Text, Images, and Business Systems
For text, images, and business systems, Magic-BI currently uses general large models to provide services. The base_url, model, and api_key are configured in `config/magic_bi.yml`.

# Auxiliary Data
Auxiliary data is primarily used to enhance the effectiveness of Magic-BI's responses to user queries. It can be divided into RAG (Retrieval-Augmented Generation) and fine-tuning forms.
## RAG Data
RAG data is added by users to assist in enhancing Magic-BI's response effectiveness. The specific addition methods are detailed in `xxx`.
## Fine-Tuning Data
Fine-tuning data is used to fine-tune language models, thereby improving Magic-BI's response effectiveness. The generation of fine-tuning data and the methods for model fine-tuning are detailed in `xxx`.

# Client
Magic-BI supports two types of clients: WEB GUI and Restful API. If you want to use Magic-BI directly, access it through the web page; if you want to integrate Magic-BI into your system or use only part of its functionality, access it 
via Restful API.
## WEB GUI
Run the command `python3 -m magic_bi.main --config config/magic_bi.yml` to start the system. Enter `http://$url:6688` in a browser to access the system. Currently supported web browsers are mainly Chrome and Firefox.
## Restful API
Run the command `python3 -m magic_bi.main --config config/magic_bi.yml` to start the system. Use an API tool or other systems to call Magic-BI. See `xxx` for API documentation.

# Models
## Large Models
Currently, large models (language and multimodal) are mainly adopted through OpenAI API compatibility, supporting both general models and fine-tuned models. Text, images, and business systems still use general large models; for SQL 
databases, the performance of fine-tuned models is better than that of general models.
### General Large Models
Text, images, and business systems currently still use general large models. For SQL databases, when using general large models, Magic-BI primarily provides Chat-BI services in a RAG (Retrieval-Augmented Generation) manner.
#### Local Large Models
Local large models can be deployed using ollama or vllm and provide services in an OpenAI API-compatible way.
#### Large Model Services
Almost all large model services are provided through the OpenAI API.
### Fine-Tuned Large Models
Fine-tuned large models are currently mainly used for SQL databases. The fine-tuning methods for the models are detailed in `xxx`.

# Configuration
The corresponding base_url, model, and api_key are configured in `config/magic_bi.yml`.