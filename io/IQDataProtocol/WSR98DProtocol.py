import numpy as np

SHORT = 'h'
INT = 'i'
FLOAT = 'f'
CHAR = 's'

class DualFormat(object):

    def __init__(self):
        self.TSHeaderPos = 0
        self.TSSweepHeaderPos = 128+256
        self.TSHeaderBlockSize = 128
        self.TSSweepBlockSize = 128
        self.flag2Product = {1:'H_I', 2:'H_Q', 3:'V_I', 4:'V_Q', 5:'velocity', 6:'reflectivity', 7:'ZDR', 8:'LDR',\
                             9:'CC', 10:'PhiDP', 11:'KDP'}

        self.TSHeader = (
            ('Version', 'B'),       # 1,2: single polarization; 3: dual-pol version; 4: burst signal included
            ('SiteName', '16s'),  
            ('spared1', INT),  
            ('spared2', CHAR),  
            ('pol', 'B'),           # h = 0, v = 1, hv =3
            ('pulsewidth', FLOAT),  # pulse width in microseconds
            ('calibration', FLOAT), # horizaontal calibration reflectivity (dBZ at 1 km)
            ('noise', FLOAT),       # noise level of the system in dBm
            ('freq', FLOAT),        # MHz
            ('firstbin', SHORT),    # first bin range in meter
            ('phasecode', CHAR),
            ('vnoise', FLOAT),      # noise level of v channel
            ('vcalib', FLOAT),      # vertical calibration reflectivity (dBZ at 1 km)
            ('pad', '78s')
        )    

    def TSSweepHeader(self):
        TSSweepHeaderBlock = (
            ('time', '8s'),  # 
            ('clock', INT),  # # 径向数据采集时间除去秒后留下的毫秒数
            ('seqnum', INT),  # 序号，每个体扫径向从1开始计数
            ('latitude', INT),  # 径向数，每个扫描从1开始
            ('longitude', INT),  # 仰角编号，从1开始
            ('height', INT),
            ('Azimuth', SHORT),  # 方位角  in scale of 1/100 degree
            ('Elevation', SHORT),  # 仰角   in scale of 1/100 degree
            ('prf', SHORT),  # 径向数据采集时间 UTC 从19700101 00：00开始 秒
            ('samples', SHORT),  
            ('binnum', SHORT),  # 本径向数据块的长度
            ('reso', SHORT),  # 径向数据
            ('mode', 'B'),  # 保留
            ('state', INT),  # radial state,0 cut_start,1 cut_mid,2 cut_end,3 vol_start,4 vol_end
            ('sploblank', 'B'),  # true if the radial is sector blanking
            ('nextprf', SHORT),  # PRF of next sweep
            ('burstmag', FLOAT),  # magnitude of burst
            ('burstang', FLOAT),  # angle of burst
            ('swpidx', SHORT),  # index of this sweep in the radial
            ('anglereso', SHORT),  # angle (azimuth for ppi ) resolution
            ('chan', 'B'),  # channnel number in this pulse 1 for h only and v only,2 for h+v
            ('length', 'H'),  # for rawiq, internal use
            ('burstbinnum', SHORT), 
            ('pad_reserved', '63s')
        )
        return TSSweepHeaderBlock

Dual_IQ = DualFormat()