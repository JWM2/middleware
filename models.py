from sqlalchemy import Column, Integer, String
from database import Base

class DeviceEntry(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    deviceid = Column(String, index=True)
    source_interface = Column(String, index=True)
    ip = Column(String, index=True)
    mac = Column(String)
