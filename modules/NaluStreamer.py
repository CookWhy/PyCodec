# Based on the document of ITU-T Recommendation H.264 05/2003 edition
# 

from bitstring import BitStream, BitArray
from h26x_extractor import nalutypes

START_CODE_PREFIX = '0x00000001'
START_CODE_PREFIX_SHORT = "0x000001"

def openNaluFile(bitstream_outputfile):
    '''
    Init Nalu File, which means clean all the old data in the file
    '''
    return open(bitstream_outputfile, 'wb')

def closeNaluFile(bitstream_outputfile_handler):
    bitstream_outputfile_handler.close()

class NaluStreamer():

    def __init__(self, nalu_type):
        '''
        init the value of nalu unit
        : param nalu_type: something like NAL_UNIT_TYPE_CODED_SLICE_IDR in nalutypes.py
        '''
        self.forbidden_zero_bit = '0b0'
        self.nal_ref_idc = '0b11'
        self.nal_unit_type = "0b" + "{0:05b}".format(nalu_type)

        self.stream = BitStream(START_CODE_PREFIX)
        self.stream.append(self.forbidden_zero_bit)
        self.stream.append(self.nal_ref_idc)
        self.stream.append(self.nal_unit_type)

    def rbsp_trailing_bits(self):
        '''
        according to RBSP trainling bits syntax on page 35, and according to explanation page 49
        '''
        rbsp_stop_one_bit = '0b1'
        rbsp_alignment_zero_bit = '0b0'
        self.stream.append(rbsp_stop_one_bit)

        plus = 8 - (self.stream.length % 8)

        for x in range(0, plus):
            self.stream.append(rbsp_alignment_zero_bit)

        #print("length after plus:")
        #print(self.stream.length)

    def export(self, bitstream_output_handler):
        """
        output the binary data into file
        """
        self.stream.tofile(bitstream_output_handler)

class SpsStreamer(NaluStreamer):
    """
    Sequence Parameter Set class
    Based on 7.3.2.1 setion on page 31 & 7.4.2.1 setion on page 53
    The sequence of set__ function is not important.
    the function export() will take care of the sequence of the SODB.
    """

    def __init__(self, nalu_type):
        super().__init__(nalu_type)

        # use some default value
        self.profile_idc = '0x64'   # u(8)
        self.constraint_set0_flag = '0b0' # u(1)
        self.constraint_set1_flag = '0b0' # u(1)
        self.constraint_set2_flag = '0b0' # u(1)

        self.reserved_zero_2bits = '0b00000' # u(5)
        self.level_idc = '0b00001' # u(5)
        self.seq_parameter_set_id = '0b0' #ue(v)

        # if ((self.profile_idc == 100) or (self.profile_idc == 110) or (self.profile_idc == 122) or (self.profile_idc == 144)):
        #     self.chroma_format_idc = self.s.read('ue')
        #     if self.chroma_format_idc == 3:
        #         self.residual_colour_transform_flag = self.s.read('uint:1')

        #     self.bit_depth_luma_minus8 = self.s.read('ue')
        #     self.bit_depth_chroma_minus8 = self.s.read('ue')
        #     self.qpprime_y_zero_transform_bypass_flag = self.s.read('uint:1')
        #     self.seq_scaling_matrix_present_flag = self.s.read('uint:1')

        #     if self.seq_scaling_matrix_present_flag:
        #         # TODO: have to implement this, otherwise it will fail
        #         raise NotImplementedError("Scaling matrix decoding is not implemented.")

        self.log2_max_frame_num_minus4 = '0b1' #ue(v)
        self.pic_order_cnt_type = '0b1' #ue(v)

        self.num_ref_frames = '0b1' #ue(v)
        self.gaps_in_frame_num_value_allowed_flag = '0b0' #u(1)
        self.pic_width_in_mbs_minus_1 = '0b0' #u(ue)
        self.pic_height_in_map_units_minus_1 = '0b0' #u(ue)
        self.frame_mbs_only_flag = '0b1' #u(1)
        # if not self.frame_mbs_only_flag:
        #     self.mb_adapative_frame_field_flag = self.s.read('uint:1')
        self.direct_8x8_inference_flag = '0b0' #u(1)
        self.frame_cropping_flag = '0b0' #u(1)
        # if self.frame_cropping_flag:
        #     self.frame_crop_left_offst = self.s.read('ue')
        #     self.frame_crop_right_offset = self.s.read('ue')
        #     self.frame_crop_top_offset = self.s.read('ue')
        #     self.frame_crop_bottom_offset = self.s.read('ue')
        self.vui_parameters_present_flag = '0b0' #u(1)

    def set__profile_idc(self, profile_idc):
        '''
        set level_idc in SPS, foramt: u(8)
        : param set_id: int number of set id, according to Table A-1 Level limits on page 207
        '''
        self.profile_idc = "0b" + "{0:08b}".format(profile_idc)

    def set__level_idc(self, level_number):
        '''
        set level_idc in SPS, foramt: u(8)
        : param set_id: int number of set id, according to Table A-1 Level limits on page 207
        '''
        self.level_idc = "0b" + "{0:08b}".format(level_number*10)

    def set__seq_parameter_set_id(self, set_id):
        '''
        set seq_parameter_set_id in SPS, foramt: ue(v)
        : param set_id: int number of set id
        '''
        s = BitArray(ue=set_id)
        self.seq_parameter_set_id = s

    def set__log2_max_frame_num_minus4(self, value):
        '''
        set log2_max_frame_num_minus4 in SPS, foramt: ue(v)
        : param value: described on page 54
        '''
        s = BitArray(ue=value)
        self.log2_max_frame_num_minus4 = s

    def set__pic_order_cnt_type(self, value):
        '''
        set pic_order_cnt_type in SPS, foramt: ue(v)
        : param value: described on page 54
        '''
        s = BitArray(ue=value)
        self.pic_order_cnt_type = s

        if (value == 0):
            # log2_max_pic_order_cnt_lsb_minus4
            log2_max_pic_order_cnt_lsb_minus4 = 0   # todo, need to add specific data
            temp = BitArray(ue=log2_max_pic_order_cnt_lsb_minus4)
            self.pic_order_cnt_type.append(temp)
        elif (value == 1):
            print("TODO: ADD MORE SPECIFIC ITEM")
        #     self.delta_pic_order_always_zero_flag = '0b1' # u(1)
        #     self.offset_for_non_ref_pic = self.s.read('se')
        #     self.offset_for_top_to_bottom_filed = self.s.read('se')
        #     self.num_ref_frames_in_pic_order_cnt_cycle = self.s.read('ue')
        #     for i in range(self.num_ref_frames_in_pic_order_cnt_cycle):
        #         self.offset_for_ref_frame.append(self.s.read('se'))

    def set__num_ref_frames(self, value):
        '''
        set num_ref_frames in SPS, foramt: ue(v)
        : param value: described on page 55
        '''
        s = BitArray(ue=value)
        self.num_ref_frames = s

    def set__gaps_in_frame_num_value_allowed_flag(self, bool_value):
        '''
        set gaps_in_frame_num_value_allowed_flag in SPS, foramt: u(1)
        : param value: described on page 55
        '''
        if (bool_value):
            self.gaps_in_frame_num_value_allowed_flag = '0b1'
        else:
            self.gaps_in_frame_num_value_allowed_flag = '0b0'

    def set__pic_width_in_mbs_minus_1(self, width):
        '''
        set pic_width_in_mbs_minus_1 in SPS, foramt: ue(v)
        : param width: video width, according to page 55 formula 7-3, 7-4, 7-5
        '''
        MB_width = 16
        pic_width_in_mbs_minus_1 = int( width/MB_width - 1 )
        s = BitArray(ue=pic_width_in_mbs_minus_1)
        self.pic_width_in_mbs_minus_1 = s

    def set__pic_height_in_map_units_minus1(self, height):
        '''
        set pic_height_in_map_units_minus1 in SPS, foramt: ue(v)
        : param width: video height, according to page 55 formula 7-6, 7-7
        '''
        MB_height = 16
        pic_height_in_map_units_minus_1 = int( height/MB_height - 1 )
        s = BitArray(ue=pic_height_in_map_units_minus_1)
        self.pic_height_in_map_units_minus_1 = s

    def set__frame_mbs_only_flag(self, bool_value):
        '''
        set frame_mbs_only_flag in SPS, foramt: ue(1)
        : param bool_value: have or not have field slices or field MBs, according to page 55
        '''
        if (bool_value):
            self.frame_mbs_only_flag = '0b1'
        else:
            self.frame_mbs_only_flag = '0b0'
            # todo: add mb_adaptive_frame_field_flag
            #mb_adaptive_frame_field_flag = '0b0' #u(1) TODO
            # self.frame_mbs_only_flag.append(mb_adaptive_frame_field_flag) #TODO

    def set__direct_8x8_inference_flag(self, bool_value):
        '''
        set direct_8x8_inference_flag in SPS, foramt: ue(v)
        : param bool_value: Specifies how certain B macroblock motion vectors are derived on page 55
        '''
        if (bool_value):
            self.direct_8x8_inference_flag = '0b1'
        else:
            self.direct_8x8_inference_flag = '0b0'

    def set__frame_cropping_flag(self, bool_value):
        '''
        set frame_cropping_flag in SPS, foramt: ue(v)
        : param bool_value: Specifies how certain B macroblock motion vectors are derived on page 55
        '''
        if (bool_value):
            self.frame_cropping_flag = '0b1'
            # TODO add more flags
            # frame_crop_left_offset
            # frame_crop_left_offset
            # frame_crop_left_offset
            # frame_crop_bottom_offset
        else:
            self.frame_cropping_flag = '0b0'

    def set__vui_parameters_present_flag(self, bool_value):
        '''
        set vui_parameters_present_flag in SPS, foramt: ue(v)
        : param bool_value: Specifies how certain B macroblock motion vectors are derived on page 55
        '''
        if (bool_value):
            self.vui_parameters_present_flag = '0b1'
            # TODO add more flags
            # vui_parameters_present_flag
        else:
            self.vui_parameters_present_flag = '0b0'

    def export(self, bitstream_output_handler):
        """
        output the binary data into file
        The sequence here is very important, should be exact the same as SPECIFIC of H.264
        """
        self.stream.append(self.profile_idc)
        self.stream.append(self.constraint_set0_flag)
        self.stream.append(self.constraint_set1_flag)
        self.stream.append(self.constraint_set2_flag)
        self.stream.append(self.reserved_zero_2bits)
        self.stream.append(self.level_idc)
        self.stream.append(self.seq_parameter_set_id)
        self.stream.append(self.log2_max_frame_num_minus4)
        self.stream.append(self.pic_order_cnt_type)
        self.stream.append(self.num_ref_frames)
        self.stream.append(self.gaps_in_frame_num_value_allowed_flag)
        self.stream.append(self.pic_width_in_mbs_minus_1)
        self.stream.append(self.pic_height_in_map_units_minus_1)
        self.stream.append(self.frame_mbs_only_flag)
        self.stream.append(self.direct_8x8_inference_flag)
        self.stream.append(self.frame_cropping_flag)
        self.stream.append(self.vui_parameters_present_flag)
        super().rbsp_trailing_bits()

        super().export(bitstream_output_handler)

class PpsStreamer(NaluStreamer):
    """
    Picture Parameter Set class
    Based on 7.3.2.1 setion on page 31 & 7.4.2.2 setion on page 56
    The sequence of set__ function is not important.
    the function export() will take care of the sequence of the SODB.
    """
    def __init__(self, nalu_type):
        super().__init__(nalu_type)

        # use some default value
        s = BitArray(ue=0)
        self.pic_parameter_set_id = s   # ue(v)
        self.seq_parameter_set_id = s # ue(v)
        self.entropy_coding_mode_flag = '0b0' # u(1)
        self.pic_order_present_flag = '0b0' # u(1)
        self.num_slice_groups_minus1 = '0b0' #ue(v)
        # TODO: subclause of num_slice_groups_minus1
        # if (num_slice_groups_minus1>0)

        s = BitArray(ue=9)
        self.num_ref_idx_l0_active_minus1 = s # ue(v)
        self.num_ref_idx_l1_active_minus1 = s # ue(v)

        self.weighted_pred_flag = '0b0' # u(1)
        self.weighted_bipred_idc = '0b00' # u(2)

        s = BitArray(se=0)
        self.pic_init_qp_minus26 = s   # se(v)
        self.pic_init_qs_minus26 = s   # se(v)
        self.chroma_qp_index_offset = s   # se(v)

        self.deblocking_filter_control_present_flag = '0b0' # u(1)
        self.constrained_intra_pred_flag = '0b0' # u(1)
        self.redundant_pic_cnt_present_flag = '0b0' # u(1)

    def export(self, bitstream_output_handler):
        """
        output the binary data into file
        The sequence here is very important, should be exact the same as SPECIFIC of H.264
        """
        self.stream.append(self.pic_parameter_set_id)
        self.stream.append(self.seq_parameter_set_id)
        self.stream.append(self.entropy_coding_mode_flag)
        self.stream.append(self.pic_order_present_flag)
        self.stream.append(self.num_slice_groups_minus1)
        self.stream.append(self.num_ref_idx_l0_active_minus1)
        self.stream.append(self.num_ref_idx_l1_active_minus1)
        self.stream.append(self.weighted_pred_flag)
        self.stream.append(self.weighted_bipred_idc)
        self.stream.append(self.pic_init_qp_minus26)
        self.stream.append(self.pic_init_qs_minus26)
        self.stream.append(self.chroma_qp_index_offset)
        self.stream.append(self.deblocking_filter_control_present_flag)
        self.stream.append(self.constrained_intra_pred_flag)
        self.stream.append(self.redundant_pic_cnt_present_flag)

        super().rbsp_trailing_bits()

        super().export(bitstream_output_handler)

def main():
    # step1, open the file
    f = "E:/temp/output/nalustreamer.264"
    handler = openNaluFile(f)

    # step2, generate sps & pps
    sps = SpsStreamer(nalutypes.NAL_UNIT_TYPE_SPS)
    sps.set__profile_idc(66) # Baseline profile
    sps.set__level_idc(3) # level 3
    sps.set__seq_parameter_set_id(0)
    sps.set__log2_max_frame_num_minus4(0)
    sps.set__pic_order_cnt_type(0)
    sps.set__num_ref_frames(10)
    sps.set__gaps_in_frame_num_value_allowed_flag(False)
    sps.set__pic_width_in_mbs_minus_1(512)
    sps.set__pic_height_in_map_units_minus1(512)
    sps.set__frame_mbs_only_flag(True)
    sps.set__direct_8x8_inference_flag(True)
    sps.set__frame_cropping_flag(False)
    sps.set__vui_parameters_present_flag(False)
    sps.export(handler)

    pps = PpsStreamer(nalutypes.NAL_UNIT_TYPE_PPS)
    pps.export(handler)

    # step3, close the file
    closeNaluFile(handler)

if __name__ == '__main__':
    main()