# enums/product_status.py
from enum import Enum


class ProductScanStatus(Enum):
    NO_PRODUCT = "no_product"
    INVALID_NAME = "invalid_name"
    DUPLICATE = "duplicate"
    SUCCESS = "success"
    ERROR = "error"
