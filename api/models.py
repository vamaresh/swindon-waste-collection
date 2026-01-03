"""
Pydantic models for the Swindon Waste Collection API
"""
from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field


class Address(BaseModel):
    """Address model for UPRN lookup results"""
    uprn: str = Field(..., description="Unique Property Reference Number")
    address: str = Field(..., description="Full formatted address")


class UPRNLookupRequest(BaseModel):
    """Request model for UPRN lookup"""
    postcode: str = Field(..., description="UK postcode", min_length=5, max_length=10)


class UPRNLookupResponse(BaseModel):
    """Response model for UPRN lookup"""
    addresses: List[Address] = Field(..., description="List of addresses found")


class Collection(BaseModel):
    """Waste collection model"""
    date: str = Field(..., description="Collection date in ISO format (YYYY-MM-DD)")
    type: str = Field(..., description="Type of waste collection")
    icon: str = Field(..., description="Icon identifier for the waste type")
    days_until: int = Field(..., description="Number of days until collection")


class CollectionsResponse(BaseModel):
    """Response model for collections endpoint"""
    collections: List[Collection] = Field(..., description="List of upcoming collections")
    uprn: str = Field(..., description="UPRN for which collections were retrieved")


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Current timestamp in ISO format")
