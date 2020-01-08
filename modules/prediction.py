import matplotlib.pyplot as plt
import numpy as np
from numpy import r_
from dct_formula_2D import ImgDctUsingDetail
import zlib
import sys
from ZigZag import ZigzagMatrix

def SAE(a, b):
    '''
    calculate Sum of Absolute Errors of two images, divided by number of pixels
    :param a: image A, matrix
    :param b: image B, matrix
    '''
    result = np.sum(np.abs(np.subtract(a,b,dtype=np.float))) / (a.size)
    return result

# 16x16 block's Mode 0 (vertical) prediction mode
def mode0_16x16(block, H):
    size = block.shape
    temp = np.zeros(size)
    for i in range(0, size[0]):
        temp[i,:] = H

    #print(temp)
    diff = SAE(block, temp)
    return temp, diff

# 16x16 block's Mode 1 (horizontal) prediction mode
def mode1_16x16(block, V):
    size = block.shape
    temp = np.zeros(size)
    for i in range(0, size[1]):
        temp[:,i] = V

    #print(temp)
    diff = SAE(block, temp)
    return temp, diff

# 16x16 block's Mode 2 (mean) prediction mode
def mode2_16x16(block, H, V):
    size = block.shape

    mean = (np.sum(H) + np.sum(V)) / (H.size+V.size)

    temp = np.zeros(size)
    temp[:] = mean

    #print(temp)
    diff = SAE(block, temp)
    return temp, diff

# 16x16 block's Mode 3 (plan) prediction mode
# TODO: this function should be verified by x264 related code
def mode3_16x16(block, H, V, P):
    size = block.shape

    h = 0
    v = 0

    for x in range(0,8):
        if (x==7):
            h = h + (x+1)*(V[8+x]-P)   # use P point value to replace p[-1, -1]
        else:
            h = h + (x+1)*(V[8+x]-V[6-x])

    for y in range(0,8):
        if (y==7):
            v = v + (y+1)*(H[8+y]-P)   # use P point value to replace p[-1, -1]
        else:
            v = v + (y+1)*(H[8+y]-H[6-y])

    a = 16*( H[15] + V[15] )
    b = ( 5*h + 32 ) / 64
    c = ( 5*v + 32 ) / 64

    temp = np.zeros(size)

    for i in range(0,8):
        for j in range(0,8):
            temp[i,j] = (a + b*(i-7) + c*(j-7) + 16) / 32

    #print(temp)
    diff = SAE(block, temp)
    return temp, diff

def pickTheBestMode(block, H, V, P):
    temp0, diff0 = mode0_16x16(block, H)
    temp1, diff1 = mode1_16x16(block, V)
    temp2, diff2 = mode2_16x16(block, H, V)
    temp3, diff3 = mode3_16x16(block, H, V, P)

    list1, list2 = [temp0, temp1, temp2, temp3], [diff0, diff1, diff2, diff3]
    mode = list2.index(min(list2))

    return list1[mode], mode

def predictImage():
    im = plt.imread("E:/liumangxuxu/code/PyCodec/modules/lena2.tif").astype(float)
    print(im.shape)
    
    step = 16 # 16x16 as block
    imsize = im.shape

    predict = np.zeros(imsize)    # intra prediction result, motion compensation
    mode_map = np.zeros(imsize)    # save block mode information

    for i in r_[:imsize[0]:step]:
        for j in r_[:imsize[1]:step]:
            H = np.zeros((step, 1))
            V = np.zeros((1, step))
            P = 0   # the value of left top conner of pixel

            if (i==0) and (j==0):  # for left-top block, just copy the data
                H = im[i,j:(j+step)]
                V = im[i:(i+step),j]
                P = im[0, 0]

            elif i==0 and j!=0:
                H = im[i,j:(j+step)]
                V = im[i:(i+step),j-1]
                P = im[i, j-1]
                
            elif j==0 and i!=0:
                H = im[i-1,j:(j+step)]
                V = im[i:(i+step),j]
                P = im[i-1, j]

            else:
                H = im[i-1,j:(j+step)]
                V = im[i:(i+step),j-1]
                P = im[i-1, j-1]

            predict[i:(i+step),j:(j+step)], mode = pickTheBestMode(im[i:(i+step),j:(j+step)], H, V, P)
            mode_map[i:(i+step),j:(j+step)].fill(mode)

    diff = SAE(im, predict)
    print(diff)

    residual = im - predict

    plt.figure()
    plt.imshow(im, cmap='gray')
    plt.title("Original of the image")

    plt.figure()
    plt.imshow(predict, cmap='gray')
    plt.title("Prediction Using H.264 16x16 intra prediction")

    plt.figure()
    plt.imshow(mode_map, cmap='gray')
    # add mode number on the picture
    # for i in r_[:imsize[0]:step]:
    #     for j in r_[:imsize[1]:step]:
    #         plt.text(i+4, j+4, mode_map[i,j])
    plt.title("mode map of 16x16 block intra prediction")

    plt.figure()
    plt.imshow(residual, cmap='gray')
    plt.title("residual after subtracting intra prediction")

    #compare the DCT result of origianl image and residual image
    dct, img_dct = ImgDctUsingDetail(im)
    dct_residual, idct_residual = ImgDctUsingDetail(residual)

    decom_dct = zlib.compress(np.trunc(dct))
    print(sys.getsizeof(decom_dct))

    #test code for ZigZag
    zig = ZigzagMatrix()
    # test = np.array([[1, 2, 3, 4, 5, 6],
    #                  [7, 8, 9, 10, 11, 12],
    #                  [13, 14, 15, 16, 17, 18]])
    # print(zig.ConvertZMatrix(test))

    # decom_dct = zlib.compress(dct_residual)
    # print(sys.getsizeof(decom_dct))
    dct_res_1D = zig.zig2Matrix(np.trunc(dct_residual))
    decom_bytes = zlib.compress(dct_res_1D)
    print(sys.getsizeof(decom_bytes))

    plt.figure()
    plt.imshow(dct, cmap='gray')
    plt.title("DCT coefficients of original image")

    plt.figure()
    plt.imshow(dct_residual, cmap='gray')
    plt.title("DCT coefficients of residual image")

    plt.show()

if __name__ == "__main__":
    np.set_printoptions(suppress=True)

    predictImage()