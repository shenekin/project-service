"""
Service layer for Vendor Management
"""

from typing import List
from fastapi import HTTPException, status
from app.dao.vendor_dao import VendorDAO
from app.models.schemas import VendorCreate, VendorUpdate


class VendorService:
    """Service for vendor management operations"""
    
    def __init__(self):
        """Initialize vendor service"""
        self.vendor_dao = VendorDAO()
    
    async def list_vendors(self) -> List[dict]:
        """List all vendors"""
        vendors = await self.vendor_dao.list_all()
        return [v.to_dict() for v in vendors]
    
    async def get_vendor(self, vendor_id: int) -> dict:
        """Get vendor by ID"""
        vendor = await self.vendor_dao.get_by_id(vendor_id)
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor with ID {vendor_id} not found"
            )
        return vendor.to_dict()

