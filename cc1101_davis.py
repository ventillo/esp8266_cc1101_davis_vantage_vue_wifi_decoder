import utime
import gc
import machine

ss = machine.Pin(15,machine.Pin.OUT) # Chip select /  HCS
so = machine.Pin(12)                 # HMISO
si = machine.Pin(13)                 # HMOSI
sck = machine.Pin(14)                # HSCLK
interrupt = machine.Pin(2) # Interrupt for packet available

gc.collect()

class CC1101(object):
    def __init__(self):
        self.debug = 1
        self.hspi = machine.SPI(1, baudrate=600000, polarity=0, phase=0)
        self.PA_TABLE = [0xC0, 0xC0, 0xC0, 0xC0,
                         0xC0, 0xC0, 0xC0, 0xC0]

        self.FREQ_2 = [0x21, 0x21, 0x21, 0x21, 0x21]
        self.FREQ_1 = [0x62, 0x65, 0x67, 0x64, 0x66]
        self.FREQ_0 = [0xE2, 0x40, 0x9D, 0x11, 0x6F]

        self.CRC_TABLE = [
            0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50A5, 0x60C6, 0x70E7,
            0x8108, 0x9129, 0xA14A, 0xB16B, 0xC18C, 0xD1AD, 0xE1CE, 0xF1EF,
            0x1231, 0x0210, 0x3273, 0x2252, 0x52B5, 0x4294, 0x72F7, 0x62D6,
            0x9339, 0x8318, 0xB37B, 0xA35A, 0xD3BD, 0xC39C, 0xF3FF, 0xE3DE,
            0x2462, 0x3443, 0x0420, 0x1401, 0x64E6, 0x74C7, 0x44A4, 0x5485,
            0xA56A, 0xB54B, 0x8528, 0x9509, 0xE5EE, 0xF5CF, 0xC5AC, 0xD58D,
            0x3653, 0x2672, 0x1611, 0x0630, 0x76D7, 0x66F6, 0x5695, 0x46B4,
            0xB75B, 0xA77A, 0x9719, 0x8738, 0xF7DF, 0xE7FE, 0xD79D, 0xC7BC,
            0x48C4, 0x58E5, 0x6886, 0x78A7, 0x0840, 0x1861, 0x2802, 0x3823,
            0xC9CC, 0xD9ED, 0xE98E, 0xF9AF, 0x8948, 0x9969, 0xA90A, 0xB92B,
            0x5AF5, 0x4AD4, 0x7AB7, 0x6A96, 0x1A71, 0x0A50, 0x3A33, 0x2A12,
            0xDBFD, 0xCBDC, 0xFBBF, 0xEB9E, 0x9B79, 0x8B58, 0xBB3B, 0xAB1A,
            0x6CA6, 0x7C87, 0x4CE4, 0x5CC5, 0x2C22, 0x3C03, 0x0C60, 0x1C41,
            0xEDAE, 0xFD8F, 0xCDEC, 0xDDCD, 0xAD2A, 0xBD0B, 0x8D68, 0x9D49,
            0x7E97, 0x6EB6, 0x5ED5, 0x4EF4, 0x3E13, 0x2E32, 0x1E51, 0x0E70,
            0xFF9F, 0xEFBE, 0xDFDD, 0xCFFC, 0xBF1B, 0xAF3A, 0x9F59, 0x8F78,
            0x9188, 0x81A9, 0xB1CA, 0xA1EB, 0xD10C, 0xC12D, 0xF14E, 0xE16F,
            0x1080, 0x00A1, 0x30C2, 0x20E3, 0x5004, 0x4025, 0x7046, 0x6067,
            0x83B9, 0x9398, 0xA3FB, 0xB3DA, 0xC33D, 0xD31C, 0xE37F, 0xF35E,
            0x02B1, 0x1290, 0x22F3, 0x32D2, 0x4235, 0x5214, 0x6277, 0x7256,
            0xB5EA, 0xA5CB, 0x95A8, 0x8589, 0xF56E, 0xE54F, 0xD52C, 0xC50D,
            0x34E2, 0x24C3, 0x14A0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
            0xA7DB, 0xB7FA, 0x8799, 0x97B8, 0xE75F, 0xF77E, 0xC71D, 0xD73C,
            0x26D3, 0x36F2, 0x0691, 0x16B0, 0x6657, 0x7676, 0x4615, 0x5634,
            0xD94C, 0xC96D, 0xF90E, 0xE92F, 0x99C8, 0x89E9, 0xB98A, 0xA9AB,
            0x5844, 0x4865, 0x7806, 0x6827, 0x18C0, 0x08E1, 0x3882, 0x28A3,
            0xCB7D, 0xDB5C, 0xEB3F, 0xFB1E, 0x8BF9, 0x9BD8, 0xABBB, 0xBB9A,
            0x4A75, 0x5A54, 0x6A37, 0x7A16, 0x0AF1, 0x1AD0, 0x2AB3, 0x3A92,
            0xFD2E, 0xED0F, 0xDD6C, 0xCD4D, 0xBDAA, 0xAD8B, 0x9DE8, 0x8DC9,
            0x7C26, 0x6C07, 0x5C64, 0x4C45, 0x3CA2, 0x2C83, 0x1CE0, 0x0CC1,
            0xEF1F, 0xFF3E, 0xCF5D, 0xDF7C, 0xAF9B, 0xBFBA, 0x8FD9, 0x9FF8,
            0x6E17, 0x7E36, 0x4E55, 0x5E74, 0x2E93, 0x3EB2, 0x0ED1, 0x1EF0]
        self.BUFFER_SIZE = 16
        self.DAVIS_PACKET_LENGTH = 10
        self.rxBuffer = []
        self.rxBufferIndex = 0
        self.rxBufferLength = 0
        self.hopIndex = 0
        self.freqComp = [0, 0, 0, 0, 0]

        # CC1101 Transfer Types.
        self.WRITE_BURST = 0x40
        self.READ_SINGLE = 0x80
        self.READ_BURST  = 0xC0

        # Davis Register Configuration Settings.
        self.DAVIS_IOCFG2   = 0x2E         # GDO2 Output Pin Configuration
        self.DAVIS_IOCFG1   = 0x2E         # GDO1 Output Pin Configuration
        self.DAVIS_IOCFG0   = 0x01         # GDO0 Output Pin Configuration
        self.DAVIS_FIFOTHR  = 0x42         # RX FIFO and TX FIFO Thresholds
        self.DAVIS_SYNC1    = 0xCB         # Synchronization word, high byte
        self.DAVIS_SYNC0    = 0x89         # Synchronization word, low byte
        self.DAVIS_PKTLEN   = 0x0A         # Packet Length
        self.DAVIS_PKTCTRL1 = 0xC4         # Packet Automation Control
        self.DAVIS_PKTCTRL0 = 0x00         # Packet Automation Control
        self.DAVIS_ADDR     = 0x00         # Device Address
        self.DAVIS_CHANNR   = 0x00         # Channel Number
        self.DAVIS_FSCTRL1  = 0x06         # Frequency Synthesizer Control
        self.DAVIS_FSCTRL0  = 0xF0         # Frequency Synthesizer Control
        self.DAVIS_FREQ2    = 0x23         # Frequency Control Word, High Byte
        self.DAVIS_FREQ1    = 0x0D         # Frequency Control Word, Middle Byte
        self.DAVIS_FREQ0    = 0x97         # Frequency Control Word, Low Byte
        self.DAVIS_MDMCFG4  = 0xC9         # Modem Configuration
        self.DAVIS_MDMCFG3  = 0x83         # Modem Configuration
        self.DAVIS_MDMCFG2  = 0x12         # Modem Configuration
        self.DAVIS_MDMCFG1  = 0x21         # Modem Configuration
        self.DAVIS_MDMCFG0  = 0xF9         # Modem Configuration
        self.DAVIS_DEVIATN  = 0x24         # Modem Deviation Setting
        self.DAVIS_MCSM2    = 0x07         # Main Radio Control State Machine Configuration
        self.DAVIS_MCSM1    = 0x00         # Main Radio Control State Machine Configuration
        self.DAVIS_MCSM0    = 0x18         # Main Radio Control State Machine Configuration
        self.DAVIS_FOCCFG   = 0x16         # Frequency Offset Compensation Configuration
        self.DAVIS_BSCFG    = 0x6C         # Bit Synchronization Configuration
        self.DAVIS_AGCCTRL2 = 0x43         # AGC Control
        self.DAVIS_AGCCTRL1 = 0x40         # AGC Control
        self.DAVIS_AGCCTRL0 = 0x91         # AGC Control
        self.DAVIS_WOREVT1  = 0x87         # High Byte Event0 Timeout
        self.DAVIS_WOREVT0  = 0x6B         # Low Byte Event0 Timeout
        self.DAVIS_WORCTRL  = 0xF8         # Wake On Radio Control
        self.DAVIS_FREND1   = 0x56         # Front End RX Configuration
        self.DAVIS_FREND0   = 0x10         # Front End TX Configuration
        self.DAVIS_FSCAL3   = 0xEF         # Frequency Synthesizer Calibration
        self.DAVIS_FSCAL2   = 0x2B         # Frequency Synthesizer Calibration
        self.DAVIS_FSCAL1   = 0x2F         # Frequency Synthesizer Calibration
        self.DAVIS_FSCAL0   = 0x1F         # Frequency Synthesizer Calibration
        self.DAVIS_RCCTRL1  = 0x00         # RC Oscillator Configuration
        self.DAVIS_RCCTRL0  = 0x00         # RC Oscillator Configuration
        self.DAVIS_FSTEST   = 0x59         # Frequency Synthesizer Calibration Control
        self.DAVIS_PTEST    = 0x7F         # Production Test
        self.DAVIS_AGCTEST  = 0x3F         # AGC Test
        self.DAVIS_TEST2    = 0x81         # Various Test Settings
        self.DAVIS_TEST1    = 0x35         # Various Test Settings
        self.DAVIS_TEST0    = 0x09         # Various Test Settings

        self.CC1101_IOCFG2   = 0x00        # GDO2 Output Pin Configuration
        self.CC1101_IOCFG1   = 0x01        # GDO1 Output Pin Configuration
        self.CC1101_IOCFG0   = 0x02        # GDO0 Output Pin Configuration
        self.CC1101_FIFOTHR  = 0x03        # RX FIFO and TX FIFO Thresholds
        self.CC1101_SYNC1    = 0x04        # Sync Word, High Byte
        self.CC1101_SYNC0    = 0x05        # Sync Word, Low Byte
        self.CC1101_PKTLEN   = 0x06        # Packet Length
        self.CC1101_PKTCTRL1 = 0x07        # Packet Automation Control
        self.CC1101_PKTCTRL0 = 0x08        # Packet Automation Control
        self.CC1101_ADDR     = 0x09        # Device Address
        self.CC1101_CHANNR   = 0x0A        # Channel Number
        self.CC1101_FSCTRL1  = 0x0B        # Frequency Synthesizer Control
        self.CC1101_FSCTRL0  = 0x0C        # Frequency Synthesizer Control
        self.CC1101_FREQ2    = 0x0D        # Frequency Control Word, High Byte
        self.CC1101_FREQ1    = 0x0E        # Frequency Control Word, Middle Byte
        self.CC1101_FREQ0    = 0x0F        # Frequency Control Word, Low Byte
        self.CC1101_MDMCFG4  = 0x10        # Modem Configuration
        self.CC1101_MDMCFG3  = 0x11        # Modem Configuration
        self.CC1101_MDMCFG2  = 0x12        # Modem Configuration
        self.CC1101_MDMCFG1  = 0x13        # Modem Configuration
        self.CC1101_MDMCFG0  = 0x14        # Modem Configuration
        self.CC1101_DEVIATN  = 0x15        # Modem Deviation Setting
        self.CC1101_MCSM2    = 0x16        # Main Radio Control State Machine Configuration
        self.CC1101_MCSM1    = 0x17        # Main Radio Control State Machine Configuration
        self.CC1101_MCSM0    = 0x18        # Main Radio Control State Machine Configuration
        self.CC1101_FOCCFG   = 0x19        # Frequency Offset Compensation Configuration
        self.CC1101_BSCFG    = 0x1A        # Bit Synchronization Configuration
        self.CC1101_AGCCTRL2 = 0x1B        # AGC Control
        self.CC1101_AGCCTRL1 = 0x1C        # AGC Control
        self.CC1101_AGCCTRL0 = 0x1D        # AGC Control
        self.CC1101_WOREVT1  = 0x1E        # High Byte Event0 Timeout
        self.CC1101_WOREVT0  = 0x1F        # Low Byte Event0 Timeout
        self.CC1101_WORCTRL  = 0x20        # Wake On Radio Control
        self.CC1101_FREND1   = 0x21        # Front End RX Configuration
        self.CC1101_FREND0   = 0x22        # Front End TX Configuration
        self.CC1101_FSCAL3   = 0x23        # Frequency Synthesizer Calibration
        self.CC1101_FSCAL2   = 0x24        # Frequency Synthesizer Calibration
        self.CC1101_FSCAL1   = 0x25        # Frequency Synthesizer Calibration
        self.CC1101_FSCAL0   = 0x26        # Frequency Synthesizer Calibration
        self.CC1101_RCCTRL1  = 0x27        # RC Oscillator Configuration
        self.CC1101_RCCTRL0  = 0x28        # RC Oscillator Configuration
        self.CC1101_FSTEST   = 0x29        # Frequency Synthesizer Calibration Control
        self.CC1101_PTEST    = 0x2A        # Production Test
        self.CC1101_AGCTEST  = 0x2B        # AGC Test
        self.CC1101_TEST2    = 0x2C        # Various Test Settings
        self.CC1101_TEST1    = 0x2D        # Various Test Settings
        self.CC1101_TEST0    = 0x2E        # Various Test Settings

        # CC1101 Status Registers.
        self.CC1101_PARTNUM        = 0x30  # Chip ID
        self.CC1101_VERSION        = 0x31  # Chip ID
        self.CC1101_FREQEST        = 0x32  # Frequency Offset Estimate from Demodulator
        self.CC1101_LQI            = 0x33  # Demodulator Estimate for Link Quality
        self.CC1101_RSSI           = 0x34  # Received Signal Strength Indication
        self.CC1101_MARCSTATE      = 0x35  # Main Radio Control State Machine State
        self.CC1101_WORTIME1       = 0x36  # High Byte of WOR Time
        self.CC1101_WORTIME0       = 0x37  # Low Byte of WOR Time
        self.CC1101_PKTSTATUS      = 0x38  # Current GDOx Status and Packet Status
        self.CC1101_VCO_VC_DAC     = 0x39  # Current Setting from PLL Calibration Module
        self.CC1101_TXBYTES        = 0x3A  # Underflow and Number of Bytes
        self.CC1101_RXBYTES        = 0x3B  # Overflow and Number of Bytes
        self.CC1101_RCCTRL1_STATUS = 0x3C  # Last RC Oscillator Calibration Result
        self.CC1101_RCCTRL0_STATUS = 0x3D  # Last RC Oscillator Calibration Result

        # CC1101 PA Table, TX FIFO and RX FIFO.
        self.CC1101_PATABLE = 0x3E   # PA TABLE address
        self.CC1101_TXFIFO  = 0x3F   # TX FIFO address
        self.CC1101_RXFIFO  = 0x3F   # RX FIFO address

        # CC1101 Command Strobes.
        self.CC1101_SRES    = 0x30   # Reset CC1101 chip
        self.CC1101_SFSTXON = 0x31   # Enable and calibrate frequency synthesizer (if MCSM0.FS_AUTOCAL = 1). If in RX (with CCA):
        #  Go to a wait state where only the synthesizer is running (for quick RX / TX turnaround).
        self.CC1101_SXOFF   = 0x32   # Turn off crystal oscillator
        self.CC1101_SCAL    = 0x33   # Calibrate frequency synthesizer and turn it off. SCAL can be strobed from IDLE mode without
        #  setting manual calibration mode (MCSM0.FS_AUTOCAL = 0)
        self.CC1101_SRX     = 0x34   # Enable RX. Perform calibration first if coming from IDLE and MCSM0.FS_AUTOCAL = 1
        self.CC1101_STX     = 0x35   # In IDLE state: Enable TX. Perform calibration first if MCSM0.FS_AUTOCAL = 1.
        #  If in RX state and CCA is enabled: Only go to TX if channel is clear
        self.CC1101_SIDLE   = 0x36   # Exit RX / TX, turn off frequency synthesizer and exit Wake-On-Radio mode if applicable
        self.CC1101_SWOR    = 0x38   # Start automatic RX polling sequence (Wake-on-Radio) if WORCTRL.RC_PD = 0
        self.CC1101_SPWD    = 0x39   # Enter power down mode when CSn goes high
        self.CC1101_SFRX    = 0x3A   # Flush the RX FIFO buffer. Only issue SFRX in IDLE or RXFIFO_OVERFLOW states
        self.CC1101_SFTX    = 0x3B   # Flush the TX FIFO buffer. Only issue SFTX in IDLE or TXFIFO_UNDERFLOW states
        self.CC1101_SWORRST = 0x3C   # Reset real time clock to Event1 value
        self.CC1101_SNOP    = 0x3D   # No operation. May be used to get access to the chip status byte

        # CC1101 Transfer Types.
        self.WRITE_BURST = 0x40
        self.READ_SINGLE = 0x80
        self.READ_BURST  = 0xC0

        # CC1101 Returned Status Bytes.
        self.CC1101_STATE_IDLE         = 0x01
        self.CC1101_STATE_ENDCAL       = 0x0C
        self.CC1101_STATE_RX           = 0x0D
        self.CC1101_STATE_RXFIFO_ERROR = 0x11
        self.CC1101_STATE_TX           = 0x13
        self.CC1101_STATE_TX_END       = 0x14
        self.CC1101_STATE_TXFIFO_ERROR = 0x16
        self.reset()
        self.setRegisters()
        for i in range(0, 5):
            self.freqComp[i] = self.DAVIS_FSCTRL0

    def readRegister(self, regAddr):
        addr = regAddr | self.READ_SINGLE
        ss.off()
        read_addr = bytes([addr])
        self.hspi.write(read_addr)
        val = self.hspi.read(1, 0x00)
        ss.on()
        return int(val[0])

    def writeRegister(self, regAddr, value):
        ss.off()
        self.hspi.write(bytes([regAddr]))
        self.hspi.write(bytes([value]))
        ss.on()

    def writeBurst(self, regAddr, wr_buffer):
        addr = regAddr | self.WRITE_BURST
        ss.off()
        self.hspi.write(bytes([addr]))
        for contents in wr_buffer:
            self.hspi.write(bytes([contents]))
        ss.on()

    def readBurst(self, regAddr, size):
        addr = regAddr | self.READ_BURST
        ss.off()
        self.hspi.write(bytes([addr]))
        rd_buffer = []
        for i in range(0, size):
            rd_result = self.hspi.read(1, 0x00)
            rd_buffer.append(hex(rd_result[0]))
        ss.on()
        return rd_buffer

    def cmdStrobe(self, command):
        ss.off()
        self.hspi.write(bytes([command]))
        ss.on()

    def readStatus(self, regAddr):
        addr = regAddr | self.READ_BURST
        ss.off()
        self.hspi.write(bytes([addr]))
        value = self.hspi.read(1, 0x00)
        ss.on()
        return int(value[0])

    def reset(self):
        ss.off()
        utime.sleep_ms(1)
        ss.on()
        utime.sleep_ms(1)
        ss.off()
        while so.value():
            pass
        self.hspi.write(bytes([self.CC1101_SRES]))
        while so.value():
            pass
        ss.on()

    def sidle(self):
        self.cmdStrobe(self.CC1101_SIDLE)
        while self.readStatus(self.CC1101_MARCSTATE) != 0x01:
            utime.sleep_us(100)
        self.cmdStrobe(self.CC1101_SFTX)
        self.cmdStrobe(self.CC1101_SFRX)
        utime.sleep_us(100)

    def setRegisters(self):
        self.writeRegister(self.CC1101_IOCFG2,    self.DAVIS_IOCFG2)
        self.writeRegister(self.CC1101_IOCFG1,    self.DAVIS_IOCFG1)
        self.writeRegister(self.CC1101_IOCFG0,    self.DAVIS_IOCFG0)
        self.writeRegister(self.CC1101_FIFOTHR,   self.DAVIS_FIFOTHR)
        self.writeRegister(self.CC1101_SYNC1,     self.DAVIS_SYNC1)
        self.writeRegister(self.CC1101_SYNC0,     self.DAVIS_SYNC0)
        self.writeRegister(self.CC1101_PKTLEN,    self.DAVIS_PKTLEN)
        self.writeRegister(self.CC1101_PKTCTRL1,  self.DAVIS_PKTCTRL1)
        self.writeRegister(self.CC1101_PKTCTRL0,  self.DAVIS_PKTCTRL0)
        self.writeRegister(self.CC1101_ADDR,      self.DAVIS_ADDR)
        self.writeRegister(self.CC1101_CHANNR,    self.DAVIS_CHANNR)
        self.writeRegister(self.CC1101_FSCTRL1,   self.DAVIS_FSCTRL1)
        self.writeRegister(self.CC1101_FSCTRL0,   self.DAVIS_FSCTRL0)
        self.writeRegister(self.CC1101_FREQ2,     self.DAVIS_FREQ2)
        self.writeRegister(self.CC1101_FREQ1,     self.DAVIS_FREQ1)
        self.writeRegister(self.CC1101_FREQ0,     self.DAVIS_FREQ0)
        self.writeRegister(self.CC1101_MDMCFG4,   self.DAVIS_MDMCFG4)
        self.writeRegister(self.CC1101_MDMCFG3,   self.DAVIS_MDMCFG3)
        self.writeRegister(self.CC1101_MDMCFG2,   self.DAVIS_MDMCFG2)
        self.writeRegister(self.CC1101_MDMCFG1,   self.DAVIS_MDMCFG1)
        self.writeRegister(self.CC1101_MDMCFG0,   self.DAVIS_MDMCFG0)
        self.writeRegister(self.CC1101_DEVIATN,   self.DAVIS_DEVIATN)
        self.writeRegister(self.CC1101_MCSM2,     self.DAVIS_MCSM2)
        self.writeRegister(self.CC1101_MCSM1,     self.DAVIS_MCSM1)
        self.writeRegister(self.CC1101_MCSM0,     self.DAVIS_MCSM0)
        self.writeRegister(self.CC1101_FOCCFG,    self.DAVIS_FOCCFG)
        self.writeRegister(self.CC1101_BSCFG,     self.DAVIS_BSCFG)
        self.writeRegister(self.CC1101_AGCCTRL2,  self.DAVIS_AGCCTRL2)
        self.writeRegister(self.CC1101_AGCCTRL1,  self.DAVIS_AGCCTRL1)
        self.writeRegister(self.CC1101_AGCCTRL0,  self.DAVIS_AGCCTRL0)
        self.writeRegister(self.CC1101_WOREVT1,   self.DAVIS_WOREVT1)
        self.writeRegister(self.CC1101_WOREVT0,   self.DAVIS_WOREVT0)
        self.writeRegister(self.CC1101_WORCTRL,   self.DAVIS_WORCTRL)
        self.writeRegister(self.CC1101_FREND1,    self.DAVIS_FREND1)
        self.writeRegister(self.CC1101_FREND0,    self.DAVIS_FREND0)
        self.writeRegister(self.CC1101_FSCAL3,    self.DAVIS_FSCAL3)
        self.writeRegister(self.CC1101_FSCAL2,    self.DAVIS_FSCAL2)
        self.writeRegister(self.CC1101_FSCAL1,    self.DAVIS_FSCAL1)
        self.writeRegister(self.CC1101_FSCAL0,    self.DAVIS_FSCAL0)
        self.writeRegister(self.CC1101_RCCTRL1,   self.DAVIS_RCCTRL1)
        self.writeRegister(self.CC1101_RCCTRL0,   self.DAVIS_RCCTRL0)
        self.writeRegister(self.CC1101_FSTEST,    self.DAVIS_FSTEST)
        self.writeRegister(self.CC1101_PTEST,     self.DAVIS_PTEST)
        self.writeRegister(self.CC1101_AGCTEST,   self.DAVIS_AGCTEST)
        self.writeRegister(self.CC1101_TEST2,     self.DAVIS_TEST2)
        self.writeRegister(self.CC1101_TEST1,     self.DAVIS_TEST1)
        self.writeRegister(self.CC1101_TEST0,     self.DAVIS_TEST0)
        self.writeBurst(self.CC1101_PATABLE,      self.PA_TABLE)
        self.setFrequency(self.hopIndex)

    def flush(self):
        self.sidle()
        self.cmdStrobe(self.CC1101_SFRX)  # Flush Rx FIFO
        self.cmdStrobe(self.CC1101_SFTX)  # Flush Tx FIFO
        self.rxBuffer = [0x00] * self.BUFFER_SIZE
        self.rxBufferLength = self.rxBufferIndex = 0

    def rx(self):
        self.cmdStrobe(self.CC1101_SRX)
        while (self.readStatus(self.CC1101_MARCSTATE) & 0x1F) != self.CC1101_STATE_RX:
            utime.sleep_us(900)
        self.rxing = 1
        self.writeRegister(self.CC1101_IOCFG0, self.DAVIS_IOCFG0)

    def hop(self):
        self.hopIndex += 1                      # Increment the index
        if (self.hopIndex > 4):                 # 5 EU frequencies
            self.hopIndex = 0
        present = self.readRegister(self.CC1101_FSCTRL0)
        # DEBUG print("Present value: {}, WRITING {} TO CC1101_FSCTRL0 / {}".format(present, self.freqComp[self.hopIndex], self.CC1101_FSCTRL0))
        self.writeRegister(self.CC1101_FSCTRL0, self.freqComp[self.hopIndex])
        self.setFrequency(self.hopIndex)             # Set the frequency.

    def setFrequency(self, index):
        self.sidle()
        self.writeRegister(self.CC1101_FREQ2, self.FREQ_2[index])
        self.writeRegister(self.CC1101_FREQ1, self.FREQ_1[index])
        self.writeRegister(self.CC1101_FREQ0, self.FREQ_0[index])
        self.flush()

    def calcCrc(self, _buffer):
        crc = 0x0000
        for i in range(0, len(_buffer)):
            crc = ((crc << 8) ^ self.CRC_TABLE[(crc >> 8) ^ (_buffer[i])]) % 65536
            # DEBUG print("CRC: {}".format(crc))
        return crc

    def readRssi(self):
        rssi = self.readRegister(self.CC1101_RXFIFO)
        if rssi >= 128:
            return (rssi - 256)/2 - 74
        elif rssi < 128:
            return rssi/2 -74
        else:
            return False

    def readLQI(self):
        return self.readRegister(self.CC1101_RXFIFO) & 0x7F

    def calcFreqError(self, value):
        if value >= 128:
            error = (value - 256) >> 1
        else:
            error = value >> 1
        return error
