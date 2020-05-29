import numpy as np
from enum import Enum

# Torch
import torch
from torch.autograd import Variable
import torch.nn.functional as F

# local files
import net_s3fd
import bbox


class Mode(Enum):
    GPU = 0
    CPU = 1


class S3FDDetector:
    """S3FD pyTorch face detector class."""
    def __init__(self, model_path, mode, gpu_id=-1):
        # load model from file
        self.net = net_s3fd.s3fd()
        self.net.load_state_dict(torch.load(model_path))

        # set mode and device
        self.gpu_id = gpu_id
        self.is_cuda = mode == Mode.GPU and torch.cuda.is_available()
        if self.is_cuda:
            with torch.cuda.device(self.gpu_id):
                self.net.cuda()

        # set evaluation mode
        self.net.eval()

    def detect(self, imgs, treshold=0.05):
        """Detect faces on images."""
        # prepare batch
        prepared_imgs = []
        for img in imgs:
            # subtract mean
            img = img - np.array([104, 117, 123])
            img = img.transpose(2, 0, 1)
            prepared_imgs.append(img)
        np_batch = np.stack(prepared_imgs)

        if self.is_cuda:
            with torch.cuda.device(self.gpu_id):
                batch = Variable(torch.from_numpy(np_batch).float(), volatile=True).cuda()
                olist = self.net(batch)
        else:
            batch = Variable(torch.from_numpy(np_batch).float(), volatile=True)
            olist = self.net(batch)

        for i in range(len(olist) // 2):
            olist[i * 2] = F.softmax(olist[i * 2], dim=1)

        batch_bboxlists = [list() for _ in range(len(imgs))]
        for i in range(len(olist) // 2):
            ocls, oreg = olist[i * 2].data.cpu(), olist[i * 2 + 1].data.cpu()
            FB, FC, FH, FW = ocls.size()  # feature map size
            stride = 2 ** (i + 2)  # 4,8,16,32,64,128
            for Findex in range(FH * FW):
                windex, hindex = Findex % FW, Findex // FW
                axc, ayc = stride // 2 + windex * stride, stride // 2 + hindex * stride
                for img_idx in range(0, len(imgs)):
                    score = ocls[img_idx, 1, hindex, windex]
                    loc = oreg[img_idx, :, hindex, windex].contiguous().view(1, 4)
                    if score < treshold:
                        continue
                    priors = torch.Tensor([[axc / 1.0, ayc / 1.0, stride * 4 / 1.0, stride * 4 / 1.0]])
                    variances = [0.1, 0.2]
                    box = bbox.decode(loc, priors, variances)
                    x1, y1, x2, y2 = box[0] * 1.0
                    batch_bboxlists[img_idx].append([x1, y1, x2, y2, score])

        batch_detections = []
        for img_idx in range(0, len(imgs)):
            bboxlist = np.array(batch_bboxlists[img_idx])
            if len(bboxlist) == 0:
                bboxlist = np.zeros((1, 5))

            # Non maximum suppression
            keep = bbox.nms(bboxlist, 0.3)
            bboxlist = bboxlist[keep, :]

            # final filtering by confidence, returns list of [x, y, width, height, s]
            batch_detections.append([[x1, y1, x2 - x1 + 1, y2 - y1 + 1, s] for x1, y1, x2, y2, s in bboxlist if s >= 0.5])

        return batch_detections
