"""
Mask R-CNN
Configurations and data loading code for the Teeth dataset
This is an sub-class created using the original class.
Written by Adrian Llopart
"""

from config import Config
import skimage.io
import utils
import os
import glob
import numpy as np
import model as modellib

# Root directory of the project
ROOT_DIR = os.getcwd()

# Directory to save logs and trained model
MODEL_DIR = os.path.join(ROOT_DIR, "logs")

# Local path to trained weights file
COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")


# Teeth Configuration Class
# It overwrites the original values from the original class
class TeethConfig(Config):
    """Base configuration class. For custom configurations, create a
    sub-class that inherits from this one and override properties
    that need to be changed.
    """

    # Name the configurations. For example, 'COCO', 'Experiment 3', ...etc.
    # Useful if your code needs to do things differently depending on which
    # experiment is running.
    NAME = "Teeth"  # Override in sub-classes

    # NUMBER OF GPUs to use. For CPU training, use 1
    GPU_COUNT = 1

    # Number of images to train with on each GPU. A 12GB GPU can typically
    # handle 2 images of 1024x1024px.
    # Adjust based on your GPU memory and image sizes. Use the highest
    # number that your GPU can handle for best performance.
    IMAGES_PER_GPU = 1

    # Number of training steps per epoch
    # This doesn't need to match the size of the training set. Tensorboard
    # updates are saved at the end of each epoch, so setting this to a
    # smaller number means getting more frequent TensorBoard updates.
    # Validation stats are also calculated at each epoch end and they
    # might take a while, so don't set this too small to avoid spending
    # a lot of time on validation stats.
    STEPS_PER_EPOCH = 1000

    # Number of validation steps to run at the end of every training epoch.
    # A bigger number improves accuracy of validation stats, but slows
    # down the training.
    VALIDATION_STEPS = 1

    # Number of classification classes (including background)
    NUM_CLASSES = 1 + 16  # For background + my_classes

    # Input image resing
    # Images are resized such that the smallest side is >= IMAGE_MIN_DIM and
    # the longest side is <= IMAGE_MAX_DIM. In case both conditions can't
    # be satisfied together the IMAGE_MAX_DIM is enforced.
    IMAGE_MIN_DIM = 448
    IMAGE_MAX_DIM = 512

    # Maximum number of ground truth instances to use in one image
    MAX_GT_INSTANCES = 32

    # Max number of final detections
    DETECTION_MAX_INSTANCES = 32


    # Image mean (RGB)
    MEAN_PIXEL = np.array([151.18749735650982,151.18749735650982,151.18749735650982])

    # TODO think it over
    # Length of square anchor side in pixels
    RPN_ANCHOR_SCALES = (16, 32, 64, 128, 256)

    # Learning rate and momentum
    # The Mask RCNN paper uses lr=0.02, but on TensorFlow it causes
    # weights to explode. Likely due to differences in optimzer
    # implementation.
    LEARNING_RATE = 0.001
    LEARNING_MOMENTUM = 0.9


class TeethDataset(utils.Dataset):
    """The base class for dataset classes.
    To use it, create a new class that adds functions specific to the dataset
    you want to use. For example:

    class CatsAndDogsDataset(Dataset):
        def load_cats_and_dogs(self):
            ...
        def load_mask(self, image_id):
            ...
        def image_reference(self, image_id):
            ...

    See COCODataset and ShapesDataset as examples.
    """

    def __init__(self, class_map=None):
        self._image_ids = []
        self.image_info = []
        # Background is always the first class
        self.class_info = [{"source": "", "id": 0, "name": "BG"}]
        self.source_class_ids = {}

    def load_teeth(self, dataset_dir, dataset_type):
        """Generate the requested number of synthetic images.
        count: number of images to generate.
        height, width: the size of the generated images.
        """
        # Add classes
        self.add_class("teeth", 1, "u1")
        self.add_class("teeth", 2, "u2")
        self.add_class("teeth", 3, "u3")
        self.add_class("teeth", 4, "u4")
        self.add_class("teeth", 5, "u5")
        self.add_class("teeth", 6, "u6")
        self.add_class("teeth", 7, "u7")
        self.add_class("teeth", 8, "u8")
        self.add_class("teeth", 9, "l1")
        self.add_class("teeth", 10, "l2")
        self.add_class("teeth", 11, "l3")
        self.add_class("teeth", 12, "l4")
        self.add_class("teeth", 13, "l5")
        self.add_class("teeth", 14, "l6")
        self.add_class("teeth", 15, "l7")
        self.add_class("teeth", 16, "l8")


        # Get folders
        dataset_dir = os.path.join(dataset_dir, dataset_type)
        examples_paths = sorted([os.path.join(dataset_dir,f) for f in os.listdir(dataset_dir)])
        number_of_examples = len(examples_paths)

        # Add images
        for example, example_path in enumerate(examples_paths):
            image_path = os.path.join(example_path,'rgb.jpg')
            self.add_image("teeth", image_id=example, path=image_path)

    def load_image(self, image_id):
        """Load the specified image and return a [H,W,3] Numpy array.
        """
        # Load image
        image = skimage.io.imread(self.image_info[image_id]['path'])

        #print(self.image_info[image_id]['path'])

        # If grayscale. Convert to RGB for consistency.
        if image.ndim != 3:
            image = skimage.color.gray2rgb(image)
        return image

    def load_mask(self, image_id):
        """Load instance masks for the given image.

        Different datasets use different ways to store masks. Override this
        method to load instance masks and return them in the form of am
        array of binary masks of shape [height, width, instances].

        Returns:
            masks: A bool array of shape [height, width, instance count] with
                a binary mask per instance.
            class_ids: a 1D array of class IDs of the instance masks.
        """
        # Override this function to load a mask from your dataset.
        # Otherwise, it returns an empty mask.

        instance_masks = []
        class_ids = []

        labels_path = os.path.dirname(self.image_info[image_id]['path'])
        labels_path = os.path.join(labels_path, 'labels')

        #Get all .png files in the folder
        file_paths = os.path.join(labels_path,'*.png')
        file_paths = sorted(glob.glob(file_paths))

        #Add mask to instance_masks and append the class name found in the filename
        for file_path in file_paths:
            for cat in self.class_names:
                if cat in file_path:
                    mask = skimage.io.imread(file_path)
                    instance_masks.append(mask)
                    class_ids.append(self.class_names.index(cat))
                    #print("Filename loaded: ", file_path)
                    #print("Class loaded: ", cat)

        #Pack instance masks into an array
        if class_ids:
            mask = np.stack(instance_masks, axis=2)
            class_ids = np.array(class_ids, dtype=np.int32)
            return mask, class_ids
        else:
            # Call super class to return an empty mask
            return super(TeethDataset, self).load_mask(image_id)



############################################################
#  Training
############################################################

#lineに通知がいくコード
#
# def send_message(message):
#     import requests
#     url = "https://notify-api.line.me/api/notify"
#     token = ""
#     headers = {"Authorization" : "Bearer "+ token}
#     payload = {"message" :  message}
#     # files = {"imageFile": open("ここに画像のファイル名", "rb")}
#     r = requests.post(url ,headers = headers ,params=payload)
#     # post = requests.post(api, headers = headers, params=payload, files=files)
#


if __name__ == '__main__':
    import argparse

    # Download COCO trained weights from Releases if needed
    if not os.path.exists(COCO_MODEL_PATH):
        utils.download_trained_weights(COCO_MODEL_PATH)

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Train Mask R-CNN on Teeth.')
    parser.add_argument('--dataset', required=True,
                        metavar="/path/to/dataset",
                        help='Directory of the Teeth dataset')
    parser.add_argument('--model', required=True,
                        metavar="/path/to/weights.h5",
                        help="Path to weights .h5 file")
    parser.add_argument('--logs', required=False,
                        default=MODEL_DIR,
                        metavar="/path/to/logs/",
                        help='Logs and checkpoints directory (default=logs/)')
    args = parser.parse_args()
    print("Model: ", args.model)
    print("Dataset: ", args.dataset)
    print("Logs: ", args.logs)

    # Configurations
    config = TeethConfig()
    config.display()

    # Create model
    model = modellib.MaskRCNN(mode="training", config=config,model_dir=args.logs)

    model.load_weights(args.model, by_name=True,exclude=["mrcnn_bbox_fc","mrcnn_class_logits","mrcnn_mask"])
    # Training dataset. Use the training set and 35K from the
    # validation set, as as in the Mask RCNN paper.
    dataset_train = TeethDataset()
    dataset_train.load_teeth(args.dataset, "training")
    dataset_train.prepare()

    # Validation dataset
    dataset_val = TeethDataset()
    dataset_val.load_teeth(args.dataset, "validation")
    dataset_val.prepare()

    # *** This training schedule is an example. Update to your needs ***
    # Training - Stage 1
    print("Training network heads")
    # class_num = 16
    # send_message("{}class学習開始".format(class_num))
    model.train(dataset_train, dataset_val,
                learning_rate=config.LEARNING_RATE,
                epochs=10,
                layers='heads')
    # send_message("{}class学習1段階目終了".format(class_num))

    # Training - Stage 2
    # Finetune layers from ResNet stage 4 and up
    print("Fine tune Resnet stage 4 and up")
    model.train(dataset_train, dataset_val,
                learning_rate=config.LEARNING_RATE,
                epochs=20,
                layers='4+')
    # send_message("{}class学習2段階目終了".format(class_num))

    # Training - Stage 3
    # Fine tune all layers
    print("Fine tune all layers")
    model.train(dataset_train, dataset_val,
                learning_rate=config.LEARNING_RATE / 10,
                epochs=40,
                layers='all')
    # send_message("{}class学習終了".format(class_num))
