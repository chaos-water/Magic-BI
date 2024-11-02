from enum import Enum


class TRAIN_DATA_GENERATE_METHOD(Enum):
    PURE_CONVERSION = "pure_conversion"
    FEW_SHOT = "few_shot_augment"
    ZERO_SHOT = "zero_shot_augment"

class TRAIN_DATA_GENERATE_STATE(Enum):
    GENERATING = "generating"
    GENERATED = "generated"

class TRAIN_DATA_ITEM_VALID_RESULT(Enum):
    VALID = "valid"
    INVALID = "invalid"