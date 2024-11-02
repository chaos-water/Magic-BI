import shutil
from contextlib import contextmanager
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import update
import os
# import paramiko
# import subprocess

from magic_bi.train.entity.domain_model import DomainModel
from magic_bi.train.entity.train_data import TrainData
from magic_bi.utils.globals import GLOBALS, GLOBAL_CONFIG
from magic_bi.train.entity.domain_model import DOMAIN_MODEL_STATE
from magic_bi.train.entity.train_data_prompted_item import TrainDataPromptedItem
from magic_bi.train.utils import get_train_data_prompted_item
import json

@contextmanager
def change_directory(target_dir):
    original_dir = os.getcwd()
    os.chdir(target_dir)
    try:
        yield
    finally:
        os.chdir(original_dir)


class ModelTrainer():
    def execute(self, domain_model_id: str, train_data_id: str, cuda_devices: str, train_epochs: float) -> int:
        domain_model_root_path = f"/{domain_model_id}"
        with change_directory("/LLaMA-Factory"):
            import os
            import subprocess
            if os.path.exists(domain_model_root_path):
                shutil.rmtree(domain_model_root_path)

            with Session(GLOBALS.sql_orm.engine, expire_on_commit=False) as session:
                domain_model: DomainModel = session.query(DomainModel).filter(
                    DomainModel.id == domain_model_id).one_or_none()
                if domain_model is None:
                    logger.error(f"execute_train_model failed, no domain model {domain_model_id} found")
                    return "".encode(), ""

                train_data: TrainData = session.query(TrainData).filter(TrainData.id == train_data_id).one_or_none()
                if train_data is None:
                    logger.error("execute_train_model failed")
                    return "".encode(), ""

                stmt = update(DomainModel).where(DomainModel.id == domain_model_id).values(
                    state=DOMAIN_MODEL_STATE.TRAINING.value)
                session.execute(stmt)
                session.commit()

            train_prompted_item_list: list[TrainDataPromptedItem] = get_train_data_prompted_item(train_data_id=train_data_id)

            data_to_export = []
            for train_prompted_item in train_prompted_item_list:
                data_to_export.append(
                    {"instruction": train_prompted_item.instruction, "input": train_prompted_item.input,
                     "output": train_prompted_item.output})

            if len(data_to_export) > 0:
                json_str = json.dumps(data_to_export, ensure_ascii=False, indent=4)
                with open("/LLaMA-Factory/data/text2sql.json", "w") as f:
                        f.write(json_str)
            else:
                logger.error("execute_train_model failed, no train_prompted_item get")
                return -1

            try:
                if cuda_devices != "":
                    visible_cuda_devices = f"CUDA_VISIBLE_DEVICES={cuda_devices}"
                else:
                    visible_cuda_devices = ""

                if "8b" in domain_model.base_model or "14b" in domain_model.base_model.lower():
                    deepspeed_config = "ds_z0_config"
                elif "32b" in domain_model.base_model.lower():
                    deepspeed_config = "ds_z3_config"
                else:
                    logger.error(f"execute_train_model failed, unsupported base model {domain_model.base_model}")
                    return -1

                if "llama" in domain_model.base_model.lower():
                    template = "llama3"
                elif "qwen" in domain_model.base_model.lower():
                    template = "qwen"

                train_command = \
                    f"FORCE_TORCHRUN=1 {visible_cuda_devices} llamafactory-cli train \
        --model_name_or_path /models/{domain_model.base_model} \
        --stage sft \
        --do_train true \
        --finetuning_type lora \
        --lora_target all \
        --deepspeed examples/deepspeed/{deepspeed_config}.json \
        --dataset text2sql \
        --template {template} \
        --cutoff_len {max(train_data.max_sql_len, 1024)} \
        --max_samples 9999999 \
        --overwrite_cache true \
        --preprocessing_num_workers 16 \
        --output_dir {domain_model_root_path}/lora_sft \
        --logging_steps 10 \
        --save_steps 500 \
        --plot_loss true \
        --overwrite_output_dir true \
        --per_device_train_batch_size 1 \
        --gradient_accumulation_steps 2 \
        --learning_rate 1.0e-4 \
        --num_train_epochs {train_epochs} \
        --lr_scheduler_type cosine \
        --warmup_ratio 0.1 \
        --bf16 true \
        --ddp_timeout 180000000 \
        --val_size 0.01 \
        --per_device_eval_batch_size 1 \
        --eval_strategy steps \
        --eval_steps 50"

                # 阻塞式执行 shell 命令
                logger.debug("train_command:%s" % train_command)
                result = subprocess.run(train_command, shell=True, check=True)
                logger.debug(result)
                logger.debug(result.__dict__)

                merge_command = \
                    f"llamafactory-cli export \
        --model_name_or_path /models/{domain_model.base_model} \
        --adapter_name_or_path /{domain_model.id}/lora_sft \
        --template llama3 \
        --finetuning_type lora \
        --export_dir {domain_model_root_path}/{domain_model.name} \
        --export_size 2 \
        --export_device cpu \
        --export_legacy_format false"

                logger.debug("merge_command:%s" % merge_command)
                result = subprocess.run(merge_command, shell=True, check=True)
                logger.debug(result)
                logger.debug(result.__dict__)

                transfer_to_gguf_command = \
                    f"python3 /llama.cpp/convert_hf_to_gguf.py {domain_model_root_path}/{domain_model.name}/ --outtype f16 --outfile  {domain_model_root_path}/{domain_model.name}.gguf"

                logger.debug(f"transfer_to_gguf_command:{transfer_to_gguf_command}")
                result = subprocess.run(merge_command, shell=True, check=True)
                logger.debug(result)
                logger.debug(result.__dict__)

                quantatize_command = \
                    f"llama-quantize {domain_model_root_path}/{domain_model.name}.gguf {domain_model_root_path}/{domain_model.name}_q4_k_m.gguf Q4_K_M"
                logger.debug(f"quantatize_command:{quantatize_command}")
                result = subprocess.run(merge_command, shell=True, check=True)
                logger.debug(result)
                logger.debug(result.__dict__)

                GLOBALS.oss_factory.add_file_by_path(domain_model_id,
                                                     f"{domain_model_root_path}/{domain_model.name}_q4_k_m.gguf")

                logger.debug(f"finished upload: {domain_model_root_path}/{domain_model.name}_q4_k_m.gguf")

                with Session(GLOBALS.sql_orm.engine, expire_on_commit=False) as session:
                    stmt = update(DomainModel).where(DomainModel.id == domain_model_id).values(
                        state=DOMAIN_MODEL_STATE.TRAINED.value)
                    session.execute(stmt)
                    session.commit()

            except Exception as e:
                logger.error("catch exception:%s" % str(e))
                with Session(GLOBALS.sql_orm.engine, expire_on_commit=False) as session:
                    stmt = update(DomainModel).where(DomainModel.id == domain_model_id).values(
                        state=DOMAIN_MODEL_STATE.NOT_TRAINED.value)
                    session.execute(stmt)
                    session.commit()

            finally:
                if os.path.exists(domain_model_root_path):
                    shutil.rmtree(domain_model_root_path)

            logger.debug("domain_model completed")
            return 0

    def is_json_para_legal(json_para: dict) -> bool:
        try:
            if json_para["domain_model_id"] != "" and json_para["train_data_id"] != "":
                return True

        except Exception as e:
            logger.error("catch exception:%s" % str(e))
            logger.error(f"is_json_para_legal failed, json_para:{json_para}")
            return False