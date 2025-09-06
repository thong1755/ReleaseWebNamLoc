from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
from datetime import date
from decimal import Decimal

# User model
class UserResponse(BaseModel):
    iduser: str
    ten: Optional[str] = None
    password: Optional[str] = None
    
    class Config:
        from_attributes = True

# Login request/response schemas
class LoginRequest(BaseModel):
    iduser: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    user_info: Optional[UserResponse] = None
    
# Change password request/response schemas
class ChangePasswordRequest(BaseModel):
    iduser: str
    current_password: str
    new_password: str

class ChangePasswordResponse(BaseModel):
    success: bool
    message: str

# Realtime data schemas
class RealtimeDataRequest(BaseModel):
    WeightValue: str
    StatusCam1: str
    StatusCam2: str
    StatusCam3: str

class RealtimeDataResponse(BaseModel):
    WeightValue: str
    StatusCam1: str
    StatusCam2: str
    StatusCam3: str
    timestamp: str

class RealtimeUpdateResponse(BaseModel):
    success: bool
    message: str

# Camera Schemas
class CameraResponse(BaseModel):
    ID: Optional[int] = None
    IPAddrees: Optional[str] = None
    UseName: Optional[str] = None
    Password: Optional[str] = None
    Port: Optional[str] = None
    Active: Optional[int] = None
    SubStream: Optional[int] = None
    Caching: Optional[str] = None

    class Config:
        from_attributes = True

# Picture Management Schemas
class PictureUploadRequest(BaseModel):
    ticket_number: str  # Số phiếu
    picture_type: str   # NK, CT, NT, XK
    camera_number: int  # 1, 2, 3...
    sequence: int       # 1, 2, 3... (lần chụp thứ mấy)
    date: Optional[str] = None  # YYYY-MM-DD format, nếu không có sẽ dùng ngày hiện tại

class PictureUploadResponse(BaseModel):
    success: bool
    message: str
    file_path: Optional[str] = None
    folder_created: bool = False

class PictureListRequest(BaseModel):
    ticket_number: Optional[str] = None
    picture_type: Optional[str] = None  # NK, CT, NT, XK
    date: Optional[str] = None  # YYYY-MM-DD format
    camera_number: Optional[int] = None

class PictureInfo(BaseModel):
    filename: str
    file_path: str
    image_url: str              # URL để xem/tải hình ảnh trực tiếp
    ticket_number: str
    picture_type: str
    camera_number: int
    sequence: int
    date: str
    file_size: int
    created_time: str

class PictureListResponse(BaseModel):
    success: bool
    message: str
    pictures: List[PictureInfo] = []

# Nhapkho response schema
class NhapkhoResponse(BaseModel):
    sophieu: int                                    # Ticket number
    ngaycan: Optional[date] = None                  # Weighing date
    msp: Optional[str] = None                       # Code (NK, etc.)
    bienso1_1: Optional[str] = None                 # License plate 1
    bienso1_2: Optional[str] = None                 # License plate 2
    bienso2_1: Optional[str] = None                 # License plate 3
    bienso2_2: Optional[str] = None                 # License plate 4
    khachhang: Optional[str] = None                 # Customer name
    loaihang: Optional[str] = None                  # Goods name
    laixe: Optional[str] = None                     # Driver name
    nguoican: Optional[str] = None                  # Weigher name
    khoiluonglan1: Optional[Decimal] = None         # First weighing value
    khoiluonglan2: Optional[Decimal] = None         # Second weighing value
    khoiluongtinh: Optional[Decimal] = None         # Net weight
    khoiluongtru: Optional[Decimal] = None          # Deducted weight
    phantramKCL: Optional[Decimal] = None           # Deducted percent
    khoiluongthanhtoan: Optional[Decimal] = None    # Payable weight
    dongia: Optional[Decimal] = None                # Unit price
    thanhtien: Optional[Decimal] = None             # Total payment
    thoigiancanlan1: Optional[str] = None           # Time of first weighing
    thoigiancanlan2: Optional[str] = None           # Time of second weighing
    ghichu: Optional[str] = None                    # Note
    chungtu: Optional[str] = None                   # Document/Customer address
    lancan: Optional[int] = None                    # Weighing count (1 or 2)
    lanin: Optional[int] = None                     # Print count
    xoaphieu: Optional[int] = None                  # Deleted flag (0: active, 1: deleted)
    
    class Config:
        from_attributes = True

# Xuatkho response schema
class XuatkhoResponse(BaseModel):
    sophieu: int                                    # Ticket number
    ngaycan: Optional[date] = None                  # Weighing date
    msp: Optional[str] = None                       # Code (NK, etc.)
    bienso1_1: Optional[str] = None                 # License plate 1
    bienso1_2: Optional[str] = None                 # License plate 2
    bienso2_1: Optional[str] = None                 # License plate 3
    bienso2_2: Optional[str] = None                 # License plate 4
    khachhang: Optional[str] = None                 # Customer name
    loaihang: Optional[str] = None                  # Goods name
    laixe: Optional[str] = None                     # Driver name
    nguoican: Optional[str] = None                  # Weigher name
    khoiluonglan1: Optional[Decimal] = None         # First weighing value
    khoiluonglan2: Optional[Decimal] = None         # Second weighing value
    khoiluongtinh: Optional[Decimal] = None         # Net weight
    khoiluongtru: Optional[Decimal] = None          # Deducted weight
    phantramKCL: Optional[Decimal] = None           # Deducted percent
    khoiluongthanhtoan: Optional[Decimal] = None    # Payable weight
    dongia: Optional[Decimal] = None                # Unit price
    thanhtien: Optional[Decimal] = None             # Total payment
    thoigiancanlan1: Optional[str] = None           # Time of first weighing
    thoigiancanlan2: Optional[str] = None           # Time of second weighing
    ghichu: Optional[str] = None                    # Note
    chungtu: Optional[str] = None                   # Document/Customer address
    lancan: Optional[int] = None                    # Weighing count (1 or 2)
    lanin: Optional[int] = None                     # Print count
    xoaphieu: Optional[int] = None                  # Deleted flag (0: active, 1: deleted)
    
    class Config:
        from_attributes = True

# Canthue response schema
class CanthueResponse(BaseModel):
    sophieu: int                                    # Ticket number
    ngaycan: Optional[date] = None                  # Weighing date
    msp: Optional[str] = None                       # Code (NK, etc.)
    bienso1_1: Optional[str] = None                 # License plate 1
    bienso1_2: Optional[str] = None                 # License plate 2
    bienso2_1: Optional[str] = None                 # License plate 3
    bienso2_2: Optional[str] = None                 # License plate 4
    khachhang: Optional[str] = None                 # Customer name
    loaihang: Optional[str] = None                  # Goods name
    laixe: Optional[str] = None                     # Driver name
    nguoican: Optional[str] = None                  # Weigher name
    khoiluonglan1: Optional[Decimal] = None         # First weighing value
    khoiluonglan2: Optional[Decimal] = None         # Second weighing value
    khoiluongtinh: Optional[Decimal] = None         # Net weight
    khoiluongtru: Optional[Decimal] = None          # Deducted weight
    phantramKCL: Optional[Decimal] = None           # Deducted percent
    khoiluongthanhtoan: Optional[Decimal] = None    # Payable weight
    dongia: Optional[Decimal] = None                # Unit price
    thanhtien: Optional[Decimal] = None             # Total payment
    thoigiancanlan1: Optional[str] = None           # Time of first weighing
    thoigiancanlan2: Optional[str] = None           # Time of second weighing
    ghichu: Optional[str] = None                    # Note
    chungtu: Optional[str] = None                   # Document/Customer address
    lancan: Optional[int] = None                    # Weighing count (1 or 2)
    lanin: Optional[int] = None                     # Print count
    xoaphieu: Optional[int] = None                  # Deleted flag (0: active, 1: deleted)
    
    class Config:
        from_attributes = True

# Nhaptau response schema
class NhaptauResponse(BaseModel):
    sophieu: int                                    # Ticket number
    ngaycan: Optional[date] = None                  # Weighing date
    msp: Optional[str] = None                       # Code (NK, etc.)
    bienso1_1: Optional[str] = None                 # License plate 1
    bienso1_2: Optional[str] = None                 # License plate 2
    bienso2_1: Optional[str] = None                 # License plate 3
    bienso2_2: Optional[str] = None                 # License plate 4
    khachhang: Optional[str] = None                 # Customer name
    loaihang: Optional[str] = None                  # Goods name
    laixe: Optional[str] = None                     # Driver name
    nguoican: Optional[str] = None                  # Weigher name
    khoiluonglan1: Optional[Decimal] = None         # First weighing value
    khoiluonglan2: Optional[Decimal] = None         # Second weighing value
    khoiluongtinh: Optional[Decimal] = None         # Net weight
    khoiluongtru: Optional[Decimal] = None          # Deducted weight
    phantramKCL: Optional[Decimal] = None           # Deducted percent
    khoiluongthanhtoan: Optional[Decimal] = None    # Payable weight
    dongia: Optional[Decimal] = None                # Unit price
    thanhtien: Optional[Decimal] = None             # Total payment
    thoigiancanlan1: Optional[str] = None           # Time of first weighing
    thoigiancanlan2: Optional[str] = None           # Time of second weighing
    ghichu: Optional[str] = None                    # Note
    chungtu: Optional[str] = None                   # Document/Customer address
    lancan: Optional[int] = None                    # Weighing count (1 or 2)
    lanin: Optional[int] = None                     # Print count
    xoaphieu: Optional[int] = None                  # Deleted flag (0: active, 1: deleted)
    
    class Config:
        from_attributes = True
        
# LogisticsDataResponse schema for the combined API endpoint
class LogisticsDataResponse(BaseModel):
    nhapkho: List[NhapkhoResponse] = []
    xuatkho: List[XuatkhoResponse] = []
    canthue: List[CanthueResponse] = []
    nhaptau: List[NhaptauResponse] = []
    total_count: Dict[str, int] = {}

# Loaihang response schema
class LoaihangResponse(BaseModel):
    mahang: str                           # Product/Goods code
    tenhang: Optional[str] = None         # Product/Goods name
    tykhoi: Optional[Decimal] = None      # Volume ratio
    dongia: Optional[Decimal] = None      # Unit price
    
    class Config:
        from_attributes = True

# Khachhang response schema
class KhachhangResponse(BaseModel):
    ID: int                                   # ID
    makhachhang: Optional[str] = None         # Customer code
    tenkhachhang: Optional[str] = None        # Customer name
    diachikhachhang: Optional[str] = None     # Customer address
    ghichukhachhang: Optional[str] = None     # Customer note
    loaihang: Optional[str] = None            # Product/Goods type
    
    class Config:
        from_attributes = True

# Xe response schema
class XeResponse(BaseModel):
    ID: int                                   # ID
    masoxe_xe: Optional[str] = None           # Vehicle code
    blenso_xe: Optional[str] = None           # License plate
    tenkhachhang_xe: Optional[str] = None     # Customer name
    diachixe_xe: Optional[str] = None         # Address
    loaihang_xe: Optional[str] = None         # Product/Goods type
    laixe_xe: Optional[str] = None            # Driver name
    ghichu_xe: Optional[str] = None           # Note
    
    class Config:
        from_attributes = True
