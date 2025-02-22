import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from pytorch_lightning.utilities.model_summary import ModelSummary
from pytorch_lightning import LightningModule, LightningDataModule, Trainer
from torchsummary import summary

__weights_dict = dict()


def load_weights(weight_file):
    if weight_file == None:
        return

    try:
        weights_dict = np.load(weight_file, allow_pickle=True).item()
    except:
        weights_dict = np.load(weight_file, allow_pickle=True, encoding='bytes').item()

    return weights_dict

# TS rewrite to lightning module


class KitModel(LightningModule):

    def __init__(self, weight_file):
        super(KitModel, self).__init__()
        global __weights_dict
        # ts add if
        if weight_file:
            __weights_dict = load_weights(weight_file)

        # 感覺好像沒用到這行, 奇怪
        self.example_input_array = torch.rand(5, 3, 256, 384)  # batch size 5, and one image

        self.stem_conv_res1_convolution = self.__conv(
            2, name='stem_conv_res1/convolution', in_channels=3, out_channels=32, kernel_size=(3, 3), stride=(2, 2), groups=1, bias=None)
        self.stem_bn_res1_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'stem_bn_res1/FusedBatchNorm_1', num_features=32, eps=0.0010000000474974513, momentum=0.0)
        self.block1a_dwconv_res1_depthwise = self.__conv(
            2, name='block1a_dwconv_res1/depthwise', in_channels=32, out_channels=32, kernel_size=(3, 3), stride=(1, 1), groups=32, bias=None)
        self.block1a_bn_res1_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'block1a_bn_res1/FusedBatchNorm_1', num_features=32, eps=0.0010000000474974513, momentum=0.0)
        self.block1a_se_reduce_res1_convolution = self.__conv(
            2, name='block1a_se_reduce_res1/convolution', in_channels=32, out_channels=8, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.block1a_se_expand_res1_convolution = self.__conv(
            2, name='block1a_se_expand_res1/convolution', in_channels=8, out_channels=32, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.block1a_project_conv_res1_convolution = self.__conv(
            2, name='block1a_project_conv_res1/convolution', in_channels=32, out_channels=16, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.block1a_project_bn_res1_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'block1a_project_bn_res1/FusedBatchNorm_1', num_features=16, eps=0.0010000000474974513, momentum=0.0)
        self.block2a_expand_conv_res1_convolution = self.__conv(
            2, name='block2a_expand_conv_res1/convolution', in_channels=16, out_channels=96, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.block2a_expand_bn_res1_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'block2a_expand_bn_res1/FusedBatchNorm_1', num_features=96, eps=0.0010000000474974513, momentum=0.0)
        self.block2a_dwconv_res1_depthwise = self.__conv(
            2, name='block2a_dwconv_res1/depthwise', in_channels=96, out_channels=96, kernel_size=(3, 3), stride=(2, 2), groups=96, bias=None)
        self.block2a_bn_res1_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'block2a_bn_res1/FusedBatchNorm_1', num_features=96, eps=0.0010000000474974513, momentum=0.0)
        self.block2a_se_reduce_res1_convolution = self.__conv(
            2, name='block2a_se_reduce_res1/convolution', in_channels=96, out_channels=4, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.block2a_se_expand_res1_convolution = self.__conv(
            2, name='block2a_se_expand_res1/convolution', in_channels=4, out_channels=96, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.block2a_project_conv_res1_convolution = self.__conv(
            2, name='block2a_project_conv_res1/convolution', in_channels=96, out_channels=24, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.block2a_project_bn_res1_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'block2a_project_bn_res1/FusedBatchNorm_1', num_features=24, eps=0.0010000000474974513, momentum=0.0)
        self.block2b_expand_conv_res1_convolution = self.__conv(
            2, name='block2b_expand_conv_res1/convolution', in_channels=24, out_channels=144, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.block2b_expand_bn_res1_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'block2b_expand_bn_res1/FusedBatchNorm_1', num_features=144, eps=0.0010000000474974513, momentum=0.0)
        self.block2b_dwconv_res1_depthwise = self.__conv(
            2, name='block2b_dwconv_res1/depthwise', in_channels=144, out_channels=144, kernel_size=(3, 3), stride=(1, 1), groups=144, bias=None)
        self.block2b_bn_res1_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'block2b_bn_res1/FusedBatchNorm_1', num_features=144, eps=0.0010000000474974513, momentum=0.0)
        self.block2b_se_reduce_res1_convolution = self.__conv(
            2, name='block2b_se_reduce_res1/convolution', in_channels=144, out_channels=6, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.block2b_se_expand_res1_convolution = self.__conv(
            2, name='block2b_se_expand_res1/convolution', in_channels=6, out_channels=144, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.block2b_project_conv_res1_convolution = self.__conv(
            2, name='block2b_project_conv_res1/convolution', in_channels=144, out_channels=24, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.block2b_project_bn_res1_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'block2b_project_bn_res1/FusedBatchNorm_1', num_features=24, eps=0.0010000000474974513, momentum=0.0)
        self.block3a_expand_conv_res1_convolution = self.__conv(
            2, name='block3a_expand_conv_res1/convolution', in_channels=24, out_channels=144, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.block3a_expand_bn_res1_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'block3a_expand_bn_res1/FusedBatchNorm_1', num_features=144, eps=0.0010000000474974513, momentum=0.0)
        self.block3a_dwconv_res1_depthwise = self.__conv(
            2, name='block3a_dwconv_res1/depthwise', in_channels=144, out_channels=144, kernel_size=(5, 5), stride=(2, 2), groups=144, bias=None)
        self.block3a_bn_res1_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'block3a_bn_res1/FusedBatchNorm_1', num_features=144, eps=0.0010000000474974513, momentum=0.0)
        self.block3a_se_reduce_res1_convolution = self.__conv(
            2, name='block3a_se_reduce_res1/convolution', in_channels=144, out_channels=6, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.block3a_se_expand_res1_convolution = self.__conv(
            2, name='block3a_se_expand_res1/convolution', in_channels=6, out_channels=144, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.block3a_project_conv_res1_convolution = self.__conv(
            2, name='block3a_project_conv_res1/convolution', in_channels=144, out_channels=40, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.block3a_project_bn_res1_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'block3a_project_bn_res1/FusedBatchNorm_1', num_features=40, eps=0.0010000000474974513, momentum=0.0)
        self.block3b_expand_conv_res1_convolution = self.__conv(
            2, name='block3b_expand_conv_res1/convolution', in_channels=40, out_channels=240, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.block3b_expand_bn_res1_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'block3b_expand_bn_res1/FusedBatchNorm_1', num_features=240, eps=0.0010000000474974513, momentum=0.0)
        self.block3b_dwconv_res1_depthwise = self.__conv(
            2, name='block3b_dwconv_res1/depthwise', in_channels=240, out_channels=240, kernel_size=(5, 5), stride=(1, 1), groups=240, bias=None)
        self.block3b_bn_res1_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'block3b_bn_res1/FusedBatchNorm_1', num_features=240, eps=0.0010000000474974513, momentum=0.0)
        self.block3b_se_reduce_res1_convolution = self.__conv(
            2, name='block3b_se_reduce_res1/convolution', in_channels=240, out_channels=10, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.block3b_se_expand_res1_convolution = self.__conv(
            2, name='block3b_se_expand_res1/convolution', in_channels=10, out_channels=240, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.block3b_project_conv_res1_convolution = self.__conv(
            2, name='block3b_project_conv_res1/convolution', in_channels=240, out_channels=40, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.block3b_project_bn_res1_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'block3b_project_bn_res1/FusedBatchNorm_1', num_features=40, eps=0.0010000000474974513, momentum=0.0)
        self.pass1_block1_mbconv1_skeleton_conv1_convolution = self.__conv(
            2, name='pass1_block1_mbconv1_skeleton_conv1/convolution', in_channels=40, out_channels=240, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.pass1_block1_mbconv1_skeleton_conv1_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass1_block1_mbconv1_skeleton_conv1_bn/FusedBatchNorm_1', num_features=240, eps=0.0010000000474974513, momentum=0.0)
        self.pass1_block1_mbconv1_skeleton_dconv1_depthwise = self.__conv(
            2, name='pass1_block1_mbconv1_skeleton_dconv1/depthwise', in_channels=240, out_channels=240, kernel_size=(5, 5), stride=(1, 1), groups=240, bias=None)
        self.pass1_block1_mbconv1_skeleton_dconv1_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass1_block1_mbconv1_skeleton_dconv1_bn/FusedBatchNorm_1', num_features=240, eps=0.0010000000474974513, momentum=0.0)
        self.pass1_block1_mbconv1_skeleton_se_se_squeeze_conv_convolution = self.__conv(
            2, name='pass1_block1_mbconv1_skeleton_se_se_squeeze_conv/convolution', in_channels=240, out_channels=10, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.pass1_block1_mbconv1_skeleton_se_se_excite_conv_convolution = self.__conv(
            2, name='pass1_block1_mbconv1_skeleton_se_se_excite_conv/convolution', in_channels=10, out_channels=240, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.pass1_block1_mbconv1_skeleton_conv2_convolution = self.__conv(
            2, name='pass1_block1_mbconv1_skeleton_conv2/convolution', in_channels=240, out_channels=40, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.pass1_block1_mbconv1_skeleton_conv2_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass1_block1_mbconv1_skeleton_conv2_bn/FusedBatchNorm_1', num_features=40, eps=0.0010000000474974513, momentum=0.0)
        self.pass1_block1_mbconv2_skeleton_conv1_convolution = self.__conv(
            2, name='pass1_block1_mbconv2_skeleton_conv1/convolution', in_channels=40, out_channels=240, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.pass1_block1_mbconv2_skeleton_conv1_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass1_block1_mbconv2_skeleton_conv1_bn/FusedBatchNorm_1', num_features=240, eps=0.0010000000474974513, momentum=0.0)
        self.pass1_block1_mbconv2_skeleton_dconv1_depthwise = self.__conv(
            2, name='pass1_block1_mbconv2_skeleton_dconv1/depthwise', in_channels=240, out_channels=240, kernel_size=(5, 5), stride=(1, 1), groups=240, bias=None)
        self.pass1_block1_mbconv2_skeleton_dconv1_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass1_block1_mbconv2_skeleton_dconv1_bn/FusedBatchNorm_1', num_features=240, eps=0.0010000000474974513, momentum=0.0)
        self.pass1_block1_mbconv2_skeleton_se_se_squeeze_conv_convolution = self.__conv(
            2, name='pass1_block1_mbconv2_skeleton_se_se_squeeze_conv/convolution', in_channels=240, out_channels=10, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.pass1_block1_mbconv2_skeleton_se_se_excite_conv_convolution = self.__conv(
            2, name='pass1_block1_mbconv2_skeleton_se_se_excite_conv/convolution', in_channels=10, out_channels=240, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.pass1_block1_mbconv2_skeleton_conv2_convolution = self.__conv(
            2, name='pass1_block1_mbconv2_skeleton_conv2/convolution', in_channels=240, out_channels=40, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.pass1_block1_mbconv2_skeleton_conv2_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass1_block1_mbconv2_skeleton_conv2_bn/FusedBatchNorm_1', num_features=40, eps=0.0010000000474974513, momentum=0.0)
        self.pass1_block1_mbconv3_skeleton_conv1_convolution = self.__conv(
            2, name='pass1_block1_mbconv3_skeleton_conv1/convolution', in_channels=80, out_channels=240, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.pass1_block1_mbconv3_skeleton_conv1_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass1_block1_mbconv3_skeleton_conv1_bn/FusedBatchNorm_1', num_features=240, eps=0.0010000000474974513, momentum=0.0)
        self.pass1_block1_mbconv3_skeleton_dconv1_depthwise = self.__conv(
            2, name='pass1_block1_mbconv3_skeleton_dconv1/depthwise', in_channels=240, out_channels=240, kernel_size=(5, 5), stride=(1, 1), groups=240, bias=None)
        self.pass1_block1_mbconv3_skeleton_dconv1_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass1_block1_mbconv3_skeleton_dconv1_bn/FusedBatchNorm_1', num_features=240, eps=0.0010000000474974513, momentum=0.0)
        self.pass1_block1_mbconv3_skeleton_se_se_squeeze_conv_convolution = self.__conv(
            2, name='pass1_block1_mbconv3_skeleton_se_se_squeeze_conv/convolution', in_channels=240, out_channels=10, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.pass1_block1_mbconv3_skeleton_se_se_excite_conv_convolution = self.__conv(
            2, name='pass1_block1_mbconv3_skeleton_se_se_excite_conv/convolution', in_channels=10, out_channels=240, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.pass1_block1_mbconv3_skeleton_conv2_convolution = self.__conv(
            2, name='pass1_block1_mbconv3_skeleton_conv2/convolution', in_channels=240, out_channels=40, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.pass1_block1_mbconv3_skeleton_conv2_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass1_block1_mbconv3_skeleton_conv2_bn/FusedBatchNorm_1', num_features=40, eps=0.0010000000474974513, momentum=0.0)
        self.pass2_block1_mbconv1_detection1_conv1_convolution = self.__conv(
            2, name='pass2_block1_mbconv1_detection1_conv1/convolution', in_channels=160, out_channels=240, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.pass2_block1_mbconv1_detection1_conv1_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass2_block1_mbconv1_detection1_conv1_bn/FusedBatchNorm_1', num_features=240, eps=0.0010000000474974513, momentum=0.0)
        self.pass2_block1_mbconv1_detection1_dconv1_depthwise = self.__conv(
            2, name='pass2_block1_mbconv1_detection1_dconv1/depthwise', in_channels=240, out_channels=240, kernel_size=(5, 5), stride=(1, 1), groups=240, bias=None)
        self.pass2_block1_mbconv1_detection1_dconv1_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass2_block1_mbconv1_detection1_dconv1_bn/FusedBatchNorm_1', num_features=240, eps=0.0010000000474974513, momentum=0.0)
        self.pass2_block1_mbconv1_detection1_se_se_squeeze_conv_convolution = self.__conv(
            2, name='pass2_block1_mbconv1_detection1_se_se_squeeze_conv/convolution', in_channels=240, out_channels=10, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.pass2_block1_mbconv1_detection1_se_se_excite_conv_convolution = self.__conv(
            2, name='pass2_block1_mbconv1_detection1_se_se_excite_conv/convolution', in_channels=10, out_channels=240, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.pass2_block1_mbconv1_detection1_conv2_convolution = self.__conv(
            2, name='pass2_block1_mbconv1_detection1_conv2/convolution', in_channels=240, out_channels=40, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.pass2_block1_mbconv1_detection1_conv2_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass2_block1_mbconv1_detection1_conv2_bn/FusedBatchNorm_1', num_features=40, eps=0.0010000000474974513, momentum=0.0)
        self.pass2_block1_mbconv2_detection1_conv1_convolution = self.__conv(
            2, name='pass2_block1_mbconv2_detection1_conv1/convolution', in_channels=40, out_channels=240, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.pass2_block1_mbconv2_detection1_conv1_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass2_block1_mbconv2_detection1_conv1_bn/FusedBatchNorm_1', num_features=240, eps=0.0010000000474974513, momentum=0.0)
        self.pass2_block1_mbconv2_detection1_dconv1_depthwise = self.__conv(
            2, name='pass2_block1_mbconv2_detection1_dconv1/depthwise', in_channels=240, out_channels=240, kernel_size=(5, 5), stride=(1, 1), groups=240, bias=None)
        self.pass2_block1_mbconv2_detection1_dconv1_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass2_block1_mbconv2_detection1_dconv1_bn/FusedBatchNorm_1', num_features=240, eps=0.0010000000474974513, momentum=0.0)
        self.pass2_block1_mbconv2_detection1_se_se_squeeze_conv_convolution = self.__conv(
            2, name='pass2_block1_mbconv2_detection1_se_se_squeeze_conv/convolution', in_channels=240, out_channels=10, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.pass2_block1_mbconv2_detection1_se_se_excite_conv_convolution = self.__conv(
            2, name='pass2_block1_mbconv2_detection1_se_se_excite_conv/convolution', in_channels=10, out_channels=240, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.pass2_block1_mbconv2_detection1_conv2_convolution = self.__conv(
            2, name='pass2_block1_mbconv2_detection1_conv2/convolution', in_channels=240, out_channels=40, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.pass2_block1_mbconv2_detection1_conv2_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass2_block1_mbconv2_detection1_conv2_bn/FusedBatchNorm_1', num_features=40, eps=0.0010000000474974513, momentum=0.0)
        self.pass2_block1_mbconv3_detection1_conv1_convolution = self.__conv(
            2, name='pass2_block1_mbconv3_detection1_conv1/convolution', in_channels=80, out_channels=240, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.pass2_block1_mbconv3_detection1_conv1_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass2_block1_mbconv3_detection1_conv1_bn/FusedBatchNorm_1', num_features=240, eps=0.0010000000474974513, momentum=0.0)
        self.pass2_block1_mbconv3_detection1_dconv1_depthwise = self.__conv(
            2, name='pass2_block1_mbconv3_detection1_dconv1/depthwise', in_channels=240, out_channels=240, kernel_size=(5, 5), stride=(1, 1), groups=240, bias=None)
        self.pass2_block1_mbconv3_detection1_dconv1_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass2_block1_mbconv3_detection1_dconv1_bn/FusedBatchNorm_1', num_features=240, eps=0.0010000000474974513, momentum=0.0)
        self.pass2_block1_mbconv3_detection1_se_se_squeeze_conv_convolution = self.__conv(
            2, name='pass2_block1_mbconv3_detection1_se_se_squeeze_conv/convolution', in_channels=240, out_channels=10, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.pass2_block1_mbconv3_detection1_se_se_excite_conv_convolution = self.__conv(
            2, name='pass2_block1_mbconv3_detection1_se_se_excite_conv/convolution', in_channels=10, out_channels=240, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.pass2_block1_mbconv3_detection1_conv2_convolution = self.__conv(
            2, name='pass2_block1_mbconv3_detection1_conv2/convolution', in_channels=240, out_channels=40, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.pass2_block1_mbconv3_detection1_conv2_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass2_block1_mbconv3_detection1_conv2_bn/FusedBatchNorm_1', num_features=40, eps=0.0010000000474974513, momentum=0.0)
        self.pass3_block1_mbconv1_detection2_conv1_convolution = self.__conv(
            2, name='pass3_block1_mbconv1_detection2_conv1/convolution', in_channels=160, out_channels=240, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.pass3_block1_mbconv1_detection2_conv1_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass3_block1_mbconv1_detection2_conv1_bn/FusedBatchNorm_1', num_features=240, eps=0.0010000000474974513, momentum=0.0)
        self.pass3_block1_mbconv1_detection2_dconv1_depthwise = self.__conv(
            2, name='pass3_block1_mbconv1_detection2_dconv1/depthwise', in_channels=240, out_channels=240, kernel_size=(5, 5), stride=(1, 1), groups=240, bias=None)
        self.pass3_block1_mbconv1_detection2_dconv1_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass3_block1_mbconv1_detection2_dconv1_bn/FusedBatchNorm_1', num_features=240, eps=0.0010000000474974513, momentum=0.0)
        self.pass3_block1_mbconv1_detection2_se_se_squeeze_conv_convolution = self.__conv(
            2, name='pass3_block1_mbconv1_detection2_se_se_squeeze_conv/convolution', in_channels=240, out_channels=10, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.pass3_block1_mbconv1_detection2_se_se_excite_conv_convolution = self.__conv(
            2, name='pass3_block1_mbconv1_detection2_se_se_excite_conv/convolution', in_channels=10, out_channels=240, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.pass3_block1_mbconv1_detection2_conv2_convolution = self.__conv(
            2, name='pass3_block1_mbconv1_detection2_conv2/convolution', in_channels=240, out_channels=40, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.pass3_block1_mbconv1_detection2_conv2_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass3_block1_mbconv1_detection2_conv2_bn/FusedBatchNorm_1', num_features=40, eps=0.0010000000474974513, momentum=0.0)
        self.pass3_block1_mbconv2_detection2_conv1_convolution = self.__conv(
            2, name='pass3_block1_mbconv2_detection2_conv1/convolution', in_channels=40, out_channels=240, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.pass3_block1_mbconv2_detection2_conv1_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass3_block1_mbconv2_detection2_conv1_bn/FusedBatchNorm_1', num_features=240, eps=0.0010000000474974513, momentum=0.0)
        self.pass3_block1_mbconv2_detection2_dconv1_depthwise = self.__conv(
            2, name='pass3_block1_mbconv2_detection2_dconv1/depthwise', in_channels=240, out_channels=240, kernel_size=(5, 5), stride=(1, 1), groups=240, bias=None)
        self.pass3_block1_mbconv2_detection2_dconv1_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass3_block1_mbconv2_detection2_dconv1_bn/FusedBatchNorm_1', num_features=240, eps=0.0010000000474974513, momentum=0.0)
        self.pass3_block1_mbconv2_detection2_se_se_squeeze_conv_convolution = self.__conv(
            2, name='pass3_block1_mbconv2_detection2_se_se_squeeze_conv/convolution', in_channels=240, out_channels=10, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.pass3_block1_mbconv2_detection2_se_se_excite_conv_convolution = self.__conv(
            2, name='pass3_block1_mbconv2_detection2_se_se_excite_conv/convolution', in_channels=10, out_channels=240, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.pass3_block1_mbconv2_detection2_conv2_convolution = self.__conv(
            2, name='pass3_block1_mbconv2_detection2_conv2/convolution', in_channels=240, out_channels=40, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.pass3_block1_mbconv2_detection2_conv2_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass3_block1_mbconv2_detection2_conv2_bn/FusedBatchNorm_1', num_features=40, eps=0.0010000000474974513, momentum=0.0)
        self.pass3_block1_mbconv3_detection2_conv1_convolution = self.__conv(
            2, name='pass3_block1_mbconv3_detection2_conv1/convolution', in_channels=80, out_channels=240, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.pass3_block1_mbconv3_detection2_conv1_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass3_block1_mbconv3_detection2_conv1_bn/FusedBatchNorm_1', num_features=240, eps=0.0010000000474974513, momentum=0.0)
        self.pass3_block1_mbconv3_detection2_dconv1_depthwise = self.__conv(
            2, name='pass3_block1_mbconv3_detection2_dconv1/depthwise', in_channels=240, out_channels=240, kernel_size=(5, 5), stride=(1, 1), groups=240, bias=None)
        self.pass3_block1_mbconv3_detection2_dconv1_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass3_block1_mbconv3_detection2_dconv1_bn/FusedBatchNorm_1', num_features=240, eps=0.0010000000474974513, momentum=0.0)
        self.pass3_block1_mbconv3_detection2_se_se_squeeze_conv_convolution = self.__conv(
            2, name='pass3_block1_mbconv3_detection2_se_se_squeeze_conv/convolution', in_channels=240, out_channels=10, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.pass3_block1_mbconv3_detection2_se_se_excite_conv_convolution = self.__conv(
            2, name='pass3_block1_mbconv3_detection2_se_se_excite_conv/convolution', in_channels=10, out_channels=240, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)
        self.pass3_block1_mbconv3_detection2_conv2_convolution = self.__conv(
            2, name='pass3_block1_mbconv3_detection2_conv2/convolution', in_channels=240, out_channels=40, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=None)
        self.pass3_block1_mbconv3_detection2_conv2_bn_FusedBatchNorm_1 = self.__batch_normalization(
            2, 'pass3_block1_mbconv3_detection2_conv2_bn/FusedBatchNorm_1', num_features=40, eps=0.0010000000474974513, momentum=0.0)
        self.pass3_detection2_confs_convolution = self.__conv(
            2, name='pass3_detection2_confs/convolution', in_channels=120, out_channels=16, kernel_size=(1, 1), stride=(1, 1), groups=1, bias=True)

    def forward(self, x):
        self.pass1_block1_mbconv1_skeleton_conv1_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        self.pass1_block1_mbconv1_skeleton_dconv1_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        self.pass1_block1_mbconv1_skeleton_se_se_squeeze_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        self.pass1_block1_mbconv2_skeleton_conv1_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        self.pass1_block1_mbconv2_skeleton_dconv1_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        self.pass1_block1_mbconv2_skeleton_se_se_squeeze_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        self.pass1_block1_mbconv3_skeleton_conv1_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        self.pass1_block1_mbconv3_skeleton_dconv1_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        self.pass1_block1_mbconv3_skeleton_se_se_squeeze_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        self.pass2_block1_mbconv1_detection1_conv1_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        self.pass2_block1_mbconv1_detection1_dconv1_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        self.pass2_block1_mbconv1_detection1_se_se_squeeze_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        self.pass2_block1_mbconv2_detection1_conv1_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        self.pass2_block1_mbconv2_detection1_dconv1_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        self.pass2_block1_mbconv2_detection1_se_se_squeeze_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        self.pass2_block1_mbconv3_detection1_conv1_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        self.pass2_block1_mbconv3_detection1_dconv1_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        self.pass2_block1_mbconv3_detection1_se_se_squeeze_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        self.pass3_block1_mbconv1_detection2_conv1_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        self.pass3_block1_mbconv1_detection2_dconv1_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        self.pass3_block1_mbconv1_detection2_se_se_squeeze_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        self.pass3_block1_mbconv2_detection2_conv1_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        self.pass3_block1_mbconv2_detection2_dconv1_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        self.pass3_block1_mbconv2_detection2_se_se_squeeze_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        self.pass3_block1_mbconv3_detection2_conv1_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        self.pass3_block1_mbconv3_detection2_dconv1_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        self.pass3_block1_mbconv3_detection2_se_se_squeeze_eswish_mul_x = torch.autograd.Variable(
            torch.Tensor([1.25]), requires_grad=False)
        stem_conv_res1_convolution_pad = F.pad(x, (0, 1, 0, 1))
        stem_conv_res1_convolution = self.stem_conv_res1_convolution(stem_conv_res1_convolution_pad)
        stem_bn_res1_FusedBatchNorm_1 = self.stem_bn_res1_FusedBatchNorm_1(
            stem_conv_res1_convolution)
        stem_activation_res1_Sigmoid = F.sigmoid(stem_bn_res1_FusedBatchNorm_1)
        stem_activation_res1_mul = stem_bn_res1_FusedBatchNorm_1 * stem_activation_res1_Sigmoid
        block1a_dwconv_res1_depthwise_pad = F.pad(stem_activation_res1_mul, (1, 1, 1, 1))
        block1a_dwconv_res1_depthwise = self.block1a_dwconv_res1_depthwise(
            block1a_dwconv_res1_depthwise_pad)
        block1a_bn_res1_FusedBatchNorm_1 = self.block1a_bn_res1_FusedBatchNorm_1(
            block1a_dwconv_res1_depthwise)
        block1a_activation_res1_Sigmoid = F.sigmoid(block1a_bn_res1_FusedBatchNorm_1)
        block1a_activation_res1_mul = block1a_bn_res1_FusedBatchNorm_1 * block1a_activation_res1_Sigmoid
        block1a_se_squeeze_res1_Mean = torch.mean(block1a_activation_res1_mul, 3, False)
        block1a_se_squeeze_res1_Mean = torch.mean(block1a_se_squeeze_res1_Mean, 2, False)
        block1a_se_reshape_res1_Shape = torch.Tensor(list(block1a_se_squeeze_res1_Mean.size()))
        block1a_se_reshape_res1_Reshape = torch.reshape(
            input=block1a_se_squeeze_res1_Mean, shape=(-1, 32, 1, 1))  # (-1,1,1,32))
        block1a_se_reshape_res1_strided_slice = block1a_se_reshape_res1_Shape[0:1]
        block1a_se_reduce_res1_convolution = self.block1a_se_reduce_res1_convolution(
            block1a_se_reshape_res1_Reshape)
        block1a_se_reduce_swish_res1_Sigmoid = F.sigmoid(block1a_se_reduce_res1_convolution)
        block1a_se_reduce_swish_res1_mul = block1a_se_reduce_res1_convolution * block1a_se_reduce_swish_res1_Sigmoid
        block1a_se_expand_res1_convolution = self.block1a_se_expand_res1_convolution(
            block1a_se_reduce_swish_res1_mul)
        block1a_se_expand_res1_Sigmoid = F.sigmoid(block1a_se_expand_res1_convolution)
        block1a_se_excite_res1_mul = block1a_activation_res1_mul * block1a_se_expand_res1_Sigmoid
        block1a_project_conv_res1_convolution = self.block1a_project_conv_res1_convolution(
            block1a_se_excite_res1_mul)
        block1a_project_bn_res1_FusedBatchNorm_1 = self.block1a_project_bn_res1_FusedBatchNorm_1(
            block1a_project_conv_res1_convolution)
        block2a_expand_conv_res1_convolution = self.block2a_expand_conv_res1_convolution(
            block1a_project_bn_res1_FusedBatchNorm_1)
        block2a_expand_bn_res1_FusedBatchNorm_1 = self.block2a_expand_bn_res1_FusedBatchNorm_1(
            block2a_expand_conv_res1_convolution)
        block2a_expand_activation_res1_Sigmoid = F.sigmoid(block2a_expand_bn_res1_FusedBatchNorm_1)
        block2a_expand_activation_res1_mul = block2a_expand_bn_res1_FusedBatchNorm_1 * \
            block2a_expand_activation_res1_Sigmoid
        block2a_dwconv_res1_depthwise_pad = F.pad(block2a_expand_activation_res1_mul, (0, 1, 0, 1))
        block2a_dwconv_res1_depthwise = self.block2a_dwconv_res1_depthwise(
            block2a_dwconv_res1_depthwise_pad)
        block2a_bn_res1_FusedBatchNorm_1 = self.block2a_bn_res1_FusedBatchNorm_1(
            block2a_dwconv_res1_depthwise)
        block2a_activation_res1_Sigmoid = F.sigmoid(block2a_bn_res1_FusedBatchNorm_1)
        block2a_activation_res1_mul = block2a_bn_res1_FusedBatchNorm_1 * block2a_activation_res1_Sigmoid
        block2a_se_squeeze_res1_Mean = torch.mean(block2a_activation_res1_mul, 3, False)
        block2a_se_squeeze_res1_Mean = torch.mean(block2a_se_squeeze_res1_Mean, 2, False)
        block2a_se_reshape_res1_Shape = torch.Tensor(list(block2a_se_squeeze_res1_Mean.size()))
        block2a_se_reshape_res1_Reshape = torch.reshape(
            input=block2a_se_squeeze_res1_Mean, shape=(-1, 96, 1, 1))  # (-1,1,1,96))
        block2a_se_reshape_res1_strided_slice = block2a_se_reshape_res1_Shape[0:1]
        block2a_se_reduce_res1_convolution = self.block2a_se_reduce_res1_convolution(
            block2a_se_reshape_res1_Reshape)
        block2a_se_reduce_swish_res1_Sigmoid = F.sigmoid(block2a_se_reduce_res1_convolution)
        block2a_se_reduce_swish_res1_mul = block2a_se_reduce_res1_convolution * block2a_se_reduce_swish_res1_Sigmoid
        block2a_se_expand_res1_convolution = self.block2a_se_expand_res1_convolution(
            block2a_se_reduce_swish_res1_mul)
        block2a_se_expand_res1_Sigmoid = F.sigmoid(block2a_se_expand_res1_convolution)
        block2a_se_excite_res1_mul = block2a_activation_res1_mul * block2a_se_expand_res1_Sigmoid
        block2a_project_conv_res1_convolution = self.block2a_project_conv_res1_convolution(
            block2a_se_excite_res1_mul)
        block2a_project_bn_res1_FusedBatchNorm_1 = self.block2a_project_bn_res1_FusedBatchNorm_1(
            block2a_project_conv_res1_convolution)
        block2b_expand_conv_res1_convolution = self.block2b_expand_conv_res1_convolution(
            block2a_project_bn_res1_FusedBatchNorm_1)
        block2b_expand_bn_res1_FusedBatchNorm_1 = self.block2b_expand_bn_res1_FusedBatchNorm_1(
            block2b_expand_conv_res1_convolution)
        block2b_expand_activation_res1_Sigmoid = F.sigmoid(block2b_expand_bn_res1_FusedBatchNorm_1)
        block2b_expand_activation_res1_mul = block2b_expand_bn_res1_FusedBatchNorm_1 * \
            block2b_expand_activation_res1_Sigmoid
        block2b_dwconv_res1_depthwise_pad = F.pad(block2b_expand_activation_res1_mul, (1, 1, 1, 1))
        block2b_dwconv_res1_depthwise = self.block2b_dwconv_res1_depthwise(
            block2b_dwconv_res1_depthwise_pad)
        block2b_bn_res1_FusedBatchNorm_1 = self.block2b_bn_res1_FusedBatchNorm_1(
            block2b_dwconv_res1_depthwise)
        block2b_activation_res1_Sigmoid = F.sigmoid(block2b_bn_res1_FusedBatchNorm_1)
        block2b_activation_res1_mul = block2b_bn_res1_FusedBatchNorm_1 * block2b_activation_res1_Sigmoid
        block2b_se_squeeze_res1_Mean = torch.mean(block2b_activation_res1_mul, 3, False)
        block2b_se_squeeze_res1_Mean = torch.mean(block2b_se_squeeze_res1_Mean, 2, False)
        block2b_se_reshape_res1_Shape = torch.Tensor(list(block2b_se_squeeze_res1_Mean.size()))
        block2b_se_reshape_res1_Reshape = torch.reshape(
            input=block2b_se_squeeze_res1_Mean, shape=(-1, 144, 1, 1))  # (-1,1,1,144))
        block2b_se_reshape_res1_strided_slice = block2b_se_reshape_res1_Shape[0:1]
        block2b_se_reduce_res1_convolution = self.block2b_se_reduce_res1_convolution(
            block2b_se_reshape_res1_Reshape)
        block2b_se_reduce_swish_res1_Sigmoid = F.sigmoid(block2b_se_reduce_res1_convolution)
        block2b_se_reduce_swish_res1_mul = block2b_se_reduce_res1_convolution * block2b_se_reduce_swish_res1_Sigmoid
        block2b_se_expand_res1_convolution = self.block2b_se_expand_res1_convolution(
            block2b_se_reduce_swish_res1_mul)
        block2b_se_expand_res1_Sigmoid = F.sigmoid(block2b_se_expand_res1_convolution)
        block2b_se_excite_res1_mul = block2b_activation_res1_mul * block2b_se_expand_res1_Sigmoid
        block2b_project_conv_res1_convolution = self.block2b_project_conv_res1_convolution(
            block2b_se_excite_res1_mul)
        block2b_project_bn_res1_FusedBatchNorm_1 = self.block2b_project_bn_res1_FusedBatchNorm_1(
            block2b_project_conv_res1_convolution)
        block2b_add_res1_add = block2b_project_bn_res1_FusedBatchNorm_1 + block2a_project_bn_res1_FusedBatchNorm_1
        block3a_expand_conv_res1_convolution = self.block3a_expand_conv_res1_convolution(
            block2b_add_res1_add)
        block3a_expand_bn_res1_FusedBatchNorm_1 = self.block3a_expand_bn_res1_FusedBatchNorm_1(
            block3a_expand_conv_res1_convolution)
        block3a_expand_activation_res1_Sigmoid = F.sigmoid(block3a_expand_bn_res1_FusedBatchNorm_1)
        block3a_expand_activation_res1_mul = block3a_expand_bn_res1_FusedBatchNorm_1 * \
            block3a_expand_activation_res1_Sigmoid
        block3a_dwconv_res1_depthwise_pad = F.pad(block3a_expand_activation_res1_mul, (1, 2, 1, 2))
        block3a_dwconv_res1_depthwise = self.block3a_dwconv_res1_depthwise(
            block3a_dwconv_res1_depthwise_pad)
        block3a_bn_res1_FusedBatchNorm_1 = self.block3a_bn_res1_FusedBatchNorm_1(
            block3a_dwconv_res1_depthwise)
        block3a_activation_res1_Sigmoid = F.sigmoid(block3a_bn_res1_FusedBatchNorm_1)
        block3a_activation_res1_mul = block3a_bn_res1_FusedBatchNorm_1 * block3a_activation_res1_Sigmoid
        block3a_se_squeeze_res1_Mean = torch.mean(block3a_activation_res1_mul, 3, False)
        block3a_se_squeeze_res1_Mean = torch.mean(block3a_se_squeeze_res1_Mean, 2, False)
        block3a_se_reshape_res1_Shape = torch.Tensor(list(block3a_se_squeeze_res1_Mean.size()))
        block3a_se_reshape_res1_Reshape = torch.reshape(
            input=block3a_se_squeeze_res1_Mean, shape=(-1, 144, 1, 1))  # (-1,1,1,144))
        block3a_se_reshape_res1_strided_slice = block3a_se_reshape_res1_Shape[0:1]
        block3a_se_reduce_res1_convolution = self.block3a_se_reduce_res1_convolution(
            block3a_se_reshape_res1_Reshape)
        block3a_se_reduce_swish_res1_Sigmoid = F.sigmoid(block3a_se_reduce_res1_convolution)
        block3a_se_reduce_swish_res1_mul = block3a_se_reduce_res1_convolution * block3a_se_reduce_swish_res1_Sigmoid
        block3a_se_expand_res1_convolution = self.block3a_se_expand_res1_convolution(
            block3a_se_reduce_swish_res1_mul)
        block3a_se_expand_res1_Sigmoid = F.sigmoid(block3a_se_expand_res1_convolution)
        block3a_se_excite_res1_mul = block3a_activation_res1_mul * block3a_se_expand_res1_Sigmoid
        block3a_project_conv_res1_convolution = self.block3a_project_conv_res1_convolution(
            block3a_se_excite_res1_mul)
        block3a_project_bn_res1_FusedBatchNorm_1 = self.block3a_project_bn_res1_FusedBatchNorm_1(
            block3a_project_conv_res1_convolution)
        block3b_expand_conv_res1_convolution = self.block3b_expand_conv_res1_convolution(
            block3a_project_bn_res1_FusedBatchNorm_1)
        block3b_expand_bn_res1_FusedBatchNorm_1 = self.block3b_expand_bn_res1_FusedBatchNorm_1(
            block3b_expand_conv_res1_convolution)
        block3b_expand_activation_res1_Sigmoid = F.sigmoid(block3b_expand_bn_res1_FusedBatchNorm_1)
        block3b_expand_activation_res1_mul = block3b_expand_bn_res1_FusedBatchNorm_1 * \
            block3b_expand_activation_res1_Sigmoid
        block3b_dwconv_res1_depthwise_pad = F.pad(block3b_expand_activation_res1_mul, (2, 2, 2, 2))
        block3b_dwconv_res1_depthwise = self.block3b_dwconv_res1_depthwise(
            block3b_dwconv_res1_depthwise_pad)
        block3b_bn_res1_FusedBatchNorm_1 = self.block3b_bn_res1_FusedBatchNorm_1(
            block3b_dwconv_res1_depthwise)
        block3b_activation_res1_Sigmoid = F.sigmoid(block3b_bn_res1_FusedBatchNorm_1)
        block3b_activation_res1_mul = block3b_bn_res1_FusedBatchNorm_1 * block3b_activation_res1_Sigmoid
        block3b_se_squeeze_res1_Mean = torch.mean(block3b_activation_res1_mul, 3, False)
        block3b_se_squeeze_res1_Mean = torch.mean(block3b_se_squeeze_res1_Mean, 2, False)
        block3b_se_reshape_res1_Shape = torch.Tensor(list(block3b_se_squeeze_res1_Mean.size()))
        block3b_se_reshape_res1_Reshape = torch.reshape(
            input=block3b_se_squeeze_res1_Mean, shape=(-1, 240, 1, 1))  # (-1,1,1,240))
        block3b_se_reshape_res1_strided_slice = block3b_se_reshape_res1_Shape[0:1]
        block3b_se_reduce_res1_convolution = self.block3b_se_reduce_res1_convolution(
            block3b_se_reshape_res1_Reshape)
        block3b_se_reduce_swish_res1_Sigmoid = F.sigmoid(block3b_se_reduce_res1_convolution)
        block3b_se_reduce_swish_res1_mul = block3b_se_reduce_res1_convolution * block3b_se_reduce_swish_res1_Sigmoid
        block3b_se_expand_res1_convolution = self.block3b_se_expand_res1_convolution(
            block3b_se_reduce_swish_res1_mul)
        block3b_se_expand_res1_Sigmoid = F.sigmoid(block3b_se_expand_res1_convolution)
        block3b_se_excite_res1_mul = block3b_activation_res1_mul * block3b_se_expand_res1_Sigmoid
        block3b_project_conv_res1_convolution = self.block3b_project_conv_res1_convolution(
            block3b_se_excite_res1_mul)
        block3b_project_bn_res1_FusedBatchNorm_1 = self.block3b_project_bn_res1_FusedBatchNorm_1(
            block3b_project_conv_res1_convolution)
        block3b_add_res1_add = block3b_project_bn_res1_FusedBatchNorm_1 + block3a_project_bn_res1_FusedBatchNorm_1
        pass1_block1_mbconv1_skeleton_conv1_convolution = self.pass1_block1_mbconv1_skeleton_conv1_convolution(
            block3b_add_res1_add)
        pass1_block1_mbconv1_skeleton_conv1_bn_FusedBatchNorm_1 = self.pass1_block1_mbconv1_skeleton_conv1_bn_FusedBatchNorm_1(
            pass1_block1_mbconv1_skeleton_conv1_convolution)
        pass1_block1_mbconv1_skeleton_conv1_eswish_mul = self.pass1_block1_mbconv1_skeleton_conv1_eswish_mul_x * \
            pass1_block1_mbconv1_skeleton_conv1_bn_FusedBatchNorm_1
        pass1_block1_mbconv1_skeleton_conv1_eswish_Sigmoid = F.sigmoid(
            pass1_block1_mbconv1_skeleton_conv1_bn_FusedBatchNorm_1)
        pass1_block1_mbconv1_skeleton_conv1_eswish_mul_1 = pass1_block1_mbconv1_skeleton_conv1_eswish_mul * \
            pass1_block1_mbconv1_skeleton_conv1_eswish_Sigmoid
        pass1_block1_mbconv1_skeleton_dconv1_depthwise_pad = F.pad(
            pass1_block1_mbconv1_skeleton_conv1_eswish_mul_1, (2, 2, 2, 2))
        pass1_block1_mbconv1_skeleton_dconv1_depthwise = self.pass1_block1_mbconv1_skeleton_dconv1_depthwise(
            pass1_block1_mbconv1_skeleton_dconv1_depthwise_pad)
        pass1_block1_mbconv1_skeleton_dconv1_bn_FusedBatchNorm_1 = self.pass1_block1_mbconv1_skeleton_dconv1_bn_FusedBatchNorm_1(
            pass1_block1_mbconv1_skeleton_dconv1_depthwise)
        pass1_block1_mbconv1_skeleton_dconv1_eswish_mul = self.pass1_block1_mbconv1_skeleton_dconv1_eswish_mul_x * \
            pass1_block1_mbconv1_skeleton_dconv1_bn_FusedBatchNorm_1
        pass1_block1_mbconv1_skeleton_dconv1_eswish_Sigmoid = F.sigmoid(
            pass1_block1_mbconv1_skeleton_dconv1_bn_FusedBatchNorm_1)
        pass1_block1_mbconv1_skeleton_dconv1_eswish_mul_1 = pass1_block1_mbconv1_skeleton_dconv1_eswish_mul * \
            pass1_block1_mbconv1_skeleton_dconv1_eswish_Sigmoid
        pass1_block1_mbconv1_skeleton_se_se_squeeze_lambda_Mean = torch.mean(
            pass1_block1_mbconv1_skeleton_dconv1_eswish_mul_1, 3, True)
        pass1_block1_mbconv1_skeleton_se_se_squeeze_lambda_Mean = torch.mean(
            pass1_block1_mbconv1_skeleton_se_se_squeeze_lambda_Mean, 2, True)
        pass1_block1_mbconv1_skeleton_se_se_squeeze_conv_convolution = self.pass1_block1_mbconv1_skeleton_se_se_squeeze_conv_convolution(
            pass1_block1_mbconv1_skeleton_se_se_squeeze_lambda_Mean)
        pass1_block1_mbconv1_skeleton_se_se_squeeze_eswish_mul = self.pass1_block1_mbconv1_skeleton_se_se_squeeze_eswish_mul_x * \
            pass1_block1_mbconv1_skeleton_se_se_squeeze_conv_convolution
        pass1_block1_mbconv1_skeleton_se_se_squeeze_eswish_Sigmoid = F.sigmoid(
            pass1_block1_mbconv1_skeleton_se_se_squeeze_conv_convolution)
        pass1_block1_mbconv1_skeleton_se_se_squeeze_eswish_mul_1 = pass1_block1_mbconv1_skeleton_se_se_squeeze_eswish_mul * \
            pass1_block1_mbconv1_skeleton_se_se_squeeze_eswish_Sigmoid
        pass1_block1_mbconv1_skeleton_se_se_excite_conv_convolution = self.pass1_block1_mbconv1_skeleton_se_se_excite_conv_convolution(
            pass1_block1_mbconv1_skeleton_se_se_squeeze_eswish_mul_1)
        pass1_block1_mbconv1_skeleton_se_se_excite_sigmoid_Sigmoid = F.sigmoid(
            pass1_block1_mbconv1_skeleton_se_se_excite_conv_convolution)
        pass1_block1_mbconv1_skeleton_se_se_multiply_mul = pass1_block1_mbconv1_skeleton_se_se_excite_sigmoid_Sigmoid * \
            pass1_block1_mbconv1_skeleton_dconv1_eswish_mul_1
        pass1_block1_mbconv1_skeleton_conv2_convolution = self.pass1_block1_mbconv1_skeleton_conv2_convolution(
            pass1_block1_mbconv1_skeleton_se_se_multiply_mul)
        pass1_block1_mbconv1_skeleton_conv2_bn_FusedBatchNorm_1 = self.pass1_block1_mbconv1_skeleton_conv2_bn_FusedBatchNorm_1(
            pass1_block1_mbconv1_skeleton_conv2_convolution)
        pass1_block1_mbconv2_skeleton_conv1_convolution = self.pass1_block1_mbconv2_skeleton_conv1_convolution(
            pass1_block1_mbconv1_skeleton_conv2_bn_FusedBatchNorm_1)
        pass1_block1_mbconv2_skeleton_conv1_bn_FusedBatchNorm_1 = self.pass1_block1_mbconv2_skeleton_conv1_bn_FusedBatchNorm_1(
            pass1_block1_mbconv2_skeleton_conv1_convolution)
        pass1_block1_mbconv2_skeleton_conv1_eswish_mul = self.pass1_block1_mbconv2_skeleton_conv1_eswish_mul_x * \
            pass1_block1_mbconv2_skeleton_conv1_bn_FusedBatchNorm_1
        pass1_block1_mbconv2_skeleton_conv1_eswish_Sigmoid = F.sigmoid(
            pass1_block1_mbconv2_skeleton_conv1_bn_FusedBatchNorm_1)
        pass1_block1_mbconv2_skeleton_conv1_eswish_mul_1 = pass1_block1_mbconv2_skeleton_conv1_eswish_mul * \
            pass1_block1_mbconv2_skeleton_conv1_eswish_Sigmoid
        pass1_block1_mbconv2_skeleton_dconv1_depthwise_pad = F.pad(
            pass1_block1_mbconv2_skeleton_conv1_eswish_mul_1, (2, 2, 2, 2))
        pass1_block1_mbconv2_skeleton_dconv1_depthwise = self.pass1_block1_mbconv2_skeleton_dconv1_depthwise(
            pass1_block1_mbconv2_skeleton_dconv1_depthwise_pad)
        pass1_block1_mbconv2_skeleton_dconv1_bn_FusedBatchNorm_1 = self.pass1_block1_mbconv2_skeleton_dconv1_bn_FusedBatchNorm_1(
            pass1_block1_mbconv2_skeleton_dconv1_depthwise)
        pass1_block1_mbconv2_skeleton_dconv1_eswish_mul = self.pass1_block1_mbconv2_skeleton_dconv1_eswish_mul_x * \
            pass1_block1_mbconv2_skeleton_dconv1_bn_FusedBatchNorm_1
        pass1_block1_mbconv2_skeleton_dconv1_eswish_Sigmoid = F.sigmoid(
            pass1_block1_mbconv2_skeleton_dconv1_bn_FusedBatchNorm_1)
        pass1_block1_mbconv2_skeleton_dconv1_eswish_mul_1 = pass1_block1_mbconv2_skeleton_dconv1_eswish_mul * \
            pass1_block1_mbconv2_skeleton_dconv1_eswish_Sigmoid
        pass1_block1_mbconv2_skeleton_se_se_squeeze_lambda_Mean = torch.mean(
            pass1_block1_mbconv2_skeleton_dconv1_eswish_mul_1, 3, True)
        pass1_block1_mbconv2_skeleton_se_se_squeeze_lambda_Mean = torch.mean(
            pass1_block1_mbconv2_skeleton_se_se_squeeze_lambda_Mean, 2, True)
        pass1_block1_mbconv2_skeleton_se_se_squeeze_conv_convolution = self.pass1_block1_mbconv2_skeleton_se_se_squeeze_conv_convolution(
            pass1_block1_mbconv2_skeleton_se_se_squeeze_lambda_Mean)
        pass1_block1_mbconv2_skeleton_se_se_squeeze_eswish_mul = self.pass1_block1_mbconv2_skeleton_se_se_squeeze_eswish_mul_x * \
            pass1_block1_mbconv2_skeleton_se_se_squeeze_conv_convolution
        pass1_block1_mbconv2_skeleton_se_se_squeeze_eswish_Sigmoid = F.sigmoid(
            pass1_block1_mbconv2_skeleton_se_se_squeeze_conv_convolution)
        pass1_block1_mbconv2_skeleton_se_se_squeeze_eswish_mul_1 = pass1_block1_mbconv2_skeleton_se_se_squeeze_eswish_mul * \
            pass1_block1_mbconv2_skeleton_se_se_squeeze_eswish_Sigmoid
        pass1_block1_mbconv2_skeleton_se_se_excite_conv_convolution = self.pass1_block1_mbconv2_skeleton_se_se_excite_conv_convolution(
            pass1_block1_mbconv2_skeleton_se_se_squeeze_eswish_mul_1)
        pass1_block1_mbconv2_skeleton_se_se_excite_sigmoid_Sigmoid = F.sigmoid(
            pass1_block1_mbconv2_skeleton_se_se_excite_conv_convolution)
        pass1_block1_mbconv2_skeleton_se_se_multiply_mul = pass1_block1_mbconv2_skeleton_se_se_excite_sigmoid_Sigmoid * \
            pass1_block1_mbconv2_skeleton_dconv1_eswish_mul_1
        pass1_block1_mbconv2_skeleton_conv2_convolution = self.pass1_block1_mbconv2_skeleton_conv2_convolution(
            pass1_block1_mbconv2_skeleton_se_se_multiply_mul)
        pass1_block1_mbconv2_skeleton_conv2_bn_FusedBatchNorm_1 = self.pass1_block1_mbconv2_skeleton_conv2_bn_FusedBatchNorm_1(
            pass1_block1_mbconv2_skeleton_conv2_convolution)
        pass1_block1_mbconv2_skeleton_dense_concat = torch.cat(
            (pass1_block1_mbconv2_skeleton_conv2_bn_FusedBatchNorm_1, pass1_block1_mbconv1_skeleton_conv2_bn_FusedBatchNorm_1), 1)
        pass1_block1_mbconv3_skeleton_conv1_convolution = self.pass1_block1_mbconv3_skeleton_conv1_convolution(
            pass1_block1_mbconv2_skeleton_dense_concat)
        pass1_block1_mbconv3_skeleton_conv1_bn_FusedBatchNorm_1 = self.pass1_block1_mbconv3_skeleton_conv1_bn_FusedBatchNorm_1(
            pass1_block1_mbconv3_skeleton_conv1_convolution)
        pass1_block1_mbconv3_skeleton_conv1_eswish_mul = self.pass1_block1_mbconv3_skeleton_conv1_eswish_mul_x * \
            pass1_block1_mbconv3_skeleton_conv1_bn_FusedBatchNorm_1
        pass1_block1_mbconv3_skeleton_conv1_eswish_Sigmoid = F.sigmoid(
            pass1_block1_mbconv3_skeleton_conv1_bn_FusedBatchNorm_1)
        pass1_block1_mbconv3_skeleton_conv1_eswish_mul_1 = pass1_block1_mbconv3_skeleton_conv1_eswish_mul * \
            pass1_block1_mbconv3_skeleton_conv1_eswish_Sigmoid
        pass1_block1_mbconv3_skeleton_dconv1_depthwise_pad = F.pad(
            pass1_block1_mbconv3_skeleton_conv1_eswish_mul_1, (2, 2, 2, 2))
        pass1_block1_mbconv3_skeleton_dconv1_depthwise = self.pass1_block1_mbconv3_skeleton_dconv1_depthwise(
            pass1_block1_mbconv3_skeleton_dconv1_depthwise_pad)
        pass1_block1_mbconv3_skeleton_dconv1_bn_FusedBatchNorm_1 = self.pass1_block1_mbconv3_skeleton_dconv1_bn_FusedBatchNorm_1(
            pass1_block1_mbconv3_skeleton_dconv1_depthwise)
        pass1_block1_mbconv3_skeleton_dconv1_eswish_mul = self.pass1_block1_mbconv3_skeleton_dconv1_eswish_mul_x * \
            pass1_block1_mbconv3_skeleton_dconv1_bn_FusedBatchNorm_1
        pass1_block1_mbconv3_skeleton_dconv1_eswish_Sigmoid = F.sigmoid(
            pass1_block1_mbconv3_skeleton_dconv1_bn_FusedBatchNorm_1)
        pass1_block1_mbconv3_skeleton_dconv1_eswish_mul_1 = pass1_block1_mbconv3_skeleton_dconv1_eswish_mul * \
            pass1_block1_mbconv3_skeleton_dconv1_eswish_Sigmoid
        pass1_block1_mbconv3_skeleton_se_se_squeeze_lambda_Mean = torch.mean(
            pass1_block1_mbconv3_skeleton_dconv1_eswish_mul_1, 3, True)
        pass1_block1_mbconv3_skeleton_se_se_squeeze_lambda_Mean = torch.mean(
            pass1_block1_mbconv3_skeleton_se_se_squeeze_lambda_Mean, 2, True)
        pass1_block1_mbconv3_skeleton_se_se_squeeze_conv_convolution = self.pass1_block1_mbconv3_skeleton_se_se_squeeze_conv_convolution(
            pass1_block1_mbconv3_skeleton_se_se_squeeze_lambda_Mean)
        pass1_block1_mbconv3_skeleton_se_se_squeeze_eswish_mul = self.pass1_block1_mbconv3_skeleton_se_se_squeeze_eswish_mul_x * \
            pass1_block1_mbconv3_skeleton_se_se_squeeze_conv_convolution
        pass1_block1_mbconv3_skeleton_se_se_squeeze_eswish_Sigmoid = F.sigmoid(
            pass1_block1_mbconv3_skeleton_se_se_squeeze_conv_convolution)
        pass1_block1_mbconv3_skeleton_se_se_squeeze_eswish_mul_1 = pass1_block1_mbconv3_skeleton_se_se_squeeze_eswish_mul * \
            pass1_block1_mbconv3_skeleton_se_se_squeeze_eswish_Sigmoid
        pass1_block1_mbconv3_skeleton_se_se_excite_conv_convolution = self.pass1_block1_mbconv3_skeleton_se_se_excite_conv_convolution(
            pass1_block1_mbconv3_skeleton_se_se_squeeze_eswish_mul_1)
        pass1_block1_mbconv3_skeleton_se_se_excite_sigmoid_Sigmoid = F.sigmoid(
            pass1_block1_mbconv3_skeleton_se_se_excite_conv_convolution)
        pass1_block1_mbconv3_skeleton_se_se_multiply_mul = pass1_block1_mbconv3_skeleton_se_se_excite_sigmoid_Sigmoid * \
            pass1_block1_mbconv3_skeleton_dconv1_eswish_mul_1
        pass1_block1_mbconv3_skeleton_conv2_convolution = self.pass1_block1_mbconv3_skeleton_conv2_convolution(
            pass1_block1_mbconv3_skeleton_se_se_multiply_mul)
        pass1_block1_mbconv3_skeleton_conv2_bn_FusedBatchNorm_1 = self.pass1_block1_mbconv3_skeleton_conv2_bn_FusedBatchNorm_1(
            pass1_block1_mbconv3_skeleton_conv2_convolution)
        pass1_block1_mbconv3_skeleton_dense_concat = torch.cat(
            (pass1_block1_mbconv3_skeleton_conv2_bn_FusedBatchNorm_1, pass1_block1_mbconv2_skeleton_dense_concat), 1)
        concatenate_1_concat = torch.cat(
            (pass1_block1_mbconv3_skeleton_dense_concat, block3b_add_res1_add), 1)
        pass2_block1_mbconv1_detection1_conv1_convolution = self.pass2_block1_mbconv1_detection1_conv1_convolution(
            concatenate_1_concat)
        pass2_block1_mbconv1_detection1_conv1_bn_FusedBatchNorm_1 = self.pass2_block1_mbconv1_detection1_conv1_bn_FusedBatchNorm_1(
            pass2_block1_mbconv1_detection1_conv1_convolution)
        pass2_block1_mbconv1_detection1_conv1_eswish_mul = self.pass2_block1_mbconv1_detection1_conv1_eswish_mul_x * \
            pass2_block1_mbconv1_detection1_conv1_bn_FusedBatchNorm_1
        pass2_block1_mbconv1_detection1_conv1_eswish_Sigmoid = F.sigmoid(
            pass2_block1_mbconv1_detection1_conv1_bn_FusedBatchNorm_1)
        pass2_block1_mbconv1_detection1_conv1_eswish_mul_1 = pass2_block1_mbconv1_detection1_conv1_eswish_mul * \
            pass2_block1_mbconv1_detection1_conv1_eswish_Sigmoid
        pass2_block1_mbconv1_detection1_dconv1_depthwise_pad = F.pad(
            pass2_block1_mbconv1_detection1_conv1_eswish_mul_1, (2, 2, 2, 2))
        pass2_block1_mbconv1_detection1_dconv1_depthwise = self.pass2_block1_mbconv1_detection1_dconv1_depthwise(
            pass2_block1_mbconv1_detection1_dconv1_depthwise_pad)
        pass2_block1_mbconv1_detection1_dconv1_bn_FusedBatchNorm_1 = self.pass2_block1_mbconv1_detection1_dconv1_bn_FusedBatchNorm_1(
            pass2_block1_mbconv1_detection1_dconv1_depthwise)
        pass2_block1_mbconv1_detection1_dconv1_eswish_mul = self.pass2_block1_mbconv1_detection1_dconv1_eswish_mul_x * \
            pass2_block1_mbconv1_detection1_dconv1_bn_FusedBatchNorm_1
        pass2_block1_mbconv1_detection1_dconv1_eswish_Sigmoid = F.sigmoid(
            pass2_block1_mbconv1_detection1_dconv1_bn_FusedBatchNorm_1)
        pass2_block1_mbconv1_detection1_dconv1_eswish_mul_1 = pass2_block1_mbconv1_detection1_dconv1_eswish_mul * \
            pass2_block1_mbconv1_detection1_dconv1_eswish_Sigmoid
        pass2_block1_mbconv1_detection1_se_se_squeeze_lambda_Mean = torch.mean(
            pass2_block1_mbconv1_detection1_dconv1_eswish_mul_1, 3, True)
        pass2_block1_mbconv1_detection1_se_se_squeeze_lambda_Mean = torch.mean(
            pass2_block1_mbconv1_detection1_se_se_squeeze_lambda_Mean, 2, True)
        pass2_block1_mbconv1_detection1_se_se_squeeze_conv_convolution = self.pass2_block1_mbconv1_detection1_se_se_squeeze_conv_convolution(
            pass2_block1_mbconv1_detection1_se_se_squeeze_lambda_Mean)
        pass2_block1_mbconv1_detection1_se_se_squeeze_eswish_mul = self.pass2_block1_mbconv1_detection1_se_se_squeeze_eswish_mul_x * \
            pass2_block1_mbconv1_detection1_se_se_squeeze_conv_convolution
        pass2_block1_mbconv1_detection1_se_se_squeeze_eswish_Sigmoid = F.sigmoid(
            pass2_block1_mbconv1_detection1_se_se_squeeze_conv_convolution)
        pass2_block1_mbconv1_detection1_se_se_squeeze_eswish_mul_1 = pass2_block1_mbconv1_detection1_se_se_squeeze_eswish_mul * \
            pass2_block1_mbconv1_detection1_se_se_squeeze_eswish_Sigmoid
        pass2_block1_mbconv1_detection1_se_se_excite_conv_convolution = self.pass2_block1_mbconv1_detection1_se_se_excite_conv_convolution(
            pass2_block1_mbconv1_detection1_se_se_squeeze_eswish_mul_1)
        pass2_block1_mbconv1_detection1_se_se_excite_sigmoid_Sigmoid = F.sigmoid(
            pass2_block1_mbconv1_detection1_se_se_excite_conv_convolution)
        pass2_block1_mbconv1_detection1_se_se_multiply_mul = pass2_block1_mbconv1_detection1_se_se_excite_sigmoid_Sigmoid * \
            pass2_block1_mbconv1_detection1_dconv1_eswish_mul_1
        pass2_block1_mbconv1_detection1_conv2_convolution = self.pass2_block1_mbconv1_detection1_conv2_convolution(
            pass2_block1_mbconv1_detection1_se_se_multiply_mul)
        pass2_block1_mbconv1_detection1_conv2_bn_FusedBatchNorm_1 = self.pass2_block1_mbconv1_detection1_conv2_bn_FusedBatchNorm_1(
            pass2_block1_mbconv1_detection1_conv2_convolution)
        pass2_block1_mbconv2_detection1_conv1_convolution = self.pass2_block1_mbconv2_detection1_conv1_convolution(
            pass2_block1_mbconv1_detection1_conv2_bn_FusedBatchNorm_1)
        pass2_block1_mbconv2_detection1_conv1_bn_FusedBatchNorm_1 = self.pass2_block1_mbconv2_detection1_conv1_bn_FusedBatchNorm_1(
            pass2_block1_mbconv2_detection1_conv1_convolution)
        pass2_block1_mbconv2_detection1_conv1_eswish_mul = self.pass2_block1_mbconv2_detection1_conv1_eswish_mul_x * \
            pass2_block1_mbconv2_detection1_conv1_bn_FusedBatchNorm_1
        pass2_block1_mbconv2_detection1_conv1_eswish_Sigmoid = F.sigmoid(
            pass2_block1_mbconv2_detection1_conv1_bn_FusedBatchNorm_1)
        pass2_block1_mbconv2_detection1_conv1_eswish_mul_1 = pass2_block1_mbconv2_detection1_conv1_eswish_mul * \
            pass2_block1_mbconv2_detection1_conv1_eswish_Sigmoid
        pass2_block1_mbconv2_detection1_dconv1_depthwise_pad = F.pad(
            pass2_block1_mbconv2_detection1_conv1_eswish_mul_1, (2, 2, 2, 2))
        pass2_block1_mbconv2_detection1_dconv1_depthwise = self.pass2_block1_mbconv2_detection1_dconv1_depthwise(
            pass2_block1_mbconv2_detection1_dconv1_depthwise_pad)
        pass2_block1_mbconv2_detection1_dconv1_bn_FusedBatchNorm_1 = self.pass2_block1_mbconv2_detection1_dconv1_bn_FusedBatchNorm_1(
            pass2_block1_mbconv2_detection1_dconv1_depthwise)
        pass2_block1_mbconv2_detection1_dconv1_eswish_mul = self.pass2_block1_mbconv2_detection1_dconv1_eswish_mul_x * \
            pass2_block1_mbconv2_detection1_dconv1_bn_FusedBatchNorm_1
        pass2_block1_mbconv2_detection1_dconv1_eswish_Sigmoid = F.sigmoid(
            pass2_block1_mbconv2_detection1_dconv1_bn_FusedBatchNorm_1)
        pass2_block1_mbconv2_detection1_dconv1_eswish_mul_1 = pass2_block1_mbconv2_detection1_dconv1_eswish_mul * \
            pass2_block1_mbconv2_detection1_dconv1_eswish_Sigmoid
        pass2_block1_mbconv2_detection1_se_se_squeeze_lambda_Mean = torch.mean(
            pass2_block1_mbconv2_detection1_dconv1_eswish_mul_1, 3, True)
        pass2_block1_mbconv2_detection1_se_se_squeeze_lambda_Mean = torch.mean(
            pass2_block1_mbconv2_detection1_se_se_squeeze_lambda_Mean, 2, True)
        pass2_block1_mbconv2_detection1_se_se_squeeze_conv_convolution = self.pass2_block1_mbconv2_detection1_se_se_squeeze_conv_convolution(
            pass2_block1_mbconv2_detection1_se_se_squeeze_lambda_Mean)
        pass2_block1_mbconv2_detection1_se_se_squeeze_eswish_mul = self.pass2_block1_mbconv2_detection1_se_se_squeeze_eswish_mul_x * \
            pass2_block1_mbconv2_detection1_se_se_squeeze_conv_convolution
        pass2_block1_mbconv2_detection1_se_se_squeeze_eswish_Sigmoid = F.sigmoid(
            pass2_block1_mbconv2_detection1_se_se_squeeze_conv_convolution)
        pass2_block1_mbconv2_detection1_se_se_squeeze_eswish_mul_1 = pass2_block1_mbconv2_detection1_se_se_squeeze_eswish_mul * \
            pass2_block1_mbconv2_detection1_se_se_squeeze_eswish_Sigmoid
        pass2_block1_mbconv2_detection1_se_se_excite_conv_convolution = self.pass2_block1_mbconv2_detection1_se_se_excite_conv_convolution(
            pass2_block1_mbconv2_detection1_se_se_squeeze_eswish_mul_1)
        pass2_block1_mbconv2_detection1_se_se_excite_sigmoid_Sigmoid = F.sigmoid(
            pass2_block1_mbconv2_detection1_se_se_excite_conv_convolution)
        pass2_block1_mbconv2_detection1_se_se_multiply_mul = pass2_block1_mbconv2_detection1_se_se_excite_sigmoid_Sigmoid * \
            pass2_block1_mbconv2_detection1_dconv1_eswish_mul_1
        pass2_block1_mbconv2_detection1_conv2_convolution = self.pass2_block1_mbconv2_detection1_conv2_convolution(
            pass2_block1_mbconv2_detection1_se_se_multiply_mul)
        pass2_block1_mbconv2_detection1_conv2_bn_FusedBatchNorm_1 = self.pass2_block1_mbconv2_detection1_conv2_bn_FusedBatchNorm_1(
            pass2_block1_mbconv2_detection1_conv2_convolution)
        pass2_block1_mbconv2_detection1_dense_concat = torch.cat(
            (pass2_block1_mbconv2_detection1_conv2_bn_FusedBatchNorm_1, pass2_block1_mbconv1_detection1_conv2_bn_FusedBatchNorm_1), 1)
        pass2_block1_mbconv3_detection1_conv1_convolution = self.pass2_block1_mbconv3_detection1_conv1_convolution(
            pass2_block1_mbconv2_detection1_dense_concat)
        pass2_block1_mbconv3_detection1_conv1_bn_FusedBatchNorm_1 = self.pass2_block1_mbconv3_detection1_conv1_bn_FusedBatchNorm_1(
            pass2_block1_mbconv3_detection1_conv1_convolution)
        pass2_block1_mbconv3_detection1_conv1_eswish_mul = self.pass2_block1_mbconv3_detection1_conv1_eswish_mul_x * \
            pass2_block1_mbconv3_detection1_conv1_bn_FusedBatchNorm_1
        pass2_block1_mbconv3_detection1_conv1_eswish_Sigmoid = F.sigmoid(
            pass2_block1_mbconv3_detection1_conv1_bn_FusedBatchNorm_1)
        pass2_block1_mbconv3_detection1_conv1_eswish_mul_1 = pass2_block1_mbconv3_detection1_conv1_eswish_mul * \
            pass2_block1_mbconv3_detection1_conv1_eswish_Sigmoid
        pass2_block1_mbconv3_detection1_dconv1_depthwise_pad = F.pad(
            pass2_block1_mbconv3_detection1_conv1_eswish_mul_1, (2, 2, 2, 2))
        pass2_block1_mbconv3_detection1_dconv1_depthwise = self.pass2_block1_mbconv3_detection1_dconv1_depthwise(
            pass2_block1_mbconv3_detection1_dconv1_depthwise_pad)
        pass2_block1_mbconv3_detection1_dconv1_bn_FusedBatchNorm_1 = self.pass2_block1_mbconv3_detection1_dconv1_bn_FusedBatchNorm_1(
            pass2_block1_mbconv3_detection1_dconv1_depthwise)
        pass2_block1_mbconv3_detection1_dconv1_eswish_mul = self.pass2_block1_mbconv3_detection1_dconv1_eswish_mul_x * \
            pass2_block1_mbconv3_detection1_dconv1_bn_FusedBatchNorm_1
        pass2_block1_mbconv3_detection1_dconv1_eswish_Sigmoid = F.sigmoid(
            pass2_block1_mbconv3_detection1_dconv1_bn_FusedBatchNorm_1)
        pass2_block1_mbconv3_detection1_dconv1_eswish_mul_1 = pass2_block1_mbconv3_detection1_dconv1_eswish_mul * \
            pass2_block1_mbconv3_detection1_dconv1_eswish_Sigmoid
        pass2_block1_mbconv3_detection1_se_se_squeeze_lambda_Mean = torch.mean(
            pass2_block1_mbconv3_detection1_dconv1_eswish_mul_1, 3, True)
        pass2_block1_mbconv3_detection1_se_se_squeeze_lambda_Mean = torch.mean(
            pass2_block1_mbconv3_detection1_se_se_squeeze_lambda_Mean, 2, True)
        pass2_block1_mbconv3_detection1_se_se_squeeze_conv_convolution = self.pass2_block1_mbconv3_detection1_se_se_squeeze_conv_convolution(
            pass2_block1_mbconv3_detection1_se_se_squeeze_lambda_Mean)
        pass2_block1_mbconv3_detection1_se_se_squeeze_eswish_mul = self.pass2_block1_mbconv3_detection1_se_se_squeeze_eswish_mul_x * \
            pass2_block1_mbconv3_detection1_se_se_squeeze_conv_convolution
        pass2_block1_mbconv3_detection1_se_se_squeeze_eswish_Sigmoid = F.sigmoid(
            pass2_block1_mbconv3_detection1_se_se_squeeze_conv_convolution)
        pass2_block1_mbconv3_detection1_se_se_squeeze_eswish_mul_1 = pass2_block1_mbconv3_detection1_se_se_squeeze_eswish_mul * \
            pass2_block1_mbconv3_detection1_se_se_squeeze_eswish_Sigmoid
        pass2_block1_mbconv3_detection1_se_se_excite_conv_convolution = self.pass2_block1_mbconv3_detection1_se_se_excite_conv_convolution(
            pass2_block1_mbconv3_detection1_se_se_squeeze_eswish_mul_1)
        pass2_block1_mbconv3_detection1_se_se_excite_sigmoid_Sigmoid = F.sigmoid(
            pass2_block1_mbconv3_detection1_se_se_excite_conv_convolution)
        pass2_block1_mbconv3_detection1_se_se_multiply_mul = pass2_block1_mbconv3_detection1_se_se_excite_sigmoid_Sigmoid * \
            pass2_block1_mbconv3_detection1_dconv1_eswish_mul_1
        pass2_block1_mbconv3_detection1_conv2_convolution = self.pass2_block1_mbconv3_detection1_conv2_convolution(
            pass2_block1_mbconv3_detection1_se_se_multiply_mul)
        pass2_block1_mbconv3_detection1_conv2_bn_FusedBatchNorm_1 = self.pass2_block1_mbconv3_detection1_conv2_bn_FusedBatchNorm_1(
            pass2_block1_mbconv3_detection1_conv2_convolution)
        pass2_block1_mbconv3_detection1_dense_concat = torch.cat(
            (pass2_block1_mbconv3_detection1_conv2_bn_FusedBatchNorm_1, pass2_block1_mbconv2_detection1_dense_concat), 1)
        concatenate_2_concat = torch.cat(
            (pass2_block1_mbconv3_detection1_dense_concat, block3b_add_res1_add), 1)
        pass3_block1_mbconv1_detection2_conv1_convolution = self.pass3_block1_mbconv1_detection2_conv1_convolution(
            concatenate_2_concat)
        pass3_block1_mbconv1_detection2_conv1_bn_FusedBatchNorm_1 = self.pass3_block1_mbconv1_detection2_conv1_bn_FusedBatchNorm_1(
            pass3_block1_mbconv1_detection2_conv1_convolution)
        pass3_block1_mbconv1_detection2_conv1_eswish_mul = self.pass3_block1_mbconv1_detection2_conv1_eswish_mul_x * \
            pass3_block1_mbconv1_detection2_conv1_bn_FusedBatchNorm_1
        pass3_block1_mbconv1_detection2_conv1_eswish_Sigmoid = F.sigmoid(
            pass3_block1_mbconv1_detection2_conv1_bn_FusedBatchNorm_1)
        pass3_block1_mbconv1_detection2_conv1_eswish_mul_1 = pass3_block1_mbconv1_detection2_conv1_eswish_mul * \
            pass3_block1_mbconv1_detection2_conv1_eswish_Sigmoid
        pass3_block1_mbconv1_detection2_dconv1_depthwise_pad = F.pad(
            pass3_block1_mbconv1_detection2_conv1_eswish_mul_1, (2, 2, 2, 2))
        pass3_block1_mbconv1_detection2_dconv1_depthwise = self.pass3_block1_mbconv1_detection2_dconv1_depthwise(
            pass3_block1_mbconv1_detection2_dconv1_depthwise_pad)
        pass3_block1_mbconv1_detection2_dconv1_bn_FusedBatchNorm_1 = self.pass3_block1_mbconv1_detection2_dconv1_bn_FusedBatchNorm_1(
            pass3_block1_mbconv1_detection2_dconv1_depthwise)
        pass3_block1_mbconv1_detection2_dconv1_eswish_mul = self.pass3_block1_mbconv1_detection2_dconv1_eswish_mul_x * \
            pass3_block1_mbconv1_detection2_dconv1_bn_FusedBatchNorm_1
        pass3_block1_mbconv1_detection2_dconv1_eswish_Sigmoid = F.sigmoid(
            pass3_block1_mbconv1_detection2_dconv1_bn_FusedBatchNorm_1)
        pass3_block1_mbconv1_detection2_dconv1_eswish_mul_1 = pass3_block1_mbconv1_detection2_dconv1_eswish_mul * \
            pass3_block1_mbconv1_detection2_dconv1_eswish_Sigmoid
        pass3_block1_mbconv1_detection2_se_se_squeeze_lambda_Mean = torch.mean(
            pass3_block1_mbconv1_detection2_dconv1_eswish_mul_1, 3, True)
        pass3_block1_mbconv1_detection2_se_se_squeeze_lambda_Mean = torch.mean(
            pass3_block1_mbconv1_detection2_se_se_squeeze_lambda_Mean, 2, True)
        pass3_block1_mbconv1_detection2_se_se_squeeze_conv_convolution = self.pass3_block1_mbconv1_detection2_se_se_squeeze_conv_convolution(
            pass3_block1_mbconv1_detection2_se_se_squeeze_lambda_Mean)
        pass3_block1_mbconv1_detection2_se_se_squeeze_eswish_mul = self.pass3_block1_mbconv1_detection2_se_se_squeeze_eswish_mul_x * \
            pass3_block1_mbconv1_detection2_se_se_squeeze_conv_convolution
        pass3_block1_mbconv1_detection2_se_se_squeeze_eswish_Sigmoid = F.sigmoid(
            pass3_block1_mbconv1_detection2_se_se_squeeze_conv_convolution)
        pass3_block1_mbconv1_detection2_se_se_squeeze_eswish_mul_1 = pass3_block1_mbconv1_detection2_se_se_squeeze_eswish_mul * \
            pass3_block1_mbconv1_detection2_se_se_squeeze_eswish_Sigmoid
        pass3_block1_mbconv1_detection2_se_se_excite_conv_convolution = self.pass3_block1_mbconv1_detection2_se_se_excite_conv_convolution(
            pass3_block1_mbconv1_detection2_se_se_squeeze_eswish_mul_1)
        pass3_block1_mbconv1_detection2_se_se_excite_sigmoid_Sigmoid = F.sigmoid(
            pass3_block1_mbconv1_detection2_se_se_excite_conv_convolution)
        pass3_block1_mbconv1_detection2_se_se_multiply_mul = pass3_block1_mbconv1_detection2_se_se_excite_sigmoid_Sigmoid * \
            pass3_block1_mbconv1_detection2_dconv1_eswish_mul_1
        pass3_block1_mbconv1_detection2_conv2_convolution = self.pass3_block1_mbconv1_detection2_conv2_convolution(
            pass3_block1_mbconv1_detection2_se_se_multiply_mul)
        pass3_block1_mbconv1_detection2_conv2_bn_FusedBatchNorm_1 = self.pass3_block1_mbconv1_detection2_conv2_bn_FusedBatchNorm_1(
            pass3_block1_mbconv1_detection2_conv2_convolution)
        pass3_block1_mbconv2_detection2_conv1_convolution = self.pass3_block1_mbconv2_detection2_conv1_convolution(
            pass3_block1_mbconv1_detection2_conv2_bn_FusedBatchNorm_1)
        pass3_block1_mbconv2_detection2_conv1_bn_FusedBatchNorm_1 = self.pass3_block1_mbconv2_detection2_conv1_bn_FusedBatchNorm_1(
            pass3_block1_mbconv2_detection2_conv1_convolution)
        pass3_block1_mbconv2_detection2_conv1_eswish_mul = self.pass3_block1_mbconv2_detection2_conv1_eswish_mul_x * \
            pass3_block1_mbconv2_detection2_conv1_bn_FusedBatchNorm_1
        pass3_block1_mbconv2_detection2_conv1_eswish_Sigmoid = F.sigmoid(
            pass3_block1_mbconv2_detection2_conv1_bn_FusedBatchNorm_1)
        pass3_block1_mbconv2_detection2_conv1_eswish_mul_1 = pass3_block1_mbconv2_detection2_conv1_eswish_mul * \
            pass3_block1_mbconv2_detection2_conv1_eswish_Sigmoid
        pass3_block1_mbconv2_detection2_dconv1_depthwise_pad = F.pad(
            pass3_block1_mbconv2_detection2_conv1_eswish_mul_1, (2, 2, 2, 2))
        pass3_block1_mbconv2_detection2_dconv1_depthwise = self.pass3_block1_mbconv2_detection2_dconv1_depthwise(
            pass3_block1_mbconv2_detection2_dconv1_depthwise_pad)
        pass3_block1_mbconv2_detection2_dconv1_bn_FusedBatchNorm_1 = self.pass3_block1_mbconv2_detection2_dconv1_bn_FusedBatchNorm_1(
            pass3_block1_mbconv2_detection2_dconv1_depthwise)
        pass3_block1_mbconv2_detection2_dconv1_eswish_mul = self.pass3_block1_mbconv2_detection2_dconv1_eswish_mul_x * \
            pass3_block1_mbconv2_detection2_dconv1_bn_FusedBatchNorm_1
        pass3_block1_mbconv2_detection2_dconv1_eswish_Sigmoid = F.sigmoid(
            pass3_block1_mbconv2_detection2_dconv1_bn_FusedBatchNorm_1)
        pass3_block1_mbconv2_detection2_dconv1_eswish_mul_1 = pass3_block1_mbconv2_detection2_dconv1_eswish_mul * \
            pass3_block1_mbconv2_detection2_dconv1_eswish_Sigmoid
        pass3_block1_mbconv2_detection2_se_se_squeeze_lambda_Mean = torch.mean(
            pass3_block1_mbconv2_detection2_dconv1_eswish_mul_1, 3, True)
        pass3_block1_mbconv2_detection2_se_se_squeeze_lambda_Mean = torch.mean(
            pass3_block1_mbconv2_detection2_se_se_squeeze_lambda_Mean, 2, True)
        pass3_block1_mbconv2_detection2_se_se_squeeze_conv_convolution = self.pass3_block1_mbconv2_detection2_se_se_squeeze_conv_convolution(
            pass3_block1_mbconv2_detection2_se_se_squeeze_lambda_Mean)
        pass3_block1_mbconv2_detection2_se_se_squeeze_eswish_mul = self.pass3_block1_mbconv2_detection2_se_se_squeeze_eswish_mul_x * \
            pass3_block1_mbconv2_detection2_se_se_squeeze_conv_convolution
        pass3_block1_mbconv2_detection2_se_se_squeeze_eswish_Sigmoid = F.sigmoid(
            pass3_block1_mbconv2_detection2_se_se_squeeze_conv_convolution)
        pass3_block1_mbconv2_detection2_se_se_squeeze_eswish_mul_1 = pass3_block1_mbconv2_detection2_se_se_squeeze_eswish_mul * \
            pass3_block1_mbconv2_detection2_se_se_squeeze_eswish_Sigmoid
        pass3_block1_mbconv2_detection2_se_se_excite_conv_convolution = self.pass3_block1_mbconv2_detection2_se_se_excite_conv_convolution(
            pass3_block1_mbconv2_detection2_se_se_squeeze_eswish_mul_1)
        pass3_block1_mbconv2_detection2_se_se_excite_sigmoid_Sigmoid = F.sigmoid(
            pass3_block1_mbconv2_detection2_se_se_excite_conv_convolution)
        pass3_block1_mbconv2_detection2_se_se_multiply_mul = pass3_block1_mbconv2_detection2_se_se_excite_sigmoid_Sigmoid * \
            pass3_block1_mbconv2_detection2_dconv1_eswish_mul_1
        pass3_block1_mbconv2_detection2_conv2_convolution = self.pass3_block1_mbconv2_detection2_conv2_convolution(
            pass3_block1_mbconv2_detection2_se_se_multiply_mul)
        pass3_block1_mbconv2_detection2_conv2_bn_FusedBatchNorm_1 = self.pass3_block1_mbconv2_detection2_conv2_bn_FusedBatchNorm_1(
            pass3_block1_mbconv2_detection2_conv2_convolution)
        pass3_block1_mbconv2_detection2_dense_concat = torch.cat(
            (pass3_block1_mbconv2_detection2_conv2_bn_FusedBatchNorm_1, pass3_block1_mbconv1_detection2_conv2_bn_FusedBatchNorm_1), 1)
        pass3_block1_mbconv3_detection2_conv1_convolution = self.pass3_block1_mbconv3_detection2_conv1_convolution(
            pass3_block1_mbconv2_detection2_dense_concat)
        pass3_block1_mbconv3_detection2_conv1_bn_FusedBatchNorm_1 = self.pass3_block1_mbconv3_detection2_conv1_bn_FusedBatchNorm_1(
            pass3_block1_mbconv3_detection2_conv1_convolution)
        pass3_block1_mbconv3_detection2_conv1_eswish_mul = self.pass3_block1_mbconv3_detection2_conv1_eswish_mul_x * \
            pass3_block1_mbconv3_detection2_conv1_bn_FusedBatchNorm_1
        pass3_block1_mbconv3_detection2_conv1_eswish_Sigmoid = F.sigmoid(
            pass3_block1_mbconv3_detection2_conv1_bn_FusedBatchNorm_1)
        pass3_block1_mbconv3_detection2_conv1_eswish_mul_1 = pass3_block1_mbconv3_detection2_conv1_eswish_mul * \
            pass3_block1_mbconv3_detection2_conv1_eswish_Sigmoid
        pass3_block1_mbconv3_detection2_dconv1_depthwise_pad = F.pad(
            pass3_block1_mbconv3_detection2_conv1_eswish_mul_1, (2, 2, 2, 2))
        pass3_block1_mbconv3_detection2_dconv1_depthwise = self.pass3_block1_mbconv3_detection2_dconv1_depthwise(
            pass3_block1_mbconv3_detection2_dconv1_depthwise_pad)
        pass3_block1_mbconv3_detection2_dconv1_bn_FusedBatchNorm_1 = self.pass3_block1_mbconv3_detection2_dconv1_bn_FusedBatchNorm_1(
            pass3_block1_mbconv3_detection2_dconv1_depthwise)
        pass3_block1_mbconv3_detection2_dconv1_eswish_mul = self.pass3_block1_mbconv3_detection2_dconv1_eswish_mul_x * \
            pass3_block1_mbconv3_detection2_dconv1_bn_FusedBatchNorm_1
        pass3_block1_mbconv3_detection2_dconv1_eswish_Sigmoid = F.sigmoid(
            pass3_block1_mbconv3_detection2_dconv1_bn_FusedBatchNorm_1)
        pass3_block1_mbconv3_detection2_dconv1_eswish_mul_1 = pass3_block1_mbconv3_detection2_dconv1_eswish_mul * \
            pass3_block1_mbconv3_detection2_dconv1_eswish_Sigmoid
        pass3_block1_mbconv3_detection2_se_se_squeeze_lambda_Mean = torch.mean(
            pass3_block1_mbconv3_detection2_dconv1_eswish_mul_1, 3, True)
        pass3_block1_mbconv3_detection2_se_se_squeeze_lambda_Mean = torch.mean(
            pass3_block1_mbconv3_detection2_se_se_squeeze_lambda_Mean, 2, True)
        pass3_block1_mbconv3_detection2_se_se_squeeze_conv_convolution = self.pass3_block1_mbconv3_detection2_se_se_squeeze_conv_convolution(
            pass3_block1_mbconv3_detection2_se_se_squeeze_lambda_Mean)
        pass3_block1_mbconv3_detection2_se_se_squeeze_eswish_mul = self.pass3_block1_mbconv3_detection2_se_se_squeeze_eswish_mul_x * \
            pass3_block1_mbconv3_detection2_se_se_squeeze_conv_convolution
        pass3_block1_mbconv3_detection2_se_se_squeeze_eswish_Sigmoid = F.sigmoid(
            pass3_block1_mbconv3_detection2_se_se_squeeze_conv_convolution)
        pass3_block1_mbconv3_detection2_se_se_squeeze_eswish_mul_1 = pass3_block1_mbconv3_detection2_se_se_squeeze_eswish_mul * \
            pass3_block1_mbconv3_detection2_se_se_squeeze_eswish_Sigmoid
        pass3_block1_mbconv3_detection2_se_se_excite_conv_convolution = self.pass3_block1_mbconv3_detection2_se_se_excite_conv_convolution(
            pass3_block1_mbconv3_detection2_se_se_squeeze_eswish_mul_1)
        pass3_block1_mbconv3_detection2_se_se_excite_sigmoid_Sigmoid = F.sigmoid(
            pass3_block1_mbconv3_detection2_se_se_excite_conv_convolution)
        pass3_block1_mbconv3_detection2_se_se_multiply_mul = pass3_block1_mbconv3_detection2_se_se_excite_sigmoid_Sigmoid * \
            pass3_block1_mbconv3_detection2_dconv1_eswish_mul_1
        pass3_block1_mbconv3_detection2_conv2_convolution = self.pass3_block1_mbconv3_detection2_conv2_convolution(
            pass3_block1_mbconv3_detection2_se_se_multiply_mul)
        pass3_block1_mbconv3_detection2_conv2_bn_FusedBatchNorm_1 = self.pass3_block1_mbconv3_detection2_conv2_bn_FusedBatchNorm_1(
            pass3_block1_mbconv3_detection2_conv2_convolution)
        pass3_block1_mbconv3_detection2_dense_concat = torch.cat(
            (pass3_block1_mbconv3_detection2_conv2_bn_FusedBatchNorm_1, pass3_block1_mbconv2_detection2_dense_concat), 1)
        pass3_detection2_confs_convolution = self.pass3_detection2_confs_convolution(
            pass3_block1_mbconv3_detection2_dense_concat)
        transposed_convolution_1 = self.__transposed(
            channels=16, kernel_size=4, stride=2)(pass3_detection2_confs_convolution)
        transposed_convolution_2 = self.__transposed(
            channels=16, kernel_size=4, stride=2)(transposed_convolution_1)
        transposed_convolution_3 = self.__transposed(
            channels=16, kernel_size=4, stride=2)(transposed_convolution_2)

        return transposed_convolution_3

    @staticmethod
    def __conv(dim, name, **kwargs):
        if dim == 1:
            layer = nn.Conv1d(**kwargs)
        elif dim == 2:
            layer = nn.Conv2d(**kwargs)
        elif dim == 3:
            layer = nn.Conv3d(**kwargs)
        else:
            raise NotImplementedError()

        layer.state_dict()['weight'].copy_(torch.from_numpy(__weights_dict[name]['weights']))
        if 'bias' in __weights_dict[name]:
            layer.state_dict()['bias'].copy_(torch.from_numpy(__weights_dict[name]['bias']))
        return layer

    @staticmethod
    def __batch_normalization(dim, name, **kwargs):
        if dim == 0 or dim == 1:
            layer = nn.BatchNorm1d(**kwargs)
        elif dim == 2:
            layer = nn.BatchNorm2d(**kwargs)
        elif dim == 3:
            layer = nn.BatchNorm3d(**kwargs)
        else:
            raise NotImplementedError()

        if 'scale' in __weights_dict[name]:
            layer.state_dict()['weight'].copy_(torch.from_numpy(__weights_dict[name]['scale']))
        else:
            layer.weight.data.fill_(1)

        if 'bias' in __weights_dict[name]:
            layer.state_dict()['bias'].copy_(torch.from_numpy(__weights_dict[name]['bias']))
        else:
            layer.bias.data.fill_(0)

        layer.state_dict()['running_mean'].copy_(torch.from_numpy(__weights_dict[name]['mean']))
        layer.state_dict()['running_var'].copy_(torch.from_numpy(__weights_dict[name]['var']))
        return layer

    @staticmethod
    def __transposed(channels, kernel_size, stride):
        return helpers.pytorch_BilinearConvTranspose2d(channels=channels, kernel_size=kernel_size, stride=stride)


if __name__ == '__main__':
    import sys
    sys.path.insert(0, 'C:/Users/TuanShu/repos/efficientpose')
    from utils import helpers
    from torch import load, quantization, backends
    from os.path import join, normpath
    from imp import load_source

    # Initialize the model - load way
    MainModel = load_source('MainModel', join('models', 'pytorch',
                            'EfficientPoseRT.py'))
    model = load(join('models', 'pytorch', 'EfficientPoseRT'))
    summary(model, (3, 256, 384))  # final output [-1, 16, 32, 48]

    # Initialize the model - pl way
    # # weight_file = './models/pytorch/EfficientPoseRT'
    # # weights_dict = np.load(weight_file, allow_pickle=True, encoding='bytes')  # .item()
    # # print(weights_dict)
    # model = KitModel(weight_file=None)  # 不確定為何這樣不行

    # summary = ModelSummary(model)
    # print(summary)


else:
    from utils import helpers
