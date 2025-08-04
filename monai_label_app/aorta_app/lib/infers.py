import logging
import os
from typing import Callable, Sequence

import torch
from monai.inferers import SlidingWindowInferer
from monai.networks.nets import UNet
from monai.transforms import (
    Activationsd,
    AsDiscreted,
    Compose,
    CropForegroundd,
    EnsureChannelFirstd,
    EnsureTyped,
    LoadImaged,
    Orientationd,
    ScaleIntensityRanged,
    Spacingd,
)

from monailabel.interfaces.tasks.infer import InferTask
from monailabel.interfaces.utils.transform import run_transforms
from monailabel.utils.others.generic import device_list, gpu_memory_map

from .configs import INTENSITY_RANGE, TARGET_SPACING, NETWORK_CONFIG, INFERENCE_CONFIG

logger = logging.getLogger(__name__)


class AortaSegmentation(InferTask):
    """
    Inference task for aortic segmentation using 3D UNet
    """

    def __init__(
        self,
        path: str,
        network: torch.nn.Module = None,
        roi_size: Sequence[int] = (96, 96, 96),
        preload: bool = False,
        config: dict = None,
    ):
        super().__init__(
            path=path,
            network=network,
            roi_size=roi_size,
            preload=preload,
            config=config,
        )
        
        self.roi_size = roi_size
        
        if network is None:
            self.network = UNet(**NETWORK_CONFIG)
        else:
            self.network = network

    def pre_transforms(self, data=None) -> Compose:
        """
        Pre-processing transforms matching the training pipeline
        """
        return Compose([
            LoadImaged(keys="image"),
            EnsureChannelFirstd(keys="image"),
            ScaleIntensityRanged(
                keys="image",
                a_min=INTENSITY_RANGE["a_min"],
                a_max=INTENSITY_RANGE["a_max"],
                b_min=INTENSITY_RANGE["b_min"],
                b_max=INTENSITY_RANGE["b_max"],
                clip=True,
            ),
            CropForegroundd(keys="image", source_key="image"),
            Orientationd(keys="image", axcodes="RAS"),
            Spacingd(
                keys="image",
                pixdim=TARGET_SPACING,
                mode="bilinear",
            ),
            EnsureTyped(keys="image"),
        ])

    def inferer(self, data=None) -> Callable:
        """
        Sliding window inferer for large volume inference
        """
        return SlidingWindowInferer(
            roi_size=INFERENCE_CONFIG["roi_size"],
            sw_batch_size=INFERENCE_CONFIG["sw_batch_size"],
            overlap=INFERENCE_CONFIG["overlap"],
        )

    def inverse_transforms(self, data=None) -> Compose:
        """
        Inverse transforms to restore original spacing and orientation
        """
        return Compose([
            EnsureTyped(keys="pred", device="cpu", track_meta=False),
            Activationsd(keys="pred", softmax=True),
            AsDiscreted(keys="pred", argmax=True),
        ])

    def post_transforms(self, data=None) -> Compose:
        """
        Post-processing transforms
        """
        return Compose([
            EnsureTyped(keys="pred", device="cpu", track_meta=False),
        ])

    def __call__(self, request, datastore=None):
        """
        Execute inference on the input request
        """
        logger.info(f"Starting aortic segmentation inference")
        
        if torch.cuda.is_available():
            logger.info(f"GPU Memory: {gpu_memory_map()}")
        
        result = super().__call__(request, datastore)
        
        logger.info(f"Aortic segmentation inference completed")
        return result

    def get_path(self):
        """
        Get the model path
        """
        return self.path

    def is_valid(self) -> bool:
        """
        Check if the model file exists and is valid
        """
        if not os.path.exists(self.path):
            logger.warning(f"Model file not found: {self.path}")
            return False
        return True

    def get_config(self):
        """
        Get inference configuration
        """
        return {
            "network": NETWORK_CONFIG,
            "inference": INFERENCE_CONFIG,
            "intensity_range": INTENSITY_RANGE,
            "target_spacing": TARGET_SPACING,
            "roi_size": self.roi_size,
        }
