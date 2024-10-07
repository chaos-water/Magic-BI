import json
from typing import List

from loguru import logger
# from sentence_transformers import util

from magic_bi.model.text_embedding import TextEmbedding
from magic_bi.model.openai_adapter import OpenaiAdapter

# from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
# import numpy as np
import re


import re

import re


def split_by_symbol(text):
    # 定义中文分隔符，使用捕获组保留标点符号
    chinese_delimiters = r'([。！])'
    segments = re.split(chinese_delimiters, text)

    # 合并标点符号和内容
    combined_segments = []
    for i in range(0, len(segments) - 1, 2):
        sentence = segments[i].strip()
        if i + 1 < len(segments):
            sentence += segments[i + 1]  # 添加标点
        if sentence:  # 只保留非空段落
            combined_segments.append(sentence.strip())

    # 如果没有有效片段，则使用英文符号分割
    if not combined_segments:
        # 定义英文分隔符，使用捕获组保留标点符号
        english_delimiters = r'(\.|\!)\s*'
        segments = re.split(english_delimiters, text)

        combined_segments = []
        for i in range(0, len(segments) - 1, 2):
            sentence = segments[i].strip()
            if i + 1 < len(segments):
                sentence += segments[i + 1]  # 添加标点
            if sentence:  # 只保留非空段落
                combined_segments.append(sentence.strip())

    return combined_segments


# def split_by_symbol_v1(text, punctuation_index=0, sentence_max_length=256):
#     # 定义标点符号顺序
#     # punctuations = [ '。', '；', '？', '！', '.', ';', '?', '!']
#     punctuations = [ '。', '；', '？', '！', '.', ';', '?', '!']
#
#
#     # 如果文本长度小于或等于128，直接返回
#     if len(text) <= sentence_max_length or punctuation_index >= len(punctuations):
#         return [text]
#
#     # 尝试按每个标点符号进行分割
#     # for punctuation in punctuations:
#     punctuation = punctuations[punctuation_index]
#     segments = text.split(punctuation)
#     result = []
#
#     for segment in segments:
#         segment = segment.strip()
#         if len(segment) > sentence_max_length:
#             # 递归处理长句子
#             punctuation_index += 1
#             result.extend(split_by_symbol(text=segment, punctuation_index=punctuation_index))
#         elif segment:  # 确保非空句子
#             result.append(segment)
#
#     # 如果处理后有句子，不再继续尝试下一个标点
#     if result:
#         return result
#     else:
#         # 如果没有有效分割，返回原文本
#         return [text]


def split_by_embedding(input_content: str, text_embedding: TextEmbedding, similarity_threshold: float=0.1):
    # 将文本分割为句子
    sentence_list_v2 = []
    sentence_list_v1 = split_by_symbol(input_content)

    for sentence in sentence_list_v1:
        sentence_list_v2.append(sentence.strip())

    # similarity_threshold = 0.1
    model = text_embedding.get_model()
    sentence_vectors = model.encode(sentence_list_v2)

    # 计算每对相邻句子的相似度
    outout_segment_list = []
    current_segment = [sentence_list_v2[0]]

    for i in range(1, len(sentence_list_v2)):
        similarity = cosine_similarity(
            [sentence_vectors[i - 1]], [sentence_vectors[i]])[0][0]

        # 如果相似度低于阈值，则分割
        if similarity < similarity_threshold:
            outout_segment_list.append("".join(current_segment))
            current_segment = [sentence_list_v2[i]]
        else:
            current_segment.append(sentence_list_v2[i])

    # 把最后的段落加入segments
    if current_segment:
        for current_sentence in current_segment:
            if len(current_sentence.strip()) > 0:
                outout_segment_list.append(current_sentence.strip())

    logger.debug("split_by_embedding suc, outout_segment_list cnt:%d" % len(outout_segment_list))
    return outout_segment_list


def extract_chunks_by_index(text: str, patterns: List):
    import re
    sentences = []
    for pattern in patterns:
        start = re.escape(pattern['start_words'])
        end = re.escape(pattern['end_words'])
        regex = rf'({start}.*?{end})'
        matches = re.findall(regex, text)
        sentences.extend(matches)
    return sentences

split_content_prompt_template = \
"""[Content]:
{content}

[Instructions]:
    1、按照语义对上诉内容进行分片，生成文档片段；
    2、主题的数量要尽可能少；
    3、原文中的任何一个文字都很重要，不要遗漏任何一个文。如果无法分片，则输出空数组[]即可;
    4、将生成的文档片段输出为一个数组即可，不需要其它解释。

首先分析给定的条件，然后逐步解决问题，不要输出推理中间步骤，直接输出推理结果。"""

def split_by_llm(input_content: str, openai_adapter: OpenaiAdapter) -> List[str]:
    split_content_prompt = split_content_prompt_template.replace("{content}", input_content)

    llm_output = openai_adapter.process(split_content_prompt)
    try:
        chunk_list = json.loads(llm_output)
        # if chunk_index_list == []:
        #     logger.debug("split_by_llm faile")
        #     return []
        #
        # chunk_list = extract_chunks_by_index(input_content, chunk_index_list)
        logger.debug("split_by_llm suc")
        return chunk_list
    except Exception as e:
        logger.debug("catch exception:%s " % str(e))
        return []

if __name__ == '__main__':
    content = \
"""宽带常见错误代码及故障的解决方法1、错误代码691处理方法：691的提示可能是用户名与密码填写错误导 致，首先检查自己的用户名是否为：xz电话号码@adsl（或0516电话号码@adsl，必须小写），再确定密码没有填错或被家庭其他成员修改，密码是区分大小写的，这一点尤其应注意如果密码遗忘，请带电话户主身份证到电信营业厅修改或拨打中国电信客服热线10000如果还是出现同样的691的提 示，有可能是上网帐号欠费或账号挂死所导致，你可以致电中国电信客户服务热线10000号查询或者申告障碍2、错误代码678处理方法：如在上网过程中遇到错误提示是678，则可以按下列步骤一步一步进行检查处 理1、首先检查Modem状态，判断Modem是否正常2、 正常的情况下，把Modem断电5分钟后重启电脑再试；Modem不正常时，要先将Modem断电，检查Modem到网卡和Modem到分离器之间的网线 是否接好3、 重启Modem无效时，Modem灯正常的情况下，建议卸载网卡驱动程序和拨号软件，并重新安装4、 仍然提示678，请致电中国电信客户服务热线10000号申告故障，我们将派专人为你检查线路是否有问题3、错误代码769处理方法：769故障一般都是出现在xp操作系统中，是由于电脑里本地连接禁用了你只需要重新启动 本地连接则可恢复正常首先请在电脑的桌面上找到一个“网上邻居”图标接下来直接用鼠标的右键单击网上邻居，再用鼠标左键单击属性然后双击本地连接，系统就会自动启用本地连接当本地连接启动好后，重新拨号就能上网4、错误代码619处理方法：建议重新启动电脑，重新连接Modem线路，如果还是无法恢复正常就卸载干净任何PPPoE软件， 重新安装5、错误代码718处理方法：718错误 一般出现在服务器故障的时候，表示已经成功发送验证信息，但是无法接收到服务器返回的响应信息，线路连接正常建议稍后再试，应该只是服务器比较繁忙导致6、错误代码734处理方法：建议重新启动电 脑，重新连接Modem线路，如果还是无法恢复正常就卸载干净任何PPPoE软件，重新安装7、错 误代码797处理方法：建议重新启动电脑，重新连接Modem线路，如果还是无法恢复正常就卸载干净任何PPPoE软件， 重新安装8、错误代码735处理方法：用户自己设 置IP地址与局方分配IP有冲突导致，建议用户IP地址选择自动获取或重装拨号软件即可9、如何判断Modem处于正常状态？当拨号连接不上网络的时候，请检查Modem是否处于正常状态当Modem处于正常状态的时 候，Modem会有两盏或三盏指示灯处于长亮状态分别是电源灯、线路灯和网卡灯不同型号的Modem，其指示灯的名称、标识可能不同，下面列出一部分Modem的指示灯的名称与标识，具体情况，请参见你的Modem的使用说明书部分Modem型号及指示灯对应表：modem型 号电源灯线路灯网卡灯信号灯上海贝尔pw/powerWanLink中兴pw/powerDslLAN华为pw/powerWanLink无线猫如 果电源灯、线路灯有任何一盏不亮或闪烁，都不正常通常你可以先关电重启一下Modem（有些modem背后有电源开关），等2分钟后，当Modem的灯 稳定下来，如果还不正常，可以参考以下的解决方法（1）电源灯：如果不亮则可能是电源未打开或未接好，也可能modem有问 题（2）线路灯：使用ADSL时，用户端的Modem要与局端的Modem同步建立连接，若能同步，则线路灯常亮，否则会闪烁如果发现线路灯闪烁，则证明线路不同步，原因可能有几种：①你的电话线连接不正确或接触不好，或者有的电话机没有正确连接分离 器；②分离器有问题；③线路有问题此时建议你检查一下各设备之间的联线是否有松动、脱落等情况，然后重新启动一下modem，如果发现线路灯依然闪烁，则可能是线路问题，你需要打10000号报障（3）网卡灯:表示Modem和计算机网卡的连接状 态如果此灯不亮，可能是你的电脑没有打开，或者是连接网卡和modem的网线未连接好，也有可能是modem故障，请确认网线和modem、网线和网卡 都连接好，你可以尝试把网线插拔几次或更换网线还有一种可能就是网卡松了或坏了如果以上步骤完成后，网卡灯还是不亮，请更换 一个modem试试，或将你的modem拿到别的有ADSL的地方试试 ，检查是否Modem问题若Modem本身正常，你需要寻求电脑公司的专业帮助二、宽带常见问题的解答1、为 什么上网时经常掉线？ADSL掉线涉及到几个方面的问题，包括线路故障(线路干扰)、Modem故障(发热、质量、兼容性)、网卡故障(速度慢、 驱动程序陈旧)等当你ADSL遇到掉线时，可以做如下操作：1）要求每个电话分机前面都必须加装分离器（滤波器），分机 最好不要超过2个，请不要存在未接分机的电话线2）网卡质量不稳定故障现象是网络只要一断开,再也连不上如果Modem的线路同步灯常亮，基本排除外部线路的故障，问题多数出在网卡上如果排除了网线、微机、插槽的问题，一般为网卡质量不稳定，请及时更换网卡3）上网、通话不能同 时进行故障现象一般是提起话筒网络就会掉线一般为外线绝缘不良或有接头接触不良，又或者是分离器的质量不好4）错误串接电话分机由于不正确串接电话分机，从而造成串扰，引起上网掉线，一般在分离器前面不要接电话分机，如果要接请从分离器后面再接分机5）MODEM发热由于MODEM长时间没关闭，导致MODEM过热也会产生上网不稳定的现象，建议你在不上网的时候，尽量把MODEM电源断开6）MODEM旁 边有高功率的电器设备，很容易导致信号受干扰，建议你MODEM旁边不要放手机、冰箱等一些电器设备打开的手机一定不要放在Modem的旁边，因为每隔几分钟手机会自动查找网络，这时强大的电磁波干扰足以造成Modem断流2、 为什么ADSL从下载速度看没有想象中的快呢？主要是速率单位的问题例如:号称56K的Modem下载速率最大才5～6K56K单 位是bit，而下载时的速率显示是byte1byte=8bit所以下载显示是120KB时，其实已经达到了120K*8BIT=0.96Mbit， 已经相当快了另外，下载速度还和网站服务器及访问人数有关系，建议下载大文件时尽量使用下载工具并且不要选择网络忙时有时网页比较慢，先试着打开别的网站如果很快，可能是您访问的网站服务器原因，请稍后再试，如果同样很慢，建议检查自己计算机内存和cpu占用情况，如利用率很高，可能中病毒，建议先查杀病毒"""
    from magic_bi.config.model_config import ModelConfig
    text_embeddig_config = ModelConfig()
    text_embeddig_config.model = "/Users/luguanglong/Codes/mojing/Magic-BI/model.md/paraphrase-multilingual-mpnet-base-v2"
    # text_embeddig_config.model = "/Users/luguanglong/Codes/mojing/Magic-BI/model.md/all-mpnet-base-v2"

    # openai_adapter_config = ModelConfig()
    # openai_adapter_config.model = "llama3.1:70b"
    # openai_adapter_config.api_key = "ollama"
    # openai_adapter_config.base_url = "http://192.168.68.96:11434/v1/"
    # openai_adapter_config.system_prompt = "You are a helpful assistant."

    text_embedding = TextEmbedding()
    text_embedding.init(model_config=text_embeddig_config)

    # openai_adapter = OpenaiAdapter()
    # openai_adapter.init(model_config=openai_adapter_config)

    content_list = split_by_embedding(content, text_embedding, 0.1)
    pass
    # content_list = split_by_embedding(content, text_embedding=text_embedding)
    # for content_item in content_list:
    #     if len(content_item) > 512:
    #         prompt = split_content_prompt_template.replace("{content}", content_item)
    #         llm_output = openai_adapter.process(prompt)
    #         llm_output_json = json.loads(llm_output)
    #         print(llm_output_json)
    #         pass
    #     else:
    #         print(len(content_item))