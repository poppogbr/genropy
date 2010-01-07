#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" GnrDojo Hello World """
import os

import datetime
from gnr.core.gnrbag import Bag, DirectoryResolver

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        
        #root = self.rootLayoutContainer(root)
        #root.data('split',Bag(dict(left_color='lime',right_color='pink')))
        root.script("""
                dojo.require("dojox.grid._data.model");
                var data = %s;
                genro.model = new dojox.grid.data.Table(null, data);

                var subrow1 = [
                	{ name: 'Part Number', rowSpan: 2,width: '200px'  },
                	{ name: 'Min.T.(F)', formatter: formatDegrees ,width: '60px' },
                	{ name: 'Max.Pressure', rowSpan: 2,width: '60px'  }
                ];
                var subrow2 = [
                	{ name: 'Max.T.(F)', formatter: formatDegrees , width: '60px' }
                ];

                var view = {
                	rows: [
                		subrow1,
                		subrow2
                	]
                };

                

                genro.structure = [
                    view
                ];
                function formatDegrees(value){
                	return value + '&deg;';
                };
        """ % self.griddata())
        
        #split=root.splitContainer(height='100%')
        #left=split.contentPane(sizeShare=25,background_color='silver')
        #rightsplit=split.splitContainer(sizeShare=75,orientation='vertical')
        #topright=rightsplit.contentPane(sizeShare=25,background_color='@split.left_color')
        #bottomright=rightsplit.contentPane(sizeShare=75,background_color='@split.right_color')
        #fb=topright.formbuilder(cols=2)
        #fb.textBox(lbl='path',width='40em',value='test.path',default='mydata.disk.root.data.sites')
        #fb.button('getdata',gnrId='xbtn',lbl='',action="""
        #     genro.doWithDataItem('@test.path','genro.xbtn.inUscita','not found')
        #     alert('request done !!!!')
        #""").func('inUscita','result',"""alert("risultato ottenuto: "+asText(result))""")

        root.grid(height='300px',gnrId="mygrid", id="grid", model="=genro.model", structure="=genro.structure",autoWidth=True)

    
    def griddata(self):
        return ("""
         [[ '4001', -946, 931, 647 ],
            [ '4002', -601, 1894, 208 ],
            [ '4003', 456, 791, 132 ],
            [ '4004', -259, 2433, 840 ],
            [ '4005', -982, 3543, 230 ],
            [ '4006', 652, 3285, 195 ],
            [ '4007', 326, 1187, 110 ],
            [ '4008', -960, -271, 70 ],
            [ '4009', 904, 3529, 188 ],
            [ '4010', -149, 406, 412 ],
            [ '4011', 972, 2686, 492 ],
            [ '4012', -321, 346, 724 ],
            [ '4013', -191, 2019, 113 ],
            [ '4014', 57, 3737, 783 ],
            [ '4015', -735, 4262, 500 ],
            [ '4016', 885, 4000, 341 ],
            [ '4017', 316, 645, 101 ],
            [ '4018', 170, 1678, 930 ],
            [ '4019', 656, 4740, 324 ],
            [ '4020', -40, 4002, 218 ],
            [ '4021', -831, -516, 661 ],
            [ '4022', -180, 186, 318 ],
            [ '4023', -363, 1100, 800 ],
            [ '4024', -406, 148, 690 ],
            [ '4025', -754, -146, 979 ],
            [ '4026', 593, 932, 713 ],
            [ '4027', -276, 2033, 858 ]]""")
            
    def griddata__(self):
        return ("""
         [[ '4001', -946, 931, 647 ],
            [ '4002', -601, 1894, 208 ],
            [ '4003', 456, 791, 132 ],
            [ '4004', -259, 2433, 840 ],
            [ '4005', -982, 3543, 230 ],
            [ '4006', 652, 3285, 195 ],
            [ '4007', 326, 1187, 110 ],
            [ '4008', -960, -271, 70 ],
            [ '4009', 904, 3529, 188 ],
            [ '4010', -149, 406, 412 ],
            [ '4011', 972, 2686, 492 ],
            [ '4012', -321, 346, 724 ],
            [ '4013', -191, 2019, 113 ],
            [ '4014', 57, 3737, 783 ],
            [ '4015', -735, 4262, 500 ],
            [ '4016', 885, 4000, 341 ],
            [ '4017', 316, 645, 101 ],
            [ '4018', 170, 1678, 930 ],
            [ '4019', 656, 4740, 324 ],
            [ '4020', -40, 4002, 218 ],
            [ '4021', -831, -516, 661 ],
            [ '4022', -180, 186, 318 ],
            [ '4023', -363, 1100, 800 ],
            [ '4024', -406, 148, 690 ],
            [ '4025', -754, -146, 979 ],
            [ '4026', 593, 932, 713 ],
            [ '4027', -276, 2033, 858 ],
            [ '4028', -777, -118, 659 ],
            [ '4029', 797, 4497, 178 ],
            [ '4030', -311, 1447, 609 ],
            [ '4031', -681, 4463, 67 ],
            [ '4032', 610, 2802, 95 ],
            [ '4033', -421, 194, 971 ],
            [ '4034', 781, 1960, 344 ],
            [ '4035', 593, 853, 444 ],
            [ '4036', 38, 381, 458 ],
            [ '4037', -110, 4026, 183 ],
            [ '4038', 615, 2135, 83 ],
            [ '4039', -47, 731, 543 ],
            [ '4040', -683, 2753, 649 ],
            [ '4041', -539, 3058, 100 ],
            [ '4042', -606, 175, 893 ],
            [ '4043', 77, 3715, 209 ],
            [ '4044', 97, 1181, 400 ],
            [ '4045', -422, 553, 508 ],
            [ '4046', -955, -123, 860 ],
            [ '4047', 936, 2095, 504 ],
            [ '4048', -867, 1887, 940 ],
            [ '4049', 182, 921, 483 ],
            [ '4050', -843, 1415, 220 ],
            [ '4051', -617, 886, 590 ],
            [ '4052', 389, 4559, 932 ],
            [ '4053', 814, 2888, 674 ],
            [ '4054', 545, 2768, 870 ],
            [ '4055', 434, 2622, 944 ],
            [ '4056', -35, 4505, 66 ],
            [ '4057', -397, 4194, 307 ],
            [ '4058', 480, 1798, 258 ],
            [ '4059', 538, 3751, 665 ],
            [ '4060', -285, 4931, 328 ],
            [ '4061', -117, 4195, 83 ],
            [ '4062', 304, 764, 427 ],
            [ '4063', -666, 2990, 291 ],
            [ '4064', -153, 1050, 512 ],
            [ '4065', -142, 4194, 577 ],
            [ '4066', -124, 4186, 65 ],
            [ '4067', -936, -115, 283 ],
            [ '4068', 802, 4990, 238 ],
            [ '4069', -530, 975, 630 ],
            [ '4070', 78, 2995, 249 ],
            [ '4071', -517, 2478, 229 ],
            [ '4072', -825, 4726, 739 ],
            [ '4073', 688, 1242, 992 ],
            [ '4074', 250, 3777, 926 ],
            [ '4075', 139, 2798, 490 ],
            [ '4076', -725, 2381, 942 ],
            [ '4077', -945, 1902, 64 ],
            [ '4078', 447, 4507, 887 ],
            [ '4079', 719, 2133, 741 ],
            [ '4080', 362, 4226, 668 ],
            [ '4081', 550, 1035, 545 ],
            [ '4082', -895, 4034, 818 ],
            [ '4083', 574, 3759, 283 ],
            [ '4084', -15, 3767, 575 ],
            [ '4085', 856, 2739, 871 ],
            [ '4086', -855, -13, 328 ],
            [ '4087', -380, 4500, 734 ],
            [ '4088', 950, 4534, 760 ],
            [ '4089', -957, 3760, 246 ],
            [ '4090', 249, 3739, 342 ],
            [ '4091', -454, 4505, 190 ],
            [ '4092', 475, 2027, 764 ],
            [ '4093', -339, 4244, 171 ],
            [ '4094', -56, 597, 170 ],
            [ '4095', -553, 3912, 210 ],
            [ '4096', -337, 1522, 473 ],
            [ '4097', -829, 708, 272 ],
            [ '4098', -299, 2833, 356 ],
            [ '4099', -198, 1324, 626 ],
            [ '4100', 248, 1267, 229 ],
            [ '4101', -23, 1017, 727 ],
            [ '4102', -24, 4011, 576 ],
            [ '4103', -497, 402, 485 ],
            [ '4104', -246, -127, 684 ],
            [ '4105', -894, 145, 856 ],
            [ '4106', 103, 3702, 842 ],
            [ '4107', -880, 3992, 60 ],
            [ '4108', -297, 3346, 306 ],
            [ '4109', -547, 4623, 817 ],
            [ '4110', -383, 1141, 850 ],
            [ '4111', -744, 3703, 335 ],
            [ '4112', 546, 4554, 562 ],
            [ '4113', 195, 4371, 842 ],
            [ '4114', -723, 3925, 418 ],
            [ '4115', 695, 3408, 241 ],
            [ '4116', -226, 2268, 148 ],
            [ '4117', 538, 3564, 552 ],
            [ '4118', -391, 4874, 908 ],
            [ '4119', -628, 2154, 447 ],
            [ '4120', -3, 3392, 71 ],
            [ '4121', -826, 694, 193 ],
            [ '4122', -511, 3193, 534 ],
            [ '4123', 375, 2977, 221 ],
            [ '4124', 139, 1955, 332 ],
            [ '4125', -369, 3575, 864 ],
            [ '4126', -320, 1706, 511 ],
            [ '4127', -11, 2040, 520 ],
            [ '4128', -363, 4858, 325 ],
            [ '4129', 518, 4480, 707 ],
            [ '4130', 585, 1160, 126 ],
            [ '4131', -821, 731, 251 ],
            [ '4132', 287, 4589, 272 ],
            [ '4133', 112, 4460, 813 ],
            [ '4134', 485, 3749, 323 ],
            [ '4135', -744, 1881, 951 ],
            [ '4136', 10, 4363, 707 ],
            [ '4137', -497, 319, 734 ],
            [ '4138', -525, 3768, 900 ],
            [ '4139', 723, 2451, 702 ],
            [ '4140', 489, 1578, 590 ],
            [ '4141', 209, 1333, 263 ],
            [ '4142', 249, 3276, 203 ],
            [ '4143', -430, 1178, 176 ],
            [ '4144', 253, 2403, 890 ],
            [ '4145', 962, 3918, 687 ],
            [ '4146', 206, 3365, 534 ],
            [ '4147', -305, 2034, 844 ],
            [ '4148', 31, 2866, 966 ],
            [ '4149', 385, 2619, 897 ],
            [ '4150', 934, 3378, 737 ],
            [ '4151', 89, 3254, 346 ],
            [ '4152', -394, 242, 532 ],
            [ '4153', -758, 1420, 726 ],
            [ '4154', -277, 2813, 245 ],
            [ '4155', 111, 3048, 673 ],
            [ '4156', -122, 2826, 752 ],
            [ '4157', 325, 2266, 825 ],
            [ '4158', -56, 4539, 462 ],
            [ '4159', 997, 4661, 761 ],
            [ '4160', -938, 3910, 354 ],
            [ '4161', 595, 2514, 441 ],
            [ '4162', 640, 3875, 570 ],
            [ '4163', 694, 2991, 611 ],
            [ '4164', 261, 2081, 208 ],
            [ '4165', -509, 4019, 146 ],
            [ '4166', 784, 3840, 634 ],
            [ '4167', -269, 1588, 482 ],
            [ '4168', 382, 4043, 705 ],
            [ '4169', -276, 2880, 534 ],
            [ '4170', 986, 4794, 776 ],
            [ '4171', -122, 1128, 107 ],
            [ '4172', 877, 3331, 712 ],
            [ '4173', 428, 1940, 604 ],
            [ '4174', 848, 3039, 878 ],
            [ '4175', -940, 4251, 608 ],
            [ '4176', -616, 287, 219 ],
            [ '4177', 488, 1662, 367 ],
            [ '4178', 3, 3993, 235 ],
            [ '4179', -633, 4895, 52 ],
            [ '4180', -452, 36, 237 ],
            [ '4181', 627, 4981, 234 ],
            [ '4182', -888, 312, 395 ],
            [ '4183', 367, 988, 170 ],
            [ '4184', -538, 4908, 749 ],
            [ '4185', -347, 2492, 617 ],
            [ '4186', -906, -161, 485 ],
            [ '4187', -940, 307, 738 ],
            [ '4188', 103, 1337, 726 ],
            [ '4189', -567, 47, 390 ],
            [ '4190', -791, 3353, 111 ],
            [ '4191', 643, 2924, 727 ],
            [ '4192', 598, 4753, 653 ],
            [ '4193', 344, 3752, 538 ],
            [ '4194', 739, 3383, 485 ],
            [ '4195', 879, 4224, 958 ],
            [ '4196', -907, 1781, 845 ],
            [ '4197', 61, 3678, 603 ],
            [ '4198', 288, 1158, 197 ],
            [ '4199', -438, -262, 843 ],
            [ '4200', 835, 4656, 415 ],
            [ '4201', -29, 3407, 382 ],
            [ '4202', -651, 3871, 373 ],
            [ '4203', 372, 3256, 446 ],
            [ '4204', 385, 721, 847 ],
            [ '4205', 38, 1608, 974 ],
            [ '4206', 837, 2696, 84 ],
            [ '4207', 626, 798, 347 ],
            [ '4208', -658, -552, 900 ],
            [ '4209', 980, 2643, 502 ],
            [ '4210', 133, 4181, 650 ],
            [ '4211', -272, 4348, 623 ],
            [ '4212', -621, 3904, 999 ],
            [ '4213', 121, 3547, 729 ],
            [ '4214', -782, 1406, 374 ],
            [ '4215', -406, 2092, 831 ],
            [ '4216', -227, 4052, 950 ],
            [ '4217', 844, 4546, 743 ],
            [ '4218', -270, 4403, 79 ],
            [ '4219', -836, 2431, 990 ],
            [ '4220', -48, 4298, 841 ],
            [ '4221', 829, 2187, 662 ],
            [ '4222', 676, 1689, 300 ],
            [ '4223', -33, 1560, 580 ],
            [ '4224', -705, 698, 383 ],
            [ '4225', -368, 2156, 338 ],
            [ '4226', 32, 450, 875 ],
            [ '4227', 699, 4918, 68 ],
            [ '4228', -426, 3608, 281 ],
            [ '4229', -229, 4532, 534 ],
            [ '4230', 536, 1828, 791 ],
            [ '4231', -780, 2897, 395 ],
            [ '4232', -112, 1831, 903 ],
            [ '4233', -351, 119, 517 ],
            [ '4234', 574, 1517, 666 ],
            [ '4235', 770, 3662, 448 ],
            [ '4236', -289, 742, 975 ],
            [ '4237', -365, 389, 900 ],
            [ '4238', -506, 3165, 190 ],
            [ '4239', 578, 4103, 55 ],
            [ '4240', -584, 3491, 715 ],
            [ '4241', -72, 3324, 881 ],
            [ '4242', -266, 803, 753 ],
            [ '4243', 247, 4902, 978 ],
            [ '4244', 493, 4756, 503 ],
            [ '4245', 705, 1852, 909 ],
            [ '4246', -632, 245, 134 ],
            [ '4247', -975, 3417, 266 ],
            [ '4248', -653, 4720, 868 ],
            [ '4249', 794, 1484, 592 ],
            [ '4250', 721, 2609, 844 ],
            [ '4251', 990, 3045, 253 ],
            [ '4252', -504, 2922, 149 ],
            [ '4253', -842, 1623, 649 ],
            [ '4254', -305, 3868, 241 ],
            [ '4255', -355, 2290, 988 ],
            [ '4256', -70, 1289, 719 ],
            [ '4257', -312, 986, 794 ],
            [ '4258', 664, 2895, 721 ],
            [ '4259', -769, 258, 875 ],
            [ '4260', 632, 4075, 367 ],
            [ '4261', -515, 1365, 442 ],
            [ '4262', -547, 4454, 304 ],
            [ '4263', 695, 2229, 243 ],
            [ '4264', 356, 3816, 791 ],
            [ '4265', 10, 4614, 980 ],
            [ '4266', -28, 2391, 444 ],
            [ '4267', -351, 581, 310 ],
            [ '4268', 461, 2715, 881 ],
            [ '4269', 225, 1326, 336 ],
            [ '4270', 612, 3800, 908 ],
            [ '4271', 174, 2381, 445 ],
            [ '4272', -288, 4050, 225 ],
            [ '4273', -89, 4316, 499 ],
            [ '4274', 593, 3072, 808 ],
            [ '4275', -454, 1100, 858 ],
            [ '4276', 917, 3908, 431 ],
            [ '4277', 499, 4338, 629 ],
            [ '4278', -423, 2821, 180 ],
            [ '4279', 912, 4883, 520 ],
            [ '4280', 395, 4195, 688 ],
            [ '4281', -829, 3283, 104 ],
            [ '4282', 720, 2535, 569 ],
            [ '4283', 162, 1154, 834 ],
            [ '4284', -186, 2418, 450 ],
            [ '4285', -213, 2320, 273 ],
            [ '4286', 216, 1900, 994 ],
            [ '4287', -968, 213, 206 ],
            [ '4288', 763, 4253, 235 ],
            [ '4289', -740, 4108, 654 ],
            [ '4290', 152, 802, 169 ],
            [ '4291', -509, 939, 383 ],
            [ '4292', 241, 618, 701 ],
            [ '4293', 423, 2013, 812 ],
            [ '4294', 140, 3212, 426 ],
            [ '4295', 106, 2816, 242 ],
            [ '4296', -534, 3726, 826 ],
            [ '4297', 230, 4981, 222 ],
            [ '4298', 32, 1897, 405 ],
            [ '4299', 477, 3742, 194 ],
            [ '4300', -964, 1475, 595 ],
            [ '4301', 955, 1583, 142 ],
            [ '4302', -52, 3942, 922 ],
            [ '4303', -812, 1306, 811 ],
            [ '4304', -692, 2985, 429 ],
            [ '4305', 857, 4230, 316 ],
            [ '4306', -835, 413, 441 ],
            [ '4307', -79, 1805, 975 ],
            [ '4308', -592, 1509, 113 ],
            [ '4309', -403, 1116, 341 ],
            [ '4310', 111, 1557, 114 ],
            [ '4311', -251, 2609, 230 ],
            [ '4312', 723, 4756, 203 ],
            [ '4313', 942, 1620, 437 ],
            [ '4314', 116, 3884, 145 ],
            [ '4315', 940, 3743, 229 ],
            [ '4316', 410, 2370, 126 ],
            [ '4317', -324, 2327, 905 ],
            [ '4318', -228, 1667, 401 ],
            [ '4319', 69, 2738, 888 ],
            [ '4320', -721, 3560, 749 ],
            [ '4321', -350, 4999, 852 ],
            [ '4322', 453, 1002, 877 ],
            [ '4323', -624, 4071, 192 ],
            [ '4324', 69, 3263, 554 ],
            [ '4325', -24, 2621, 407 ],
            [ '4326', 949, 2092, 480 ],
            [ '4327', 233, 4341, 215 ],
            [ '4328', -136, 4146, 657 ],
            [ '4329', 850, 3547, 665 ],
            [ '4330', -354, 1459, 588 ],
            [ '4331', -131, 1413, 838 ],
            [ '4332', -454, 3889, 519 ],
            [ '4333', 530, 3403, 690 ],
            [ '4334', -388, 4601, 513 ],
            [ '4335', 899, 4759, 456 ],
            [ '4336', -546, 1495, 952 ],
            [ '4337', -182, 1852, 994 ],
            [ '4338', -187, 4963, 404 ],
            [ '4339', -757, 486, 214 ],
            [ '4340', 226, 3668, 559 ],
            [ '4341', 93, 3755, 939 ],
            [ '4342', -860, 3045, 108 ],
            [ '4343', -813, 25, 164 ],
            [ '4344', -814, -679, 342 ],
            [ '4345', 280, 3001, 402 ],
            [ '4346', 233, 4686, 938 ],
            [ '4347', -79, 1676, 957 ],
            [ '4348', 326, 2270, 458 ],
            [ '4349', 735, 3873, 606 ],
            [ '4350', -404, 2051, 517 ],
            [ '4351', -777, 479, 672 ],
            [ '4352', 200, 4248, 170 ],
            [ '4353', 603, 1329, 428 ],
            [ '4354', 95, 3135, 995 ],
            [ '4355', 740, 2031, 388 ],
            [ '4356', 370, 1894, 171 ],
            [ '4357', 38, 1958, 409 ],
            [ '4358', -611, 3999, 651 ],
            [ '4359', -243, 1881, 394 ],
            [ '4360', -39, 540, 413 ],
            [ '4361', 78, 4701, 278 ],
            [ '4362', -263, 4510, 315 ],
            [ '4363', -433, 3555, 644 ],
            [ '4364', -290, 4136, 445 ],
            [ '4365', -585, -241, 573 ],
            [ '4366', 586, 4458, 446 ],
            [ '4367', -909, 184, 501 ],
            [ '4368', 197, 637, 428 ],
            [ '4369', -930, 291, 770 ],
            [ '4370', 236, 4373, 557 ],
            [ '4371', -227, 3126, 573 ],
            [ '4372', -119, 4235, 320 ],
            [ '4373', 899, 2507, 225 ],
            [ '4374', -616, 3484, 191 ],
            [ '4375', 343, 2184, 674 ],
            [ '4376', 124, 507, 543 ],
            [ '4377', -555, 1996, 617 ],
            [ '4378', 313, 4435, 385 ],
            [ '4379', -125, 1857, 906 ],
            [ '4380', -220, 1137, 85 ],
            [ '4381', -809, 1868, 649 ],
            [ '4382', -211, 2910, 648 ],
            [ '4383', -594, 4897, 825 ],
            [ '4384', -373, 4426, 938 ],
            [ '4385', -82, 4518, 626 ],
            [ '4386', -230, 966, 404 ],
            [ '4387', -183, 4101, 53 ],
            [ '4388', -707, -96, 66 ],
            [ '4389', 874, 1894, 748 ],
            [ '4390', -673, 2955, 996 ],
            [ '4391', 993, 4266, 353 ],
            [ '4392', 416, 3891, 627 ],
            [ '4393', 539, 4692, 561 ],
            [ '4394', 578, 3270, 803 ],
            [ '4395', -932, -484, 751 ],
            [ '4396', 84, 3692, 112 ],
            [ '4397', 206, 2738, 429 ],
            [ '4398', 326, 1204, 762 ],
            [ '4399', -851, 632, 262 ],
            [ '4400', 206, 4582, 344 ],
            [ '4401', 104, 4540, 850 ],
            [ '4402', -984, 2933, 615 ],
            [ '4403', 364, 1699, 325 ],
            [ '4404', 936, 4160, 364 ],
            [ '4405', 547, 2523, 485 ],
            [ '4406', 120, 1917, 66 ],
            [ '4407', 318, 2048, 419 ],
            [ '4408', -835, 1115, 212 ],
            [ '4409', 245, 2540, 354 ],
            [ '4410', 430, 4614, 419 ],
            [ '4411', 757, 4048, 220 ],
            [ '4412', -408, 1742, 65 ],
            [ '4413', 352, 1327, 292 ],
            [ '4414', -589, 2909, 588 ],
            [ '4415', 21, 3529, 524 ],
            [ '4416', -765, -226, 558 ],
            [ '4417', -839, 1530, 228 ],
            [ '4418', 838, 2913, 716 ],
            [ '4419', -841, 3631, 755 ],
            [ '4420', 82, 1671, 653 ],
            [ '4421', -101, 1549, 192 ],
            [ '4422', 371, 3288, 256 ],
            [ '4423', -591, 1017, 752 ],
            [ '4424', -802, 762, 757 ],
            [ '4425', 434, 2332, 700 ],
            [ '4426', 68, 3558, 562 ],
            [ '4427', -844, 3800, 750 ],
            [ '4428', 261, 431, 673 ],
            [ '4429', 459, 567, 988 ],
            [ '4430', 382, 1744, 84 ],
            [ '4431', 64, 3269, 167 ],
            [ '4432', -648, -342, 380 ],
            [ '4433', -308, 933, 968 ],
            [ '4434', -40, 392, 432 ],
            [ '4435', 204, 847, 317 ],
            [ '4436', 967, 3465, 904 ],
            [ '4437', -299, 4585, 405 ],
            [ '4438', -713, 107, 427 ],
            [ '4439', -988, 16, 906 ],
            [ '4440', -753, 1812, 279 ],
            [ '4441', 685, 2219, 163 ],
            [ '4442', -636, 4518, 285 ],
            [ '4443', 639, 3034, 226 ],
            [ '4444', 209, 1293, 338 ],
            [ '4445', -136, 4718, 469 ],
            [ '4446', -272, 3522, 583 ],
            [ '4447', 466, 4286, 137 ],
            [ '4448', -573, 1053, 766 ],
            [ '4449', 9, 4776, 147 ],
            [ '4450', -603, 1274, 544 ],
            [ '4451', 313, 4737, 74 ],
            [ '4452', 92, 756, 408 ],
            [ '4453', 321, 3066, 180 ],
            [ '4454', -128, 1581, 533 ],
            [ '4455', 610, 1146, 581 ],
            [ '4456', -920, 1750, 144 ],
            [ '4457', -564, 2329, 296 ],
            [ '4458', 372, 4686, 662 ],
            [ '4459', -203, 4083, 743 ],
            [ '4460', -508, 1985, 263 ],
            [ '4461', 239, 4845, 511 ],
            [ '4462', 247, 1226, 200 ],
            [ '4463', -484, 1103, 406 ],
            [ '4464', 615, 3416, 845 ],
            [ '4465', -136, 3110, 142 ],
            [ '4466', 802, 2688, 795 ],
            [ '4467', -259, 1992, 567 ],
            [ '4468', 710, 3319, 409 ],
            [ '4469', 218, 2485, 577 ],
            [ '4470', 440, 1187, 832 ],
            [ '4471', -346, 739, 224 ],
            [ '4472', -306, 3901, 195 ],
            [ '4473', 414, 4540, 675 ],
            [ '4474', -104, 504, 239 ],
            [ '4475', -143, 4380, 838 ],
            [ '4476', 871, 2142, 74 ],
            [ '4477', -709, 4711, 741 ],
            [ '4478', 407, 1601, 518 ],
            [ '4479', -651, 1711, 970 ],
            [ '4480', -97, 350, 114 ],
            [ '4481', 538, 2654, 502 ],
            [ '4482', -60, 3067, 948 ],
            [ '4483', 514, 2873, 410 ],
            [ '4484', 814, 3990, 434 ],
            [ '4485', -704, 13, 254 ],
            [ '4486', 849, 1787, 834 ],
            [ '4487', 486, 2613, 443 ],
            [ '4488', -619, 3266, 975 ],
            [ '4489', -472, 3869, 758 ],
            [ '4490', 278, 2191, 540 ],
            [ '4491', -99, 823, 376 ],
            [ '4492', 34, 4745, 609 ],
            [ '4493', 660, 902, 242 ],
            [ '4494', 574, 3146, 394 ],
            [ '4495', 590, 2535, 895 ],
            [ '4496', -491, 1700, 131 ],
            [ '4497', 599, 4115, 613 ],
            [ '4498', -804, 1749, 158 ],
            [ '4499', 398, 3690, 708 ]]
        """)
