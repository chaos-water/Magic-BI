import shutil
from loguru import logger
from magic_bi.utils.globals import Globals, GLOBALS
import os
from magic_bi.data.video.video_frame import ChatFrame
import time
import json

from magic_bi.data.video.video_frame_cropper import VideoFrameCropper
from magic_bi.data.data import Data
from magic_bi.utils.utils import image_ndarray_to_bytes


def tmp_save(frame, video_path, timestamp, frame_description):
    # frame_description = "%s\n\n%s" % (five_captions_descriptions, yolo_result_descriptions)
    imgage_dir = "./image_dir"
    text_dir = "./text_dir"
    from PIL import Image
    image = Image.fromarray(frame)
    video_name = os.path.basename(video_path)
    image_name = "%s_%s.jpg" % (video_name, str(timestamp))
    text_name = "%s_%s.txt" % (video_name, str(timestamp))
    image_path = os.path.join(imgage_dir, image_name)
    text_path = os.path.join(text_dir, text_name)
    image.save(image_path)
    with open(text_path, 'w') as f:
        f.write(frame_description)

def process_video(globals: Globals, data: Data, collection_id: str):
    import uuid, os
    tmp_dir_path = "./%s" % uuid.uuid1().hex
    os.mkdir(tmp_dir_path)

    try:
        file_path = os.path.join(tmp_dir_path, data.file_name)
        logger.debug("file_path: %s" % file_path)
        with open(file_path, "wb") as f:
            f.write(data.file_bytes)

        video_frame_cropper = VideoFrameCropper()
        video_frame_cropper.init(globals=GLOBALS)
        timestamp_2_frame_dict = video_frame_cropper.process(file_path)
        index = 0
        for timestamp, frame in timestamp_2_frame_dict.items():
            index += 1
            logger.debug("total frame cnt:%d, current frame cnt:%d" % (len(timestamp_2_frame_dict), index))
            chat_frame: ChatFrame = ChatFrame()
            chat_frame.file_id = data.file_id
            #         prompt = '''
            # Generate up to 5 captions for this image in Chinese.
            # '''
            prompt = '''
                Generate description for this image in Chinese as detail as you can. 
                '''

            try:
                five_captions_descriptions = GLOBALS.llava_adapter.process(frame, prompt)
                results = GLOBALS.yolo_inferencer.process(frame)
                yolo_result_descriptions = ""
                if len(results) > 0 and len(results[0].boxes) > 0:
                    yolo_result_descriptions = GLOBALS.yolo_inferencer.yolo_result_to_line_description(results[0].boxes)

                chat_frame.frame_description = "%s\n\n%s" % (five_captions_descriptions, yolo_result_descriptions)
                # tmp_save(frame, input_file, timestamp, chat_frame.frame_description)

                chat_frame.vector = GLOBALS.text_embedding.get(chat_frame.frame_description)
                chat_frame.file_name = os.path.basename(file_path)
                frame_bytes = image_ndarray_to_bytes(frame)
                chat_frame.frame_storage_id = \
                    GLOBALS.oss_factory.add_file_without_id(data.collection_id, frame_bytes)
                chat_frame.file_timeoffset = timestamp
                chat_frame.collection_id = data.collection_id

                GLOBALS.qdrant_adapter.upsert(collection_id=data.dataset_id, entities=[chat_frame])
                logger.debug("video_chat_collection_id:%s" % data)
            except Exception as e:
                logger.error("catch exception:%s" % str(e))

        # session = globals.sql_orm.get_session()
        # session.query(Data).filter(Data.file_id == data.file_id).update({"chat_analyse_status": ANALYSE_STATUS.PROCESSED.value, "update_timestamp": int(time.time() * 1000)})
        # session.commit()


    finally:
        if os.path.exists(tmp_dir_path):
            shutil.rmtree(tmp_dir_path)
            pass

    # logger.debug('load_video_by_file_bytes suc, analyse_types:%s, file_name:%s, collection_id:%s' % (analyse_types, data.file_name, collection_id))

def find_videos_in_directory(directory):
    import os
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.mpeg', '.mpg', '.m4v', '.3gp', '.ts']

    video_paths = []

    for root, dirs, files in os.walk(directory):
        for data in files:
            _, extension = os.path.splitext(data)
            if extension.lower() in video_extensions:
                video_paths.append(os.path.join(root, data))

    logger.debug('find_videos_in_directory suc, video_paths cnt:%d' % len(video_paths))
    print("video_paths:%s" % video_paths)
    return video_paths


def analyse_file_func(channel, method, properties, body):
    body_dict = json.loads(body)
    user_id = body_dict.get("user_id")
    file_id = body_dict.get("file_id")

    session = GLOBALS.sql_orm.get_session()
    data = session.query(Data).filter(Data.file_id == file_id, Data.user_id == user_id).first()
    if data is None:
        channel.basic_ack(delivery_tag=method.delivery_tag)
        logger.error("analyse_file_func failed, data is None, body:%s" % body_dict)
        return

    logger.debug("collection_id:%s" % data.dataset_id)
    data.file_bytes, file_size = GLOBALS.oss_factory.get_file(data.dataset_id, file_id)
    if file_size == 0 or len(data.file_bytes) == 0:
        channel.basic_ack(delivery_tag=method.delivery_tag)
        logger.error("analyse_file_func failed, collection_id:%s, file_id:%s" % (data.dataset_id, file_id))
        return
    process_video(GLOBALS, data, data.dataset_id)

    channel.basic_ack(delivery_tag=method.delivery_tag)
    # logger.debug("analyse_file_func suc")
    logger.debug("analyse_file_func suc, request body:%s" % body_dict)

if __name__ == '__main__':
    dir_path = "/media/luguanglong/mobile_drive/Data/内部数据集/施工监管场景视频/施工监管场景视频"
    find_videos_in_directory(dir_path)


