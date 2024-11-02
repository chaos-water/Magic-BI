from loguru import logger
from FlagEmbedding import FlagReranker

class TextRerankeAdapter(object):
    def __init__(self):
        self.reranker = None

    def init(self, model_path_or_name: str="='BAAI/bge-reranker-v2-m3'") -> int:
        self.reranker = FlagReranker(model_path_or_name, use_fp16=True)

        logger.debug("TextRerankeAdapter init suc")
        return 0

    # 这段代码做个改写，scores是个分数的数组，用来标识compare_input_list中匹配的程度。请根据score的多少，输出input_text_list中的文本，并配上对应的分数。
    def process(self, input_text: str, input_text_list: list[str]) -> list:
        compare_input_list = [[input_text, input_text2] for input_text2 in input_text_list]

        scores = self.reranker.compute_score(compare_input_list, normalize=True)

        # Zip the texts with their scores and sort by score in descending order
        scored_texts = sorted(zip(input_text_list, scores), key=lambda x: x[1], reverse=True)

        # Print the results
        # for text, score in scored_texts:
        #     print(f'Text: "{text}" | Score: {score}')
        logger.debug("process suc scored_texts:%d" % len(scored_texts))
        return scored_texts

if __name__ == '__main__':
    relevant_text_ranker: TextRerankeAdapter = TextRerankeAdapter()
    relevant_text_ranker.init(model_path_or_name='BAAI/bge-reranker-v2-m3')
    # relevant_text_ranker.init(model_path_or_name="BAAI/bge-reranker-large")
    question = "DSL调制解调器的软件要求是什么？"
    chunks = ['本手册旨在提供有关DSL调制解调器的设置、操作和故障排除指南。它适用于网络管理员、技术支持人员和用户。\n', '本手册提供了有关DSL调制解调器设置、操作和故障排除的详细指南。通过遵循这些步骤，您可以轻松地配置和管理您的DSL网络连接。如果您仍然遇到问题，请联系技术支持人员或制造商寻求帮助。\n', 'DSL调制解调器设备\n个人计算机或笔记本电脑\n网络电缆（RJ-11）\n电源线\n', '将DSL调制解调器设备连接到电源线上。\n使用网络电缆（RJ-11）将调制解调器连接到电话线路上。\n将调制解调器连接到个人计算机或笔记本电脑的以太网端口上。\n', '检查带宽限制是否设置过低。\n检查网络拥塞是否严重。\n尝试更换DSL模式或调整带宽限制。\n', '打开网络浏览器并输入调制解调器的IP地址（通常为192.168.1.1）。\n输入管理员用户名和密码（默认值通常为admin/admin）。\n配置调制解调器的参数，包括：\nDSL模式：选择正确的DSL模式（例如ADSL、VDSL等）。\n带宽：设置带宽限制。\nIP地址：配置IP地址和子网掩码。\n\n\nDSL模式：选择正确的DSL模式（例如ADSL、VDSL等）。\n带宽：设置带宽限制。\nIP地址：配置IP地址和子网掩码。\n', 'A：下载最新的固件版本并按照制造商的指南进行更新。\n', '使用网络浏览器测试互联网连接。\n如果无法连接，请检查调制解调器的LED指示灯是否正常闪烁。\n', '检查调制解调器的LED指示灯是否正常闪烁。\n检查网络电缆（RJ-11）是否松动或损坏。\n重启调制解调器和个人计算机或笔记本电脑。\n', '检查管理员用户名和密码是否正确。\n检查IP地址是否配置正确。\n尝试使用默认值（admin/admin）登录。\n', 'A：按住调制解调器的复位按钮约10秒钟，直到LED指示灯闪烁。\n', '操作系统：Windows、macOS 或 Linux\n网络浏览器：Google Chrome、Mozilla Firefox 或 Safari\n']


    ret = relevant_text_ranker.process(question, chunks)
    print(ret)
