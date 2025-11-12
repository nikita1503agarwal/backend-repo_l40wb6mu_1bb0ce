"""
Database Schemas for Fixed Asset Management

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercased class name (e.g., Asset -> "asset").

These schemas are used for validation when creating/updating documents.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date


class Asset(BaseModel):
    """
    Fixed assets in your organization.
    Collection name: "asset"
    """
    name: str = Field(..., description="Asset name")
    category: str = Field(..., description="Category (e.g., Laptop, Vehicle, Furniture)")
    tag: str = Field(..., description="Unique asset tag or barcode")
    serial_number: Optional[str] = Field(None, description="Manufacturer serial number")
    status: Literal["available", "in_use", "maintenance", "retired"] = Field(
        "available", description="Lifecycle status"
    )
    location_id: Optional[str] = Field(None, description="Reference to location _id")
    assigned_to: Optional[str] = Field(None, description="Person currently responsible")
    purchase_date: Optional[date] = Field(None, description="Purchase date")
    cost: Optional[float] = Field(None, ge=0, description="Purchase cost")
    notes: Optional[str] = Field(None, description="Additional notes")


class Location(BaseModel):
    """
    Physical locations where assets reside.
    Collection name: "location"
    """
    name: str = Field(..., description="Location name")
    code: str = Field(..., description="Short code")
    address: Optional[str] = Field(None, description="Street address or details")


class Assignment(BaseModel):
    """
    Asset assignment history.
    Collection name: "assignment"
    """
    asset_id: str = Field(..., description="Reference to asset _id")
    assignee_name: str = Field(..., description="Person responsible")
    location_id: Optional[str] = Field(None, description="Reference to location _id")


class Audit(BaseModel):
    """
    Audit trail for asset actions (status changes, moves, edits).
    Collection name: "audit"
    """
    asset_id: str = Field(..., description="Reference to asset _id")
    action: str = Field(..., description="Action performed")
    notes: Optional[str] = Field(None, description="Optional details")
