from sqlalchemy import create_engine, Column, String, Integer, Date, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def build_database_url():
    """Build database URL từ các tham số environment"""
    # Kiểm tra xem có DATABASE_URL đầy đủ không
    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("mssql+pyodbc://"):
        return database_url
    
    # Build từ các tham số riêng biệt
    server = os.getenv("DB_SERVER", "localhost")
    port = os.getenv("DB_PORT", "1433")
    database = os.getenv("DB_NAME", "datacanxe")
    username = os.getenv("DB_USERNAME", "")
    password = os.getenv("DB_PASSWORD", "")
    driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    trusted_connection = os.getenv("DB_TRUSTED_CONNECTION", "yes").lower()
    
    # Build connection string
    if username and password:
        # SQL Server Authentication
        conn_str = f"mssql+pyodbc://{username}:{password}@{server}:{port}/{database}"
    else:
        # Windows Authentication
        conn_str = f"mssql+pyodbc://{server}:{port}/{database}"
    
    # Add driver và trusted connection
    conn_str += f"?driver={driver.replace(' ', '+')}"
    
    if not username and trusted_connection == "yes":
        conn_str += "&trusted_connection=yes"
    
    return conn_str

# Database URL
DATABASE_URL = build_database_url()
print(f"🔗 Database URL: {DATABASE_URL}")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=False)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# User model
class User(Base):
    __tablename__ = "user"
    
    iduser = Column(String(50), primary_key=True)
    ten = Column(String(100))
    password = Column(String(50))

# Nhapkho model - Import Warehouse Tickets
class Nhapkho(Base):
    __tablename__ = "nhapkho"
    
    sophieu = Column(Integer, primary_key=True)           # Ticket number
    ngaycan = Column(Date)                                # Weighing date
    msp = Column(String(50))                              # Code (NK, etc.)
    bienso1_1 = Column(String(50))                        # License plate 1
    bienso1_2 = Column(String(50))                        # License plate 2
    bienso2_1 = Column(String(50))                        # License plate 3
    bienso2_2 = Column(String(50))                        # License plate 4
    khachhang = Column(String(100))                       # Customer name
    loaihang = Column(String(100))                        # Goods name
    laixe = Column(String(100))                           # Driver name
    nguoican = Column(String(100))                        # Weigher name
    khoiluonglan1 = Column(DECIMAL(18,2))                 # First weighing value
    khoiluonglan2 = Column(DECIMAL(18,2))                 # Second weighing value
    khoiluongtinh = Column(DECIMAL(18,2))                 # Net weight
    khoiluongtru = Column(DECIMAL(18,2))                  # Deducted weight
    phantramKCL = Column(DECIMAL(5,2))                    # Deducted percent
    khoiluongthanhtoan = Column(DECIMAL(18,2))            # Payable weight
    dongia = Column(DECIMAL(18,2))                        # Unit price
    thanhtien = Column(DECIMAL(18,2))                     # Total payment
    thoigiancanlan1 = Column(String(50))                  # Time of first weighing
    thoigiancanlan2 = Column(String(50))                  # Time of second weighing
    ghichu = Column(String(200))                          # Note
    chungtu = Column(String(100))                         # Document/Customer address
    lancan = Column(Integer)                              # Weighing count (1 or 2)
    lanin = Column(Integer)                               # Print count
    xoaphieu = Column(Integer, default=0)                 # Deleted flag (0: active, 1: deleted)

# Xuatkho model - Export Warehouse Tickets
class Xuatkho(Base):
    __tablename__ = "xuatkho"
    
    sophieu = Column(Integer, primary_key=True)           # Ticket number
    ngaycan = Column(Date)                                # Weighing date
    msp = Column(String(50))                              # Code (NK, etc.)
    bienso1_1 = Column(String(50))                        # License plate 1
    bienso1_2 = Column(String(50))                        # License plate 2
    bienso2_1 = Column(String(50))                        # License plate 3
    bienso2_2 = Column(String(50))                        # License plate 4
    khachhang = Column(String(100))                       # Customer name
    loaihang = Column(String(100))                        # Goods name
    laixe = Column(String(100))                           # Driver name
    nguoican = Column(String(100))                        # Weigher name
    khoiluonglan1 = Column(DECIMAL(18,2))                 # First weighing value
    khoiluonglan2 = Column(DECIMAL(18,2))                 # Second weighing value
    khoiluongtinh = Column(DECIMAL(18,2))                 # Net weight
    khoiluongtru = Column(DECIMAL(18,2))                  # Deducted weight
    phantramKCL = Column(DECIMAL(5,2))                    # Deducted percent
    khoiluongthanhtoan = Column(DECIMAL(18,2))            # Payable weight
    dongia = Column(DECIMAL(18,2))                        # Unit price
    thanhtien = Column(DECIMAL(18,2))                     # Total payment
    thoigiancanlan1 = Column(String(50))                  # Time of first weighing
    thoigiancanlan2 = Column(String(50))                  # Time of second weighing
    ghichu = Column(String(200))                          # Note
    chungtu = Column(String(100))                         # Document/Customer address
    lancan = Column(Integer)                              # Weighing count (1 or 2)
    lanin = Column(Integer)                               # Print count
    xoaphieu = Column(Integer, default=0)                 # Deleted flag (0: active, 1: deleted)

# Canthue model - Weighing Service Tickets
class Canthue(Base):
    __tablename__ = "canthue"
    
    sophieu = Column(Integer, primary_key=True)           # Ticket number
    ngaycan = Column(Date)                                # Weighing date
    msp = Column(String(50))                              # Code (NK, etc.)
    bienso1_1 = Column(String(50))                        # License plate 1
    bienso1_2 = Column(String(50))                        # License plate 2
    bienso2_1 = Column(String(50))                        # License plate 3
    bienso2_2 = Column(String(50))                        # License plate 4
    khachhang = Column(String(100))                       # Customer name
    loaihang = Column(String(100))                        # Goods name
    laixe = Column(String(100))                           # Driver name
    nguoican = Column(String(100))                        # Weigher name
    khoiluonglan1 = Column(DECIMAL(18,2))                 # First weighing value
    khoiluonglan2 = Column(DECIMAL(18,2))                 # Second weighing value
    khoiluongtinh = Column(DECIMAL(18,2))                 # Net weight
    khoiluongtru = Column(DECIMAL(18,2))                  # Deducted weight
    phantramKCL = Column(DECIMAL(5,2))                    # Deducted percent
    khoiluongthanhtoan = Column(DECIMAL(18,2))            # Payable weight
    dongia = Column(DECIMAL(18,2))                        # Unit price
    thanhtien = Column(DECIMAL(18,2))                     # Total payment
    thoigiancanlan1 = Column(String(50))                  # Time of first weighing
    thoigiancanlan2 = Column(String(50))                  # Time of second weighing
    ghichu = Column(String(200))                          # Note
    chungtu = Column(String(100))                         # Document/Customer address
    lancan = Column(Integer)                              # Weighing count (1 or 2)
    lanin = Column(Integer)                               # Print count
    xoaphieu = Column(Integer, default=0)                 # Deleted flag (0: active, 1: deleted)

# Nhaptau model - Ship Import Tickets
class Nhaptau(Base):
    __tablename__ = "nhaptau"
    
    sophieu = Column(Integer, primary_key=True)           # Ticket number
    ngaycan = Column(Date)                                # Weighing date
    msp = Column(String(50))                              # Code (NK, etc.)
    bienso1_1 = Column(String(50))                        # License plate 1
    bienso1_2 = Column(String(50))                        # License plate 2
    bienso2_1 = Column(String(50))                        # License plate 3
    bienso2_2 = Column(String(50))                        # License plate 4
    khachhang = Column(String(100))                       # Customer name
    loaihang = Column(String(100))                        # Goods name
    laixe = Column(String(100))                           # Driver name
    nguoican = Column(String(100))                        # Weigher name
    khoiluonglan1 = Column(DECIMAL(18,2))                 # First weighing value
    khoiluonglan2 = Column(DECIMAL(18,2))                 # Second weighing value
    khoiluongtinh = Column(DECIMAL(18,2))                 # Net weight
    khoiluongtru = Column(DECIMAL(18,2))                  # Deducted weight
    phantramKCL = Column(DECIMAL(5,2))                    # Deducted percent
    khoiluongthanhtoan = Column(DECIMAL(18,2))            # Payable weight
    dongia = Column(DECIMAL(18,2))                        # Unit price
    thanhtien = Column(DECIMAL(18,2))                     # Total payment
    thoigiancanlan1 = Column(String(50))                  # Time of first weighing
    thoigiancanlan2 = Column(String(50))                  # Time of second weighing
    ghichu = Column(String(200))                          # Note
    chungtu = Column(String(100))                         # Document/Customer address
    lancan = Column(Integer)                              # Weighing count (1 or 2)
    lanin = Column(Integer)                               # Print count
    xoaphieu = Column(Integer, default=0)                 # Deleted flag (0: active, 1: deleted)

# Loaihang model - Product/Goods Type
class Loaihang(Base):
    __tablename__ = "loaihang"
    
    mahang = Column(String(50), primary_key=True)        # Product/Goods code
    tenhang = Column(String(255))                        # Product/Goods name
    tykhoi = Column(DECIMAL(18, 4))                      # Volume ratio
    dongia = Column(DECIMAL(18, 2))                      # Unit price

# Khachhang model - Customer
class Khachhang(Base):
    __tablename__ = "khachhang"
    
    ID = Column(Integer, primary_key=True)                # ID
    makhachhang = Column(String(20))                      # Customer code
    tenkhachhang = Column(String(50))                     # Customer name
    diachikhachhang = Column(String(45))                  # Customer address
    ghichukhachhang = Column(String(45))                  # Customer note
    loaihang = Column(String(50))                         # Product/Goods type

# Xe model - Vehicle
class Xe(Base):
    __tablename__ = "xe"
    
    ID = Column(Integer, primary_key=True)                # ID
    masoxe_xe = Column(String(20))                        # Vehicle code
    blenso_xe = Column(String(20))                        # License plate
    tenkhachhang_xe = Column(String(45))                  # Customer name
    diachixe_xe = Column(String(45))                      # Address
    loaihang_xe = Column(String(20))                      # Product/Goods type
    laixe_xe = Column(String(45))                         # Driver name
    ghichu_xe = Column(String(45))                        # Note

# Camera model - Camera Configuration
class Camera(Base):
    __tablename__ = "camera"
    
    ID = Column(Integer, primary_key=True)                # ID
    IPAddrees = Column(String(20))                        # IP Address
    UseName = Column(String(20))                          # Username
    Password = Column(String(20))                         # Password
    Port = Column(String(4))                              # Port
    Active = Column(Integer)                              # Active status (0: inactive, 1: active)
    SubStream = Column(Integer)                           # SubStream (0: main stream, 1: sub stream)
    Caching = Column(String(5))                           # Caching setting

# Create tables
def create_tables():
    """Tạo các bảng trong database"""
    Base.metadata.create_all(bind=engine)

# Dependency để get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
