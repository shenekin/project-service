"""
API router for vendor management
"""

from fastapi import APIRouter
from app.models.schemas import VendorResponse
from app.services.vendor_service import VendorService


router = APIRouter(prefix="/api/v1/vendors", tags=["vendors"])


@router.get("", response_model=list[VendorResponse])
async def list_vendors():
    """List all vendors"""
    service = VendorService()
    return await service.list_vendors()


@router.get("/{vendor_id}", response_model=VendorResponse)
async def get_vendor(vendor_id: int):
    """Get vendor by ID"""
    service = VendorService()
    return await service.get_vendor(vendor_id)

