import numpy as np
from IQDataProtocol.WSR98DProtocol import Dual_IQ
from util import _prepare_for_read, _unpack_from_buf, IQ_unpack


class DualPolData(object): 
    '''
    decode the IQ signal data
    '''
    def __init__(self, filename, station_lon=None, station_lat=None, station_alt=None, debug_model = 0):
        super(DualPolData,self).__init__()
        self.filename = filename
        self.station_lon = station_lon
        self.station_lat = station_lat
        self.station_alt = station_alt
        self.debug_model = debug_model
        self.fid = _prepare_for_read(self.filename)  ##对压缩的文件进行解码
        self._check_dualpol_data()  #check whether the file is Dual-Pol IQ data
        self.header = self._parse_TSHeader()
        self.radial = self._parse_radial()
        self.nrays = len(self.radial)
        print("nrays: ",self.nrays)
        self.azimuth = self.get_azimuth()
        self.elevation = self.get_elevation()
        self.fid.close()

    def _parse_TSHeader(self):
        TSHeader = {}                                                                                                                                                                       
        print(Dual_IQ.TSHeaderBlockSize)
        fixed_buf = self.fid.read(Dual_IQ.TSHeaderBlockSize)  ##读取前面固定头的信息
        TSHeader, size = _unpack_from_buf(fixed_buf, \
                                                              Dual_IQ.TSHeaderPos,
                                                              Dual_IQ.TSHeader)                                                                                      
        return TSHeader
                                                              
    def _parse_radial(self):
        #IQ_length = (channel*binnum+firstbinnum)*2*2
        radial = []
        self.fid.seek(0, 0)
        self.fid.seek(Dual_IQ.TSSweepHeaderPos, 0)
        buf = self.fid.read(Dual_IQ.TSSweepBlockSize, )
        iteration_no = 0
        while len(buf) == Dual_IQ.TSSweepBlockSize: # and iteration_no < 100: 
            iteration_no += 1 
            RadialDict, size = _unpack_from_buf(buf, 0, Dual_IQ.TSSweepHeader())
            #print(RadialDict)
            self.chan = int(RadialDict['chan'])
            self.binnum = int(RadialDict['binnum'])
            #print('bin no.',RadialDict['binnum'])
            self.burstbinnum = int(RadialDict['burstbinnum'])
            self.LengthOfData = ( self.chan * self.binnum+ self.burstbinnum ) * 2 * 2
            if self.LengthOfData > 1:
                RadialDict['Azimuth'] = RadialDict['Azimuth'] / 100.
                RadialDict['Elevation'] = RadialDict['Elevation'] / 100.
            else:
                RadialDict['Azimuth'] = np.nan
                RadialDict['Elevation'] = np.nan
            #print("length",self.LengthOfData)
            RadialDict['fields'] = self._parse_radial_single()
            #RadialDict['H_IQ']=unpack(buf,'uint16',data['d'][-1]['binnum']*2,ptr+128)
            radial.append(RadialDict)
            buf = self.fid.read(Dual_IQ.TSSweepBlockSize)
            if (self.debug_model == 1):
                print(radial[-1])
        return radial
    
    def _parse_radial_single(self):
        '''decode for each radial'''
        radial_var = {}
        Hdata_buf = self.fid.read( self.binnum * 2 *2)
        Hdata_tmp = (np.frombuffer(Hdata_buf, dtype="uint16", offset=0)).astype(int) # <表示字节顺序，小端；U表示Unicode，数据类型，1表示元素位长，数据大小
        #numpy.frombuffer(buffer, dtype=float, count=-1, offset=0)
        #16 bit是2字节
        radial_var['H_I'], radial_var['H_Q'] = IQ_unpack(Hdata_tmp)
        radial_var['Pt_H'] = np.power(radial_var['H_I'],2) + np.power(radial_var['H_Q'],2)

        if self.chan == 2:
            Vdata_buf = self.fid.read( self.binnum * 2 *2 )
            Vdata_tmp = (np.frombuffer(Vdata_buf, dtype="uint16", offset=0)).astype(int)
            radial_var['V_I'], radial_var['V_Q'] = IQ_unpack(Vdata_tmp)
            radial_var['Pt_V'] = np.power(radial_var['V_I'],2) + np.power(radial_var['V_Q'],2)

        Burst_buf = self.fid.read( self.burstbinnum * 2 *2 )
        BurstData_tmp = (np.frombuffer(Burst_buf, dtype="uint16", offset=0)).astype(int)
        
        return radial_var
                                               
    def _check_dualpol_data(self):
        """
        :param fid: file fid
        :return:
        """
        assert self.fid.read(0) in b"34", 'It is not a dual-pol signal!'
        self.fid.seek(0, 0)
        return

    def get_azimuth(self):
        """
        获取每根径向的方位角
        :return:(nRays)
        """
        az = np.array([self.radial[iray]['Azimuth'] for iray in range(self.nrays)])
        az = np.where(az < 0, az + 360, az)
        return az

    def get_elevation(self):
        """
        获取每根径向的仰角
        :return: (nRays)
        """
        return np.array([self.radial[iray]['Elevation'] for iray in range(self.nrays)])
    
