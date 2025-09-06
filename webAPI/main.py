from fastapi import FastAPI, HTTPException, Depends, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import text, Column
from typing import List, Dict, Optional, Union
import uvicorn
from datetime import datetime
import os
import pathlib
from dotenv import load_dotenv
import re
import mimetypes
from io import BytesIO

# Load environment variables
load_dotenv()

from database import get_db, create_tables, User as DBUser, Nhapkho, Xuatkho, Canthue, Nhaptau, Loaihang, Khachhang, Xe, Camera
from schemas import (
    UserResponse, NhapkhoResponse, NhaptauResponse, XuatkhoResponse, 
    CanthueResponse, LoaihangResponse, KhachhangResponse, XeResponse, CameraResponse,
    RealtimeDataRequest, RealtimeDataResponse, RealtimeUpdateResponse,
    PictureUploadRequest, PictureUploadResponse, PictureListRequest, 
    PictureListResponse, PictureInfo
)

# Biến toàn cục để lưu trữ dữ liệu realtime
realtime_data = {
    "WeightValue": "0.00",
    "StatusCam1": "Offline",
    "StatusCam2": "Offline", 
    "StatusCam3": "Offline",
    "timestamp": datetime.now().isoformat()
}

# Hàm tiện ích để tạo điều kiện lọc tiếng Việt
def vietnamese_filter(column: Column, value: str):
    """
    Tạo điều kiện lọc hỗ trợ tiếng Việt không phân biệt hoa thường và dấu
    """
    if not value:
        return None
    collate_clause = f"N'%{value}%'"
    return text(f"{column.key} LIKE {collate_clause} COLLATE Vietnamese_CI_AI")
from schemas import (
    LoginRequest, LoginResponse, UserResponse, 
    ChangePasswordRequest, ChangePasswordResponse,
    RealtimeDataRequest, RealtimeDataResponse, RealtimeUpdateResponse,
    NhapkhoResponse, XuatkhoResponse, CanthueResponse, NhaptauResponse, 
    LogisticsDataResponse, LoaihangResponse, KhachhangResponse, XeResponse
)

# Tạo ứng dụng FastAPI
app = FastAPI(
    title="NamLoc Web API",
    description="Web API với chức năng đăng nhập",
    version="1.0.0"
)


# Tạo bảng khi khởi động
create_tables()

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Thay bằng domain cụ thể nếu cần bảo mật hơn
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for Flutter webAPP
from fastapi.staticfiles import StaticFiles
import pathlib

webapp_path = pathlib.Path(__file__).parent.parent / "webAPP"
app.mount("/webapp", StaticFiles(directory=str(webapp_path), html=True), name="webapp")


# API login - DUY NHẤT ĐƯỢC GIỮ LẠI
@app.post("/auth/login", response_model=LoginResponse)
async def login_user(login_data: LoginRequest, db: Session = Depends(get_db)):
    """API đăng nhập user"""
    try:
        # Tìm user theo iduser
        user = db.query(DBUser).filter(DBUser.iduser == login_data.iduser).first()
        
        if user is None:
            return LoginResponse(
                success=False,
                message="Không tìm thấy người dùng",
                user_info=None
            )
        
        # Kiểm tra password (trong thực tế nên hash password)
        if user.password != login_data.password:
            return LoginResponse(
                success=False,
                message="Mật khẩu không đúng",
                user_info=None
            )
        
        # Đăng nhập thành công
        return LoginResponse(
            success=True,
            message="Đăng nhập thành công",
            user_info=UserResponse(
                iduser=user.iduser,
                ten=user.ten,
                password=None  # Không trả về password khi đăng nhập thành công
            )
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi đăng nhập: {str(e)}")

# API đổi mật khẩu
@app.post("/auth/change-password", response_model=ChangePasswordResponse)
async def change_password(change_data: ChangePasswordRequest, db: Session = Depends(get_db)):
    """API đổi mật khẩu cho user"""
    try:
        # Tìm user theo iduser
        user = db.query(DBUser).filter(DBUser.iduser == change_data.iduser).first()
        
        if user is None:
            return ChangePasswordResponse(
                success=False,
                message="Không tìm thấy người dùng"
            )
        
        # Kiểm tra mật khẩu hiện tại
        if user.password != change_data.current_password:
            return ChangePasswordResponse(
                success=False,
                message="Mật khẩu hiện tại không đúng"
            )
        
        # Cập nhật mật khẩu mới
        user.password = change_data.new_password
        db.commit()
        
        # Trả về kết quả thành công
        return ChangePasswordResponse(
            success=True,
            message="Đổi mật khẩu thành công"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi đổi mật khẩu: {str(e)}")

# API nhận dữ liệu realtime từ VB App
@app.post("/realtime/update", response_model=RealtimeUpdateResponse)
async def update_realtime_data(data: RealtimeDataRequest):
    """API để VB App gửi dữ liệu realtime lên server"""
    global realtime_data
    try:
        # Cập nhật dữ liệu realtime
        current_time = datetime.now().isoformat()
        realtime_data = {
            "WeightValue": data.WeightValue,
            "StatusCam1": data.StatusCam1,
            "StatusCam2": data.StatusCam2,
            "StatusCam3": data.StatusCam3,
            "timestamp": current_time
        }
        
        return RealtimeUpdateResponse(
            success=True,
            message="Cập nhật dữ liệu thành công",
            timestamp=current_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi cập nhật dữ liệu realtime: {str(e)}")

# API lấy dữ liệu realtime cho Mobile App
@app.get("/realtime/data", response_model=RealtimeDataResponse)
async def get_realtime_data():
    """API để Mobile App lấy dữ liệu realtime từ server"""
    global realtime_data
    try:
        return RealtimeDataResponse(
            WeightValue=realtime_data["WeightValue"],
            StatusCam1=realtime_data["StatusCam1"],
            StatusCam2=realtime_data["StatusCam2"],
            StatusCam3=realtime_data["StatusCam3"],
            timestamp=realtime_data["timestamp"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy dữ liệu realtime: {str(e)}")

# API để get dữ liệu từ table nhapkho với điều kiện lọc theo ngày
@app.get("/nhapkho", response_model=List[NhapkhoResponse])
async def get_nhapkho(
    db: Session = Depends(get_db),
    tu_ngay: str = None,     # Từ ngày (format: YYYY-MM-DD)
    den_ngay: str = None,    # Đến ngày (format: YYYY-MM-DD)
    khachhang: str = None,   # Lọc theo tên khách hàng
    sophieu: str = None,     # Lọc theo số phiếu
    bienso: str = None,      # Lọc theo biển số xe
    loaihang: str = None,    # Lọc theo loại hàng
    limit: int = None,       # Giới hạn số records trả về
    offset: int = 0          # Vị trí bắt đầu lấy dữ liệu
):
    """
    Lấy dữ liệu từ bảng nhapkho với các điều kiện lọc
    
    Parameters:
    - tu_ngay: Từ ngày (YYYY-MM-DD), ví dụ: 2024-01-01
    - den_ngay: Đến ngày (YYYY-MM-DD), ví dụ: 2024-01-31
    - khachhang: Tìm theo tên khách hàng (contains)
    - sophieu: Tìm theo số phiếu (contains)
    - bienso: Tìm theo biển số xe (contains)
    - loaihang: Tìm theo loại hàng (contains)
    - limit: Giới hạn số lượng records trả về
    
    Examples:
    - /nhapkho?tu_ngay=2024-01-01&den_ngay=2024-01-31
    - /nhapkho?tu_ngay=2024-01-15
    - /nhapkho?khachhang=CÔNG TY ABC
    - /nhapkho?tu_ngay=2024-01-01&den_ngay=2024-01-31&khachhang=ABC&bienso=51D&loaihang=Gạo&limit=10
    """
    try:
        # Bắt đầu với query cơ bản
        query = db.query(Nhapkho)
        
        # Lọc theo khoảng thời gian
        if tu_ngay:
            query = query.filter(Nhapkho.ngaycan >= tu_ngay)
        
        if den_ngay:
            query = query.filter(Nhapkho.ngaycan <= den_ngay)
            
        # Lọc theo khách hàng (hỗ trợ tiếng Việt đầy đủ)
        if khachhang:
            query = query.filter(vietnamese_filter(Nhapkho.khachhang, khachhang))
            
        # Lọc theo số phiếu
        if sophieu:
            query = query.filter(Nhapkho.sophieu.contains(sophieu))
            
        # Lọc theo biển số xe (chỉ kiểm tra trường bienso1_1)
        if bienso:
            query = query.filter(vietnamese_filter(Nhapkho.bienso1_1, bienso))
            
        # Lọc theo loại hàng (hỗ trợ tiếng Việt đầy đủ)
        if loaihang:
            query = query.filter(vietnamese_filter(Nhapkho.loaihang, loaihang))
        
        # Sắp xếp theo ngày cân (mới nhất trước)
        query = query.order_by(Nhapkho.ngaycan.desc())
        
        # Thêm offset để bỏ qua một số lượng bản ghi từ đầu
        if offset and offset > 0:
            query = query.offset(offset)
            
        # Giới hạn số lượng nếu có
        if limit and limit > 0:
            query = query.limit(limit)
            
        # Thực hiện query
        results = query.all()
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy dữ liệu nhapkho: {str(e)}")

# API để get dữ liệu từ table xuatkho với điều kiện lọc theo ngày
@app.get("/xuatkho", response_model=List[XuatkhoResponse])
async def get_xuatkho(
    db: Session = Depends(get_db),
    tu_ngay: str = None,     # Từ ngày (format: YYYY-MM-DD)
    den_ngay: str = None,    # Đến ngày (format: YYYY-MM-DD)
    khachhang: str = None,   # Lọc theo tên khách hàng
    sophieu: str = None,     # Lọc theo số phiếu
    bienso: str = None,      # Lọc theo biển số xe
    loaihang: str = None,    # Lọc theo loại hàng
    limit: int = None,       # Giới hạn số records trả về
    offset: int = 0          # Vị trí bắt đầu lấy dữ liệu
):
    """
    Lấy dữ liệu từ bảng xuatkho với các điều kiện lọc
    
    Parameters:
    - tu_ngay: Từ ngày (YYYY-MM-DD), ví dụ: 2024-01-01
    - den_ngay: Đến ngày (YYYY-MM-DD), ví dụ: 2024-01-31
    - khachhang: Tìm theo tên khách hàng (contains)
    - sophieu: Tìm theo số phiếu (contains)
    - bienso: Tìm theo biển số xe (contains)
    - loaihang: Tìm theo loại hàng (contains)
    - limit: Giới hạn số lượng records trả về
    
    Examples:
    - /xuatkho?tu_ngay=2024-01-01&den_ngay=2024-01-31
    - /xuatkho?tu_ngay=2024-01-15
    - /xuatkho?khachhang=CÔNG TY ABC
    - /xuatkho?tu_ngay=2024-01-01&den_ngay=2024-01-31&khachhang=ABC&bienso=51D&loaihang=Gạo&limit=10
    """
    try:
        # Bắt đầu với query cơ bản
        query = db.query(Xuatkho)
        
        # Lọc theo khoảng thời gian
        if tu_ngay:
            query = query.filter(Xuatkho.ngaycan >= tu_ngay)
        
        if den_ngay:
            query = query.filter(Xuatkho.ngaycan <= den_ngay)
            
        # Lọc theo khách hàng (hỗ trợ tiếng Việt đầy đủ)
        if khachhang:
            query = query.filter(vietnamese_filter(Xuatkho.khachhang, khachhang))
            
        # Lọc theo số phiếu
        if sophieu:
            query = query.filter(Xuatkho.sophieu.contains(sophieu))
            
        # Lọc theo biển số xe (chỉ kiểm tra trường bienso1_1)
        if bienso:
            query = query.filter(vietnamese_filter(Xuatkho.bienso1_1, bienso))
            
        # Lọc theo loại hàng (hỗ trợ tiếng Việt đầy đủ)
        if loaihang:
            query = query.filter(vietnamese_filter(Xuatkho.loaihang, loaihang))
        
        # Sắp xếp theo ngày cân (mới nhất trước)
        query = query.order_by(Xuatkho.ngaycan.desc())
        
        # Thêm offset để bỏ qua một số lượng bản ghi từ đầu
        if offset and offset > 0:
            query = query.offset(offset)
            
        # Giới hạn số lượng nếu có
        if limit and limit > 0:
            query = query.limit(limit)
            
        # Thực hiện query
        results = query.all()
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy dữ liệu xuatkho: {str(e)}")

# API để get dữ liệu từ table canthue với điều kiện lọc theo ngày
@app.get("/canthue", response_model=List[CanthueResponse])
async def get_canthue(
    db: Session = Depends(get_db),
    tu_ngay: str = None,     # Từ ngày (format: YYYY-MM-DD)
    den_ngay: str = None,    # Đến ngày (format: YYYY-MM-DD)
    khachhang: str = None,   # Lọc theo tên khách hàng
    sophieu: str = None,     # Lọc theo số phiếu
    bienso: str = None,      # Lọc theo biển số xe
    loaihang: str = None,    # Lọc theo loại hàng
    limit: int = None,       # Giới hạn số records trả về
    offset: int = 0          # Vị trí bắt đầu lấy dữ liệu
):
    """
    Lấy dữ liệu từ bảng canthue với các điều kiện lọc
    
    Parameters:
    - tu_ngay: Từ ngày (YYYY-MM-DD), ví dụ: 2024-01-01
    - den_ngay: Đến ngày (YYYY-MM-DD), ví dụ: 2024-01-31
    - khachhang: Tìm theo tên khách hàng (contains)
    - sophieu: Tìm theo số phiếu (contains)
    - bienso: Tìm theo biển số xe (contains)
    - loaihang: Tìm theo loại hàng (contains)
    - limit: Giới hạn số lượng records trả về
    
    Examples:
    - /canthue?tu_ngay=2024-01-01&den_ngay=2024-01-31
    - /canthue?tu_ngay=2024-01-15
    - /canthue?khachhang=CÔNG TY ABC
    - /canthue?tu_ngay=2024-01-01&den_ngay=2024-01-31&khachhang=ABC&bienso=51D&loaihang=Gạo&limit=10
    """
    try:
        # Bắt đầu với query cơ bản
        query = db.query(Canthue)
        
        # Lọc theo khoảng thời gian
        if tu_ngay:
            query = query.filter(Canthue.ngaycan >= tu_ngay)
        
        if den_ngay:
            query = query.filter(Canthue.ngaycan <= den_ngay)
            
        # Lọc theo khách hàng (hỗ trợ tiếng Việt đầy đủ)
        if khachhang:
            query = query.filter(vietnamese_filter(Canthue.khachhang, khachhang))
            
        # Lọc theo số phiếu
        if sophieu:
            query = query.filter(Canthue.sophieu.contains(sophieu))
            
        # Lọc theo biển số xe (chỉ kiểm tra trường bienso1_1)
        if bienso:
            query = query.filter(vietnamese_filter(Canthue.bienso1_1, bienso))
            
        # Lọc theo loại hàng (hỗ trợ tiếng Việt đầy đủ)
        if loaihang:
            query = query.filter(vietnamese_filter(Canthue.loaihang, loaihang))
        
        # Sắp xếp theo ngày cân (mới nhất trước)
        query = query.order_by(Canthue.ngaycan.desc())
        
        # Thêm offset để bỏ qua một số lượng bản ghi từ đầu
        if offset and offset > 0:
            query = query.offset(offset)
            
        # Giới hạn số lượng nếu có
        if limit and limit > 0:
            query = query.limit(limit)
            
        # Thực hiện query
        results = query.all()
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy dữ liệu canthue: {str(e)}")

# API để get dữ liệu từ table nhaptau với điều kiện lọc theo ngày
@app.get("/nhaptau", response_model=List[NhaptauResponse])
async def get_nhaptau(
    db: Session = Depends(get_db),
    tu_ngay: str = None,     # Từ ngày (format: YYYY-MM-DD)
    den_ngay: str = None,    # Đến ngày (format: YYYY-MM-DD)
    khachhang: str = None,   # Lọc theo tên khách hàng
    sophieu: str = None,     # Lọc theo số phiếu
    bienso: str = None,      # Lọc theo biển số xe
    loaihang: str = None,    # Lọc theo loại hàng
    limit: int = None,       # Giới hạn số records trả về
    offset: int = 0          # Vị trí bắt đầu lấy dữ liệu
):
    """
    Lấy dữ liệu từ bảng nhaptau với các điều kiện lọc
    
    Parameters:
    - tu_ngay: Từ ngày (YYYY-MM-DD), ví dụ: 2024-01-01
    - den_ngay: Đến ngày (YYYY-MM-DD), ví dụ: 2024-01-31
    - khachhang: Tìm theo tên khách hàng (contains)
    - sophieu: Tìm theo số phiếu (contains)
    - bienso: Tìm theo biển số xe (contains)
    - loaihang: Tìm theo loại hàng (contains)
    - limit: Giới hạn số lượng records trả về
    
    Examples:
    - /nhaptau?tu_ngay=2024-01-01&den_ngay=2024-01-31
    - /nhaptau?tu_ngay=2024-01-15
    - /nhaptau?khachhang=CÔNG TY ABC
    - /nhaptau?tu_ngay=2024-01-01&den_ngay=2024-01-31&khachhang=ABC&bienso=51D&loaihang=Gạo&limit=10
    """
    try:
        # Bắt đầu với query cơ bản
        query = db.query(Nhaptau)
        
        # Lọc theo khoảng thời gian
        if tu_ngay:
            query = query.filter(Nhaptau.ngaycan >= tu_ngay)
        
        if den_ngay:
            query = query.filter(Nhaptau.ngaycan <= den_ngay)
            
        # Lọc theo khách hàng (hỗ trợ tiếng Việt đầy đủ)
        if khachhang:
            query = query.filter(vietnamese_filter(Nhaptau.khachhang, khachhang))
            
        # Lọc theo số phiếu
        if sophieu:
            query = query.filter(Nhaptau.sophieu.contains(sophieu))
            
        # Lọc theo biển số xe (chỉ kiểm tra trường bienso1_1)
        if bienso:
            query = query.filter(vietnamese_filter(Nhaptau.bienso1_1, bienso))
            
        # Lọc theo loại hàng (hỗ trợ tiếng Việt đầy đủ)
        if loaihang:
            query = query.filter(vietnamese_filter(Nhaptau.loaihang, loaihang))
        
        # Sắp xếp theo ngày cân (mới nhất trước)
        query = query.order_by(Nhaptau.ngaycan.desc())
        
        # Thêm offset để bỏ qua một số lượng bản ghi từ đầu
        if offset and offset > 0:
            query = query.offset(offset)
            
        # Giới hạn số lượng nếu có
        if limit and limit > 0:
            query = query.limit(limit)
            
        # Thực hiện query
        results = query.all()
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy dữ liệu nhaptau: {str(e)}")

# API tổng hợp dữ liệu từ 4 bảng: nhapkho, xuatkho, canthue, nhaptau
@app.get("/logistics/all", response_model=LogisticsDataResponse)
async def get_all_logistics_data(
    db: Session = Depends(get_db),
    tu_ngay: str = None,     # Từ ngày (format: YYYY-MM-DD)
    den_ngay: str = None,    # Đến ngày (format: YYYY-MM-DD)
    khachhang: str = None,   # Lọc theo tên khách hàng
    sophieu: str = None,     # Lọc theo số phiếu
    bienso: str = None,      # Lọc theo biển số xe
    loaihang: str = None,    # Lọc theo loại hàng
    limit: int = None,       # Giới hạn số records trả về mỗi bảng
    offset: int = 0,         # Vị trí bắt đầu lấy dữ liệu
    tables: str = None       # Chọn các bảng cụ thể, phân cách bởi dấu phẩy: "nhapkho,xuatkho,canthue,nhaptau"
):
    """
    API tổng hợp dữ liệu từ tất cả 4 bảng: nhapkho, xuatkho, canthue, nhaptau với các điều kiện lọc
    
    Parameters:
    - tu_ngay: Từ ngày (YYYY-MM-DD), ví dụ: 2024-01-01
    - den_ngay: Đến ngày (YYYY-MM-DD), ví dụ: 2024-01-31
    - khachhang: Tìm theo tên khách hàng (contains)
    - sophieu: Tìm theo số phiếu (contains)
    - bienso: Tìm theo biển số xe (contains)
    - loaihang: Tìm theo loại hàng (contains)
    - limit: Giới hạn số lượng records trả về mỗi bảng
    - tables: Chọn các bảng cụ thể, phân cách bởi dấu phẩy: "nhapkho,xuatkho,canthue,nhaptau"
    
    Examples:
    - /logistics/all?tu_ngay=2024-01-01&den_ngay=2024-01-31
    - /logistics/all?tu_ngay=2024-01-15&tables=nhapkho,xuatkho
    - /logistics/all?khachhang=CÔNG TY ABC
    - /logistics/all?tu_ngay=2024-01-01&den_ngay=2024-01-31&khachhang=ABC&bienso=51D&loaihang=Gạo&limit=10
    """
    try:
        result = LogisticsDataResponse(
            nhapkho=[],
            xuatkho=[],
            canthue=[],
            nhaptau=[],
            total_count={}
        )
        
        # Xác định các bảng cần lấy dữ liệu
        selected_tables = []
        if tables:
            selected_tables = [table.strip().lower() for table in tables.split(",")]
        else:
            selected_tables = ["nhapkho", "xuatkho", "canthue", "nhaptau"]
        
        # Lấy dữ liệu từ bảng nhapkho
        if "nhapkho" in selected_tables:
            nhapkho_query = db.query(Nhapkho)
            
            # Áp dụng các điều kiện lọc
            if tu_ngay:
                nhapkho_query = nhapkho_query.filter(Nhapkho.ngaycan >= tu_ngay)
            if den_ngay:
                nhapkho_query = nhapkho_query.filter(Nhapkho.ngaycan <= den_ngay)
            if khachhang:
                nhapkho_query = nhapkho_query.filter(vietnamese_filter(Nhapkho.khachhang, khachhang))
            if sophieu:
                nhapkho_query = nhapkho_query.filter(Nhapkho.sophieu.contains(sophieu))
            if bienso:
                nhapkho_query = nhapkho_query.filter(vietnamese_filter(Nhapkho.bienso1_1, bienso))
            if loaihang:
                nhapkho_query = nhapkho_query.filter(vietnamese_filter(Nhapkho.loaihang, loaihang))
            
            # Sắp xếp theo ngày (mới nhất trước)
            nhapkho_query = nhapkho_query.order_by(Nhapkho.ngaycan.desc())
            
            # Thêm offset để bỏ qua một số lượng bản ghi từ đầu
            if offset and offset > 0:
                nhapkho_query = nhapkho_query.offset(offset)
                
            # Giới hạn số lượng nếu có
            if limit and limit > 0:
                nhapkho_query = nhapkho_query.limit(limit)
            
            # Thực hiện query
            nhapkho_results = nhapkho_query.all()
            result.nhapkho = nhapkho_results
            result.total_count["nhapkho"] = len(nhapkho_results)
        
        # Lấy dữ liệu từ bảng xuatkho
        if "xuatkho" in selected_tables:
            xuatkho_query = db.query(Xuatkho)
            
            # Áp dụng các điều kiện lọc
            if tu_ngay:
                xuatkho_query = xuatkho_query.filter(Xuatkho.ngaycan >= tu_ngay)
            if den_ngay:
                xuatkho_query = xuatkho_query.filter(Xuatkho.ngaycan <= den_ngay)
            if khachhang:
                xuatkho_query = xuatkho_query.filter(vietnamese_filter(Xuatkho.khachhang, khachhang))
            if sophieu:
                xuatkho_query = xuatkho_query.filter(Xuatkho.sophieu.contains(sophieu))
            if bienso:
                xuatkho_query = xuatkho_query.filter(vietnamese_filter(Xuatkho.bienso1_1, bienso))
            if loaihang:
                xuatkho_query = xuatkho_query.filter(vietnamese_filter(Xuatkho.loaihang, loaihang))
            
            # Sắp xếp theo ngày (mới nhất trước)
            xuatkho_query = xuatkho_query.order_by(Xuatkho.ngaycan.desc())
            
            # Thêm offset để bỏ qua một số lượng bản ghi từ đầu
            if offset and offset > 0:
                xuatkho_query = xuatkho_query.offset(offset)
                
            # Giới hạn số lượng nếu có
            if limit and limit > 0:
                xuatkho_query = xuatkho_query.limit(limit)
            
            # Thực hiện query
            xuatkho_results = xuatkho_query.all()
            result.xuatkho = xuatkho_results
            result.total_count["xuatkho"] = len(xuatkho_results)
        
        # Lấy dữ liệu từ bảng canthue
        if "canthue" in selected_tables:
            canthue_query = db.query(Canthue)
            
            # Áp dụng các điều kiện lọc
            if tu_ngay:
                canthue_query = canthue_query.filter(Canthue.ngaycan >= tu_ngay)
            if den_ngay:
                canthue_query = canthue_query.filter(Canthue.ngaycan <= den_ngay)
            if khachhang:
                canthue_query = canthue_query.filter(vietnamese_filter(Canthue.khachhang, khachhang))
            if sophieu:
                canthue_query = canthue_query.filter(Canthue.sophieu.contains(sophieu))
            if bienso:
                canthue_query = canthue_query.filter(vietnamese_filter(Canthue.bienso1_1, bienso))
            if loaihang:
                canthue_query = canthue_query.filter(vietnamese_filter(Canthue.loaihang, loaihang))
            
            # Sắp xếp theo ngày (mới nhất trước)
            canthue_query = canthue_query.order_by(Canthue.ngaycan.desc())
            
            # Thêm offset để bỏ qua một số lượng bản ghi từ đầu
            if offset and offset > 0:
                canthue_query = canthue_query.offset(offset)
                
            # Giới hạn số lượng nếu có
            if limit and limit > 0:
                canthue_query = canthue_query.limit(limit)
            
            # Thực hiện query
            canthue_results = canthue_query.all()
            result.canthue = canthue_results
            result.total_count["canthue"] = len(canthue_results)
        
        # Lấy dữ liệu từ bảng nhaptau
        if "nhaptau" in selected_tables:
            nhaptau_query = db.query(Nhaptau)
            
            # Áp dụng các điều kiện lọc
            if tu_ngay:
                nhaptau_query = nhaptau_query.filter(Nhaptau.ngaycan >= tu_ngay)
            if den_ngay:
                nhaptau_query = nhaptau_query.filter(Nhaptau.ngaycan <= den_ngay)
            if khachhang:
                nhaptau_query = nhaptau_query.filter(vietnamese_filter(Nhaptau.khachhang, khachhang))
            if sophieu:
                nhaptau_query = nhaptau_query.filter(Nhaptau.sophieu.contains(sophieu))
            if bienso:
                nhaptau_query = nhaptau_query.filter(vietnamese_filter(Nhaptau.bienso1_1, bienso))
            if loaihang:
                nhaptau_query = nhaptau_query.filter(vietnamese_filter(Nhaptau.loaihang, loaihang))
            
            # Sắp xếp theo ngày (mới nhất trước)
            nhaptau_query = nhaptau_query.order_by(Nhaptau.ngaycan.desc())
            
            # Thêm offset để bỏ qua một số lượng bản ghi từ đầu
            if offset and offset > 0:
                nhaptau_query = nhaptau_query.offset(offset)
                
            # Giới hạn số lượng nếu có
            if limit and limit > 0:
                nhaptau_query = nhaptau_query.limit(limit)
            
            # Thực hiện query
            nhaptau_results = nhaptau_query.all()
            result.nhaptau = nhaptau_results
            result.total_count["nhaptau"] = len(nhaptau_results)
        
        # Tính tổng số bản ghi
        result.total_count["all"] = sum(result.total_count.values())
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy dữ liệu tổng hợp: {str(e)}")

# API để get dữ liệu từ table loaihang
@app.get("/loaihang", response_model=List[LoaihangResponse])
async def get_loaihang(
    db: Session = Depends(get_db),
    mahang: str = None,     # Lọc theo mã hàng
    tenhang: str = None,    # Lọc theo tên hàng
    limit: int = None,      # Giới hạn số records trả về
    offset: int = 0         # Vị trí bắt đầu lấy dữ liệu
):
    """
    Lấy dữ liệu từ bảng loaihang với các điều kiện lọc
    
    Parameters:
    - mahang: Tìm theo mã hàng (contains)
    - tenhang: Tìm theo tên hàng (contains)
    - limit: Giới hạn số lượng records trả về
    
    Examples:
    - /loaihang
    - /loaihang?mahang=G001
    - /loaihang?tenhang=Gạo
    - /loaihang?limit=10
    """
    try:
        # Bắt đầu với query cơ bản
        query = db.query(Loaihang)
        
        # Lọc theo mã hàng
        if mahang:
            query = query.filter(vietnamese_filter(Loaihang.mahang, mahang))
            
        # Lọc theo tên hàng (hỗ trợ tiếng Việt đầy đủ)
        if tenhang:
            query = query.filter(vietnamese_filter(Loaihang.tenhang, tenhang))
        
        # Thêm offset để bỏ qua một số lượng bản ghi từ đầu
        if offset and offset > 0:
            query = query.offset(offset)
            
        # Giới hạn số lượng nếu có
        if limit and limit > 0:
            query = query.limit(limit)
            
        # Thực hiện query
        results = query.all()
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy dữ liệu loaihang: {str(e)}")

# API để get dữ liệu từ table khachhang
@app.get("/khachhang", response_model=List[KhachhangResponse])
async def get_khachhang(
    db: Session = Depends(get_db),
    makhachhang: str = None,     # Lọc theo mã khách hàng
    tenkhachhang: str = None,    # Lọc theo tên khách hàng
    loaihang: str = None,        # Lọc theo loại hàng
    limit: int = None,           # Giới hạn số records trả về
    offset: int = 0              # Vị trí bắt đầu lấy dữ liệu
):
    """
    Lấy dữ liệu từ bảng khachhang với các điều kiện lọc
    
    Parameters:
    - makhachhang: Tìm theo mã khách hàng (contains)
    - tenkhachhang: Tìm theo tên khách hàng (contains)
    - loaihang: Tìm theo loại hàng (contains)
    - limit: Giới hạn số lượng records trả về
    
    Examples:
    - /khachhang
    - /khachhang?makhachhang=KH001
    - /khachhang?tenkhachhang=CÔNG TY ABC
    - /khachhang?loaihang=Gạo&limit=10
    """
    try:
        # Bắt đầu với query cơ bản
        query = db.query(Khachhang)
        
        # Lọc theo mã khách hàng
        if makhachhang:
            query = query.filter(vietnamese_filter(Khachhang.makhachhang, makhachhang))
            
        # Lọc theo tên khách hàng (hỗ trợ tiếng Việt đầy đủ)
        if tenkhachhang:
            query = query.filter(vietnamese_filter(Khachhang.tenkhachhang, tenkhachhang))
            
        # Lọc theo loại hàng (hỗ trợ tiếng Việt đầy đủ)
        if loaihang:
            query = query.filter(vietnamese_filter(Khachhang.loaihang, loaihang))
        
        # Thêm offset để bỏ qua một số lượng bản ghi từ đầu
        if offset and offset > 0:
            query = query.offset(offset)
            
        # Giới hạn số lượng nếu có
        if limit and limit > 0:
            query = query.limit(limit)
            
        # Thực hiện query
        results = query.all()
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy dữ liệu khachhang: {str(e)}")

# API để get dữ liệu từ table xe
@app.get("/xe", response_model=List[XeResponse])
async def get_xe(
    db: Session = Depends(get_db),
    bienso: str = None,           # Lọc theo biển số xe
    tenkhachhang: str = None,     # Lọc theo tên khách hàng
    loaihang: str = None,         # Lọc theo loại hàng
    laixe: str = None,            # Lọc theo tên lái xe
    limit: int = None,            # Giới hạn số records trả về
    offset: int = 0               # Vị trí bắt đầu lấy dữ liệu
):
    """
    Lấy dữ liệu từ bảng xe với các điều kiện lọc
    
    Parameters:
    - bienso: Tìm theo biển số xe (contains)
    - tenkhachhang: Tìm theo tên khách hàng (contains)
    - loaihang: Tìm theo loại hàng (contains)
    - laixe: Tìm theo tên lái xe (contains)
    - limit: Giới hạn số lượng records trả về
    
    Examples:
    - /xe
    - /xe?bienso=51D
    - /xe?tenkhachhang=CÔNG TY ABC
    - /xe?loaihang=Gạo&laixe=Nguyễn Văn A&limit=10
    """
    try:
        # Bắt đầu với query cơ bản
        query = db.query(Xe)
        
        # Lọc theo biển số
        if bienso:
            query = query.filter(vietnamese_filter(Xe.blenso_xe, bienso))
            
        # Lọc theo tên khách hàng (hỗ trợ tiếng Việt đầy đủ)
        if tenkhachhang:
            query = query.filter(vietnamese_filter(Xe.tenkhachhang_xe, tenkhachhang))
            
        # Lọc theo loại hàng (hỗ trợ tiếng Việt đầy đủ)
        if loaihang:
            query = query.filter(vietnamese_filter(Xe.loaihang_xe, loaihang))
            
        # Lọc theo tên lái xe (hỗ trợ tiếng Việt đầy đủ)
        if laixe:
            query = query.filter(vietnamese_filter(Xe.laixe_xe, laixe))
        
        # Thêm offset để bỏ qua một số lượng bản ghi từ đầu
        if offset and offset > 0:
            query = query.offset(offset)
            
        # Giới hạn số lượng nếu có
        if limit and limit > 0:
            query = query.limit(limit)
            
        # Thực hiện query
        results = query.all()
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy dữ liệu xe: {str(e)}")

# Camera endpoint
@app.get("/camera", response_model=List[CameraResponse])
def get_camera(
    id: Optional[int] = Query(None, description="ID của camera"),
    ip: Optional[str] = Query(None, description="IP Address của camera"), 
    username: Optional[str] = Query(None, description="Username để kết nối camera"),
    active: Optional[int] = Query(None, description="Trạng thái hoạt động (0: tắt, 1: bật)"),
    port: Optional[str] = Query(None, description="Port của camera"),
    offset: Optional[int] = Query(None, ge=0, description="Bỏ qua số lượng bản ghi từ đầu"),
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Giới hạn số lượng kết quả trả về"),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách camera theo điều kiện lọc
    """
    try:
        # Tạo query cơ bản
        query = db.query(Camera)
        
        # Áp dụng filters với validation
        if id is not None:
            try:
                camera_id = int(id)
                query = query.filter(Camera.ID == camera_id)
            except (ValueError, TypeError):
                raise HTTPException(status_code=400, detail="ID phải là số nguyên hợp lệ")
        
        if ip:
            query = query.filter(Camera.IPAddrees.ilike(f"%{ip}%"))
        
        if username:
            query = query.filter(Camera.UseName.ilike(f"%{username}%"))
        
        if active is not None:
            try:
                active_status = int(active)
                if active_status not in [0, 1]:
                    raise HTTPException(status_code=400, detail="Active phải là 0 (tắt) hoặc 1 (bật)")
                query = query.filter(Camera.Active == active_status)
            except (ValueError, TypeError):
                raise HTTPException(status_code=400, detail="Active phải là số nguyên (0 hoặc 1)")
        
        if port:
            query = query.filter(Camera.Port.ilike(f"%{port}%"))
        
        # Thêm offset để bỏ qua một số lượng bản ghi từ đầu
        if offset and offset > 0:
            query = query.offset(offset)
            
        # Giới hạn số lượng nếu có
        if limit and limit > 0:
            query = query.limit(limit)
            
        # Thực hiện query
        results = query.all()
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy dữ liệu camera: {str(e)}")

# ==== PICTURE MANAGEMENT APIs ====

# Các hằng số
PICTURE_TYPES = {
    "NK": "NhapKho",
    "CT": "CanThue", 
    "NT": "NhapTau",
    "XK": "XuatKho"
}

def get_picture_base_path():
    """Lấy đường dẫn base cho hình ảnh từ environment variable"""
    return os.getenv("PICTURE_BASE_PATH", r"D:\Picture")

def create_folder_structure(picture_type: str, date: str):
    """
    Tạo cấu trúc thư mục cho hình ảnh
    Args:
        picture_type: NK, CT, NT, XK
        date: YYYY-MM-DD format
    Returns:
        str: Đường dẫn thư mục đã tạo
    """
    base_path = get_picture_base_path()
    folder_path = os.path.join(base_path, picture_type, date)
    
    try:
        pathlib.Path(folder_path).mkdir(parents=True, exist_ok=True)
        return folder_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Không thể tạo thư mục {folder_path}: {str(e)}")

def generate_filename(ticket_number: str, camera_number: int, sequence: int):
    """
    Tạo tên file theo format: [Số phiếu]-CMR[Camera]_[Sequence]
    Args:
        ticket_number: Số phiếu
        camera_number: Số camera (1, 2, 3...)
        sequence: Lần chụp thứ mấy (1, 2, 3...)
    Returns:
        str: Tên file (không bao gồm extension)
    """
    return f"{ticket_number}-CMR{camera_number}_{sequence}"

def parse_filename(filename: str):
    """
    Parse tên file để lấy thông tin
    Args:
        filename: Tên file (có thể có extension)
    Returns:
        dict: {ticket_number, camera_number, sequence} hoặc None nếu không match
    """
    # Loại bỏ extension
    name_without_ext = os.path.splitext(filename)[0]
    
    # Pattern: [Số phiếu]-CMR[Camera]_[Sequence]
    pattern = r"^(.+)-CMR(\d+)_(\d+)$"
    match = re.match(pattern, name_without_ext)
    
    if match:
        return {
            "ticket_number": match.group(1),
            "camera_number": int(match.group(2)),
            "sequence": int(match.group(3))
        }
    return None

@app.post("/picture/upload", response_model=PictureUploadResponse)
async def upload_picture(
    file: UploadFile = File(...),
    ticket_number: str = Query(..., description="Số phiếu"),
    picture_type: str = Query(..., description="Loại phiếu: NK, CT, NT, XK"),
    camera_number: int = Query(..., description="Số camera (1, 2, 3...)"),
    sequence: int = Query(1, description="Lần chụp thứ mấy (1, 2, 3...)"),
    date: Optional[str] = Query(None, description="Ngày chụp (YYYY-MM-DD), mặc định là hôm nay")
):
    """
    Upload hình ảnh với cấu trúc thư mục theo ngày và tên file theo camera
    """
    try:
        # Validate picture_type
        if picture_type not in PICTURE_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"Loại phiếu không hợp lệ. Cho phép: {', '.join(PICTURE_TYPES.keys())}"
            )
        
        # Validate camera_number
        if camera_number < 1:
            raise HTTPException(status_code=400, detail="Số camera phải >= 1")
            
        # Validate sequence
        if sequence < 1:
            raise HTTPException(status_code=400, detail="Sequence phải >= 1")
        
        # Sử dụng ngày hiện tại nếu không được cung cấp
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Định dạng ngày không hợp lệ. Sử dụng YYYY-MM-DD")
        
        # Tạo cấu trúc thư mục
        folder_path = create_folder_structure(picture_type, date)
        folder_created = not os.path.exists(folder_path)
        
        # Tạo tên file
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
        filename_base = generate_filename(ticket_number, camera_number, sequence)
        filename = filename_base + file_extension
        
        # Đường dẫn đầy đủ của file
        file_path = os.path.join(folder_path, filename)
        
        # Kiểm tra file đã tồn tại
        if os.path.exists(file_path):
            raise HTTPException(
                status_code=400, 
                detail=f"File đã tồn tại: {filename}"
            )
        
        # Lưu file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        return PictureUploadResponse(
            success=True,
            message=f"Upload thành công: {filename}",
            file_path=file_path,
            folder_created=folder_created
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi upload file: {str(e)}")

@app.get("/picture/list", response_model=PictureListResponse)
def list_pictures(
    ticket_number: Optional[str] = Query(None, description="Số phiếu cần tìm"),
    date: Optional[str] = Query(None, description="Ngày cụ thể (YYYY-MM-DD)"),
    picture_type: Optional[str] = Query(None, description="Loại phiếu: NK, CT, NT, XK"),
    camera_number: Optional[int] = Query(None, description="Số camera"),
    sequence: Optional[int] = Query(None, description="Lần chụp (1, 2, 3...)"),
    limit: Optional[int] = Query(None, description="Giới hạn số lượng kết quả")
):
    """
    Lấy danh sách hình ảnh theo các điều kiện lọc.
    
    Parameters:
    - ticket_number: Số phiếu cần tìm (chính xác)
    - date: Ngày cụ thể (YYYY-MM-DD)
    - picture_type: Loại phiếu (NK, CT, NT, XK)
    - camera_number: Số camera
    - sequence: Lần chụp (1, 2, 3...)
    - limit: Giới hạn số lượng kết quả trả về
    
    Examples:
    - /picture/list?ticket_number=PH001
    - /picture/list?date=2025-08-17
    - /picture/list?ticket_number=PH001&date=2025-08-17
    - /picture/list?ticket_number=PH001&picture_type=NK&camera_number=1
    """
    try:
        base_path = get_picture_base_path()
        pictures = []
        
        # Validate picture_type nếu được cung cấp
        if picture_type and picture_type not in PICTURE_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"Loại phiếu không hợp lệ. Cho phép: {', '.join(PICTURE_TYPES.keys())}"
            )
        
        # Validate date format nếu được cung cấp
        if date:
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Định dạng ngày không hợp lệ. Sử dụng YYYY-MM-DD")
        
        # Xác định các thư mục cần scan
        picture_types_to_scan = [picture_type] if picture_type else list(PICTURE_TYPES.keys())
        
        for ptype in picture_types_to_scan:
            type_path = os.path.join(base_path, ptype)
            if not os.path.exists(type_path):
                continue
                
            # Xác định các thư mục ngày cần scan
            if date:
                # Nếu có date cụ thể, chỉ tìm trong thư mục đó
                date_folders = [date] if os.path.exists(os.path.join(type_path, date)) else []
            else:
                # Lấy tất cả thư mục ngày
                date_folders = [d for d in os.listdir(type_path) 
                              if os.path.isdir(os.path.join(type_path, d)) and re.match(r"\d{4}-\d{2}-\d{2}", d)]
            
            for date_folder in date_folders:
                folder_path = os.path.join(type_path, date_folder)
                
                if os.path.exists(folder_path):
                    for filename in os.listdir(folder_path):
                        file_path = os.path.join(folder_path, filename)
                        
                        # Chỉ xử lý file (không phải thư mục)
                        if os.path.isfile(file_path):
                            # Parse thông tin từ tên file
                            file_info = parse_filename(filename)
                            
                            if file_info:
                                # Áp dụng các bộ lọc
                                if ticket_number and file_info["ticket_number"] != ticket_number:
                                    continue
                                    
                                if camera_number and file_info["camera_number"] != camera_number:
                                    continue
                                
                                if sequence and file_info["sequence"] != sequence:
                                    continue
                                
                                # Lấy thông tin file
                                file_stat = os.stat(file_path)
                                
                                # Tạo URL để xem hình ảnh
                                image_url = f"/picture/view/{ptype}/{date_folder}/{filename}"
                                
                                pictures.append(PictureInfo(
                                    filename=filename,
                                    file_path=file_path,
                                    image_url=image_url,
                                    ticket_number=file_info["ticket_number"],
                                    picture_type=ptype,
                                    camera_number=file_info["camera_number"],
                                    sequence=file_info["sequence"],
                                    date=date_folder,
                                    file_size=file_stat.st_size,
                                    created_time=datetime.fromtimestamp(file_stat.st_ctime).isoformat()
                                ))
                                
                                # Kiểm tra giới hạn số lượng
                                if limit and len(pictures) >= limit:
                                    break
                    
                    # Kiểm tra giới hạn số lượng (break khỏi loop date_folder)
                    if limit and len(pictures) >= limit:
                        break
                
                # Kiểm tra giới hạn số lượng (break khỏi loop picture type)
                if limit and len(pictures) >= limit:
                    break
        
        # Sắp xếp theo ngày và tên file
        pictures.sort(key=lambda x: (x.date, x.filename))
        
        return PictureListResponse(
            success=True,
            message=f"Tìm thấy {len(pictures)} hình ảnh",
            pictures=pictures
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy danh sách hình ảnh: {str(e)}")

@app.get("/picture/get")
def get_picture(
    ticket_number: str = Query(..., description="Số phiếu (bắt buộc)"),
    camera_number: int = Query(..., description="Số camera (bắt buộc)"),
    sequence: int = Query(..., description="Lần chụp (bắt buộc)"),
    date: Optional[str] = Query(None, description="Ngày (YYYY-MM-DD), nếu không có sẽ tìm trong tất cả ngày"),
    picture_type: Optional[str] = Query(None, description="Loại phiếu: NK, CT, NT, XK")
):
    """
    Lấy chính xác 1 hình ảnh theo số phiếu, camera, lần chụp.
    Trả về thông tin file hoặc lỗi nếu không tìm thấy.
    """
    try:
        base_path = get_picture_base_path()
        
        # Validate picture_type nếu được cung cấp
        if picture_type and picture_type not in PICTURE_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"Loại phiếu không hợp lệ. Cho phép: {', '.join(PICTURE_TYPES.keys())}"
            )
        
        # Validate date format nếu được cung cấp
        if date:
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Định dạng ngày không hợp lệ. Sử dụng YYYY-MM-DD")
        
        # Xác định các thư mục cần tìm
        picture_types_to_search = [picture_type] if picture_type else list(PICTURE_TYPES.keys())
        
        for ptype in picture_types_to_search:
            type_path = os.path.join(base_path, ptype)
            if not os.path.exists(type_path):
                continue
                
            # Xác định các thư mục ngày cần tìm
            if date:
                date_folders = [date] if os.path.exists(os.path.join(type_path, date)) else []
            else:
                date_folders = [d for d in os.listdir(type_path) 
                              if os.path.isdir(os.path.join(type_path, d)) and re.match(r"\d{4}-\d{2}-\d{2}", d)]
            
            for date_folder in date_folders:
                folder_path = os.path.join(type_path, date_folder)
                
                if os.path.exists(folder_path):
                    for filename in os.listdir(folder_path):
                        file_path = os.path.join(folder_path, filename)
                        
                        if os.path.isfile(file_path):
                            # Parse thông tin từ tên file
                            file_info = parse_filename(filename)
                            
                            if file_info:
                                # Kiểm tra khớp chính xác
                                if (file_info["ticket_number"] == ticket_number and 
                                    file_info["camera_number"] == camera_number and 
                                    file_info["sequence"] == sequence):
                                    
                                    # Tìm thấy! Trả về thông tin file
                                    file_stat = os.stat(file_path)
                                    
                                    return {
                                        "success": True,
                                        "message": f"Tìm thấy hình ảnh: {filename}",
                                        "picture": {
                                            "filename": filename,
                                            "file_path": file_path,
                                            "ticket_number": file_info["ticket_number"],
                                            "picture_type": ptype,
                                            "camera_number": file_info["camera_number"],
                                            "sequence": file_info["sequence"],
                                            "date": date_folder,
                                            "file_size": file_stat.st_size,
                                            "created_time": datetime.fromtimestamp(file_stat.st_ctime).isoformat()
                                        }
                                    }
        
        # Không tìm thấy
        return {
            "success": False,
            "message": f"Không tìm thấy hình ảnh: Số phiếu {ticket_number}, Camera {camera_number}, Lần chụp {sequence}",
            "picture": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy hình ảnh: {str(e)}")

@app.delete("/picture/delete")
def delete_picture(
    file_path: str = Query(..., description="Đường dẫn đầy đủ của file cần xóa")
):
    """
    Xóa hình ảnh
    """
    try:
        base_path = get_picture_base_path()
        
        # Kiểm tra file có nằm trong base path không (bảo mật)
        if not file_path.startswith(base_path):
            raise HTTPException(status_code=400, detail="Đường dẫn file không hợp lệ")
        
        # Kiểm tra file tồn tại
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File không tồn tại")
        
        # Xóa file
        os.remove(file_path)
        
        return {"success": True, "message": f"Đã xóa file: {os.path.basename(file_path)}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa file: {str(e)}")

@app.get("/picture/folders")
def get_picture_folders():
    """
    Lấy cấu trúc thư mục hình ảnh
    """
    try:
        base_path = get_picture_base_path()
        result = {
            "base_path": base_path,
            "folders": {}
        }
        
        for ptype in PICTURE_TYPES.keys():
            type_path = os.path.join(base_path, ptype)
            result["folders"][ptype] = {
                "full_name": PICTURE_TYPES[ptype],
                "path": type_path,
                "exists": os.path.exists(type_path),
                "dates": []
            }
            
            if os.path.exists(type_path):
                date_folders = [d for d in os.listdir(type_path) 
                              if os.path.isdir(os.path.join(type_path, d)) and re.match(r"\d{4}-\d{2}-\d{2}", d)]
                date_folders.sort(reverse=True)  # Ngày mới nhất trước
                result["folders"][ptype]["dates"] = date_folders
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy cấu trúc thư mục: {str(e)}")

@app.get("/picture/view/{picture_type}/{date}/{filename}")
def view_picture(
    picture_type: str,
    date: str, 
    filename: str
):
    """
    Xem/tải hình ảnh trực tiếp
    
    Parameters:
    - picture_type: Loại phiếu (NK, CT, NT, XK)
    - date: Ngày (YYYY-MM-DD)
    - filename: Tên file hình ảnh
    
    Returns: File hình ảnh trực tiếp
    
    Examples:
    - GET /picture/view/NK/2025-08-17/5-CMR1_1.png
    - GET /picture/view/CT/2025-08-17/PH001-CMR2_1.jpg
    """
    try:
        # Validate picture_type
        if picture_type not in PICTURE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Loại phiếu không hợp lệ. Cho phép: {', '.join(PICTURE_TYPES.keys())}"
            )
        
        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Định dạng ngày không hợp lệ. Sử dụng YYYY-MM-DD")
        
        # Tạo đường dẫn file
        base_path = get_picture_base_path()
        file_path = os.path.join(base_path, picture_type, date, filename)
        
        # Kiểm tra file có tồn tại
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"Không tìm thấy file: {filename}")
        
        # Kiểm tra đây có phải là file không (không phải thư mục)
        if not os.path.isfile(file_path):
            raise HTTPException(status_code=400, detail="Path không phải là file")
        
        # Xác định content type
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = "application/octet-stream"
        
        # Trả về file trực tiếp
        return FileResponse(
            path=file_path,
            media_type=content_type,
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xem hình ảnh: {str(e)}")

@app.get("/picture/image")
def get_picture_image(
    ticket_number: str = Query(..., description="Số phiếu"),
    camera_number: int = Query(..., description="Số camera"),
    sequence: int = Query(..., description="Lần chụp"), 
    date: Optional[str] = Query(None, description="Ngày (YYYY-MM-DD), nếu không có sẽ tìm trong tất cả ngày"),
    picture_type: Optional[str] = Query(None, description="Loại phiếu: NK, CT, NT, XK")
):
    """
    Lấy hình ảnh trực tiếp theo số phiếu, camera, lần chụp
    
    Parameters:
    - ticket_number: Số phiếu (bắt buộc)
    - camera_number: Số camera (bắt buộc)
    - sequence: Lần chụp (bắt buộc)
    - date: Ngày (YYYY-MM-DD), nếu không có sẽ tìm trong tất cả ngày
    - picture_type: Loại phiếu (NK, CT, NT, XK)
    
    Returns: File hình ảnh trực tiếp
    
    Examples:
    - GET /picture/image?ticket_number=5&camera_number=1&sequence=1
    - GET /picture/image?ticket_number=PH001&camera_number=2&sequence=1&date=2025-08-17
    """
    try:
        # Validate parameters
        if camera_number < 1:
            raise HTTPException(status_code=400, detail="Camera number phải >= 1")
        
        if sequence < 1:
            raise HTTPException(status_code=400, detail="Sequence phải >= 1")
        
        # Validate picture_type nếu được cung cấp
        if picture_type and picture_type not in PICTURE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Loại phiếu không hợp lệ. Cho phép: {', '.join(PICTURE_TYPES.keys())}"
            )
        
        # Validate date format nếu được cung cấp
        if date:
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Định dạng ngày không hợp lệ. Sử dụng YYYY-MM-DD")
        
        base_path = get_picture_base_path()
        
        # Xác định các loại phiếu cần tìm
        picture_types_to_search = [picture_type] if picture_type else list(PICTURE_TYPES.keys())
        
        # Tìm kiếm file
        for ptype in picture_types_to_search:
            type_path = os.path.join(base_path, ptype)
            if not os.path.exists(type_path):
                continue
            
            # Xác định thư mục ngày cần tìm
            if date:
                date_folders = [date] if os.path.exists(os.path.join(type_path, date)) else []
            else:
                date_folders = [d for d in os.listdir(type_path) 
                              if os.path.isdir(os.path.join(type_path, d)) and re.match(r"\d{4}-\d{2}-\d{2}", d)]
            
            for date_folder in date_folders:
                folder_path = os.path.join(type_path, date_folder)
                
                if os.path.exists(folder_path):
                    for filename in os.listdir(folder_path):
                        file_path = os.path.join(folder_path, filename)
                        
                        # Chỉ xử lý file
                        if os.path.isfile(file_path):
                            # Parse thông tin từ tên file
                            file_info = parse_filename(filename)
                            
                            if file_info:
                                # Kiểm tra khớp chính xác
                                if (file_info["ticket_number"] == ticket_number and 
                                    file_info["camera_number"] == camera_number and 
                                    file_info["sequence"] == sequence):
                                    
                                    # Tìm thấy! Trả về file trực tiếp
                                    content_type, _ = mimetypes.guess_type(file_path)
                                    if content_type is None:
                                        content_type = "application/octet-stream"
                                    
                                    return FileResponse(
                                        path=file_path,
                                        media_type=content_type,
                                        filename=filename
                                    )
        
        # Không tìm thấy
        raise HTTPException(
            status_code=404, 
            detail=f"Không tìm thấy hình ảnh: Số phiếu {ticket_number}, Camera {camera_number}, Lần chụp {sequence}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy hình ảnh: {str(e)}")

# Chạy server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
