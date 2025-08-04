import logging
import os
from typing import Any, Dict, Optional, Union

from monailabel.interfaces.app import MONAILabelApp
from monailabel.interfaces.config import TaskConfig
from monailabel.interfaces.datastore import Datastore
from monailabel.interfaces.tasks.infer import InferTask
from monailabel.interfaces.tasks.train import TrainTask
from monailabel.utils.others.generic import download_file, strtobool

from lib.configs import PRETRAINED_PATH
from lib.infers import AortaSegmentation

logger = logging.getLogger(__name__)


class AortaApp(MONAILabelApp):
    """
    MONAI Label App for Aortic Segmentation using 3D UNet
    
    This application provides interactive segmentation capabilities for aortic structures
    using a pre-trained 3D UNet model with 24 output classes.
    """

    def __init__(self, app_dir, studies, conf):
        self.model_dir = os.path.join(app_dir, "model")
        
        configs = {}
        for t in ["segmentation"]:
            configs[t] = TaskConfig(
                id=t,
                name=f"Aortic {t.title()}",
                type=t,
                description=f"A pre-trained model for Aortic {t}",
            )

        models = {
            "aorta_segmentation": os.path.join(self.model_dir, "aorta_segmentation_unet.pt"),
        }

        if conf.get("use_pretrained_model", True):
            spatial_size = conf.get("spatial_size", [96, 96, 96])
            for name, path in models.items():
                if not os.path.exists(path):
                    logger.info(f"Model {name} not found at {path}")
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    with open(path, 'w') as f:
                        f.write("# Placeholder for pre-trained model weights\n")

        super().__init__(
            app_dir=app_dir,
            studies=studies,
            conf=conf,
            name="Aortic Segmentation App",
            description="MONAI Label App for Aortic Segmentation using 3D UNet",
            version="1.0.0",
            configs=configs,
        )

    def init_infers(self) -> Dict[str, InferTask]:
        """
        Initialize inference tasks
        """
        infers: Dict[str, InferTask] = {}
        
        infers["aorta_segmentation"] = AortaSegmentation(
            path=os.path.join(self.model_dir, "aorta_segmentation_unet.pt"),
            network=self._get_network(),
            roi_size=self.conf.get("spatial_size", [96, 96, 96]),
            preload=strtobool(self.conf.get("preload", "false")),
            config={"cache_transforms": True, "cache_transforms_in_memory": True},
        )
        
        return infers

    def init_trainers(self) -> Dict[str, TrainTask]:
        """
        Initialize training tasks
        """
        trainers: Dict[str, TrainTask] = {}
        return trainers

    def _get_network(self):
        """
        Get the 3D UNet network definition
        """
        from monai.networks.nets import UNet
        
        return UNet(
            spatial_dims=3,
            in_channels=1,
            out_channels=24,  # 24 classes (background + 23 regions)
            channels=(16, 32, 64, 128, 256),
            strides=(2, 2, 2, 2),
            num_res_units=2,
        )

    def init_datastore(self) -> Datastore:
        """
        Initialize datastore
        """
        datastore = super().init_datastore()
        return datastore
