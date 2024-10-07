import os.path

import torch

from typing import Dict
from loguru import logger
import cv2
from magic_bi.utils.globals import Globals

class VideoFrameCropper():
    def __init__(self):
        pass

    def init(self, globals: Globals) -> int:
        self.globals: Globals = globals
        return 0

    def process(self, video_path: str) -> Dict:
        try:
            index = 0
            output_timestamp_2_frame = {}
            previous_embedding = [0.0]*768
            timestamp_2_frame = self._extract_key_frames(video_path)
            logger.debug("timestamp_2_frame_cnt:%d" % len(timestamp_2_frame))
            for timestamp, frame in timestamp_2_frame.items():
                index += 1
                if (index % 100) == 0:
                    logger.debug("process in, video_path:%s, index:%d" % (video_path, index))

                current_embedding = self.globals.clip_embedding.get_image_vector(frame)
                similarity = self._cosine_similarity(vector1=previous_embedding, vector2=current_embedding)

                previous_embedding = current_embedding
                if similarity > 0.92:
                    logger.debug("similarity:%f" % similarity)
                    continue
                dir_path = "./tmp"
                frame_path = os.path.join(dir_path, "%d_%f.jpg" % (timestamp, similarity))
                cv2.imwrite(frame_path, frame)
                output_timestamp_2_frame[timestamp] = frame

            logger.debug("process suc, output_timestamp_2_frame cnt:%d" % len(output_timestamp_2_frame))
            return output_timestamp_2_frame
        except Exception as e:
            logger.error("exception:%s" % str(e))
        finally:
            logger.debug("process exit")

    def _extract_key_frames(self, input_file):
        # 保存符合条件的关键帧的字典
        try:
            keyframes = {}

            import time
            begin_timestamp = int(time.time())
            # 打开视频文件
            video_capture = cv2.VideoCapture(input_file)

            # 确认视频文件是否成功打开
            if not video_capture.isOpened():
                logger.error("无法打开视频文件")
                return keyframes
            fps = video_capture.get(cv2.CAP_PROP_FPS)
            total_frame_count = video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
            round_fps = round(fps)
            # 初始化帧计数器和前一帧
            prev_frame = None
            frame_count = 0

            # 计算每一帧与前一帧的光流
            while True:
                ret, frame = video_capture.read()
                # 确认是否成功读取帧
                if not ret or frame is None:
                    break

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                if frame_count % round_fps != 0:
                    frame_count += 1
                    continue

                # 转换为灰度图像
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                if prev_frame is not None:
                    # 估计光流
                    flow = cv2.calcOpticalFlowFarneback(prev_frame, gray_frame, None, 0.5, 3, 15, 3, 5, 1.2, 0)
                    flow_magnitude = cv2.norm(flow, cv2.NORM_L2)
                    # print("帧 {} 与前一帧的光流大小: {}".format(frame_count, flow_magnitude))
                    # 如果光流大小超过阈值，保存该帧
                    if flow_magnitude > 2500:  # 这里可以根据需要调整阈值
                        frame_timestamp = int(frame_count * (1000 / fps))
                        keyframes[frame_timestamp] = frame_rgb
                else:
                    frame_timestamp = int(frame_count * (1000 / fps))
                    keyframes[frame_timestamp] = frame_rgb

                # # 更新前一帧
                prev_frame = gray_frame

                if (frame_count % 900) == 0:
                    logger.debug("video_path:%s, frame count:%d, total_frame_count:%d" % (input_file, frame_count, total_frame_count))

                frame_count += 1

            # 关闭视频文件
            video_capture.release()

            end_timestamp = int(time.time())
            logger.debug("_extract_key_frames, video_path: %s, cost_time:%d" % (input_file, (end_timestamp - begin_timestamp)))
            return keyframes
        except Exception as e:
            logger.error("catch exception:%s" % str(e))
        finally:
            logger.debug("_extract_key_frames exit")

    def _cosine_similarity(self, vector1, vector2):
        # Convert vectors to torch tensors
        vector1_tensor = torch.tensor(vector1)
        vector2_tensor = torch.tensor(vector2)

        # Compute dot product
        dot_product = torch.dot(vector1_tensor, vector2_tensor)

        # Compute magnitudes of each vector
        magnitude1 = torch.norm(vector1_tensor)
        magnitude2 = torch.norm(vector2_tensor)

        if magnitude1.item() == 0.0 or magnitude2.item() == 0.0:
            return 0.0
        else:
            similarity = dot_product / (magnitude1 * magnitude2)
            return similarity.item()


