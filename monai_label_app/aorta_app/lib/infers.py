import logging
import os
from collections.abc import Sequence
from typing import Callable, Optional

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
from monailabel.utils.others.generic import gpu_memory_map

from .configs import INFERENCE_CONFIG, INTENSITY_RANGE, NETWORK_CONFIG, TARGET_SPACING

logger = logging.getLogger(__name__)


class AortaSegmentation(InferTask):
    """
    Inference task for aortic segmentation using 3D UNet
    """

    def __init__(
        self,
        path: str,
        network: Optional[torch.nn.Module] = None,
        roi_size: Sequence[int] = (96, 96, 96),
        preload: bool = False,
        config: Optional[dict] = None,
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

    def pre_transforms(self, data: Optional[dict] = None) -> Compose:  # noqa: ARG002
        """
        Pre-processing transforms matching the training pipeline
        """
        return Compose(
            [
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
            ]
        )

    def inferer(self, data: Optional[dict] = None) -> Callable:  # noqa: ARG002
        """
        Sliding window inferer for large volume inference
        """
        return SlidingWindowInferer(
            roi_size=INFERENCE_CONFIG["roi_size"],
            sw_batch_size=INFERENCE_CONFIG["sw_batch_size"],
            overlap=INFERENCE_CONFIG["overlap"],
        )

    def inverse_transforms(self, data: Optional[dict] = None) -> Compose:  # noqa: ARG002
        """
        Inverse transforms to restore original spacing and orientation
        """
        return Compose(
            [
                EnsureTyped(keys="pred", device="cpu", track_meta=False),
                Activationsd(keys="pred", softmax=True),
                AsDiscreted(keys="pred", argmax=True),
            ]
        )

    def post_transforms(self, data: Optional[dict] = None) -> Compose:  # noqa: ARG002
        """
        Post-processing transforms
        """
        return Compose(
            [
                EnsureTyped(keys="pred", device="cpu", track_meta=False),
            ]
        )

    def __call__(self, request: dict, datastore: Optional[dict] = None) -> dict:
        """
        Execute inference on the input request
        """
        logger.info("Starting aortic segmentation inference")

        if torch.cuda.is_available():
            logger.info(f"GPU Memory: {gpu_memory_map()}")

        result = super().__call__(request, datastore)

        logger.info("Aortic segmentation inference completed")
        return result

    def get_path(self) -> str:
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

    def get_config(self) -> dict:
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
