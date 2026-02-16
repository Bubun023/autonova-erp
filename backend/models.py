from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime, date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, Boolean, ForeignKey, Text, Numeric, Date
from typing import List, Optional
from decimal import Decimal

db = SQLAlchemy()
bcrypt = Bcrypt()


class Role(db.Model):
    """Role model for user permissions"""
    __tablename__ = 'roles'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    users: Mapped[List["User"]] = relationship('User', back_populates='role')
    
    def to_dict(self):
        """Convert role to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Role {self.name}>'


class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('roles.id'), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    role: Mapped["Role"] = relationship('Role', back_populates='users')
    
    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role.to_dict() if self.role else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class Customer(db.Model):
    """Customer model"""
    __tablename__ = 'customers'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(120), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    address: Mapped[str] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - cascade delete for customer vehicles
    vehicles: Mapped[List["Vehicle"]] = relationship('Vehicle', back_populates='owner', cascade='all, delete-orphan')
    
    def to_dict(self, include_vehicles=False):
        """Convert customer to dictionary"""
        data = {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_vehicles:
            data['vehicles'] = [vehicle.to_dict() for vehicle in self.vehicles]
        
        return data
    
    def __repr__(self):
        return f'<Customer {self.first_name} {self.last_name}>'


class Vehicle(db.Model):
    """Vehicle model"""
    __tablename__ = 'vehicles'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey('customers.id'), nullable=False)
    make: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(50), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    vin: Mapped[str] = mapped_column(String(17), unique=True, nullable=True)
    license_plate: Mapped[str] = mapped_column(String(20), nullable=True)
    color: Mapped[str] = mapped_column(String(30), nullable=True)
    mileage: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner: Mapped["Customer"] = relationship('Customer', back_populates='vehicles')
    
    def to_dict(self, include_owner=False):
        """Convert vehicle to dictionary"""
        data = {
            'id': self.id,
            'customer_id': self.customer_id,
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'vin': self.vin,
            'license_plate': self.license_plate,
            'color': self.color,
            'mileage': self.mileage,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_owner:
            data['owner'] = self.owner.to_dict() if self.owner else None
        
        return data
    
    def __repr__(self):
        return f'<Vehicle {self.year} {self.make} {self.model}>'


class InsuranceCompany(db.Model):
    """Insurance company model"""
    __tablename__ = 'insurance_companies'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    contact_person: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert insurance company to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'contact_person': self.contact_person,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<InsuranceCompany {self.name}>'


class Estimate(db.Model):
    """Estimate model"""
    __tablename__ = 'estimates'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    estimate_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey('customers.id'), nullable=False)
    vehicle_id: Mapped[int] = mapped_column(Integer, ForeignKey('vehicles.id'), nullable=False)
    
    # Insurance details
    insurance_company_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('insurance_companies.id'), nullable=True)
    insurance_claim_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_insurance_claim: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Estimate details
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estimated_completion_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Status workflow
    status: Mapped[str] = mapped_column(String(20), default='pending')  # pending, approved, rejected
    approved_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Totals (calculated)
    parts_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal('0.00'))
    labour_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal('0.00'))
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal('0.00'))
    grand_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal('0.00'))
    
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer: Mapped["Customer"] = relationship('Customer')
    vehicle: Mapped["Vehicle"] = relationship('Vehicle')
    insurance_company: Mapped[Optional["InsuranceCompany"]] = relationship('InsuranceCompany')
    parts: Mapped[List["EstimatePart"]] = relationship('EstimatePart', cascade='all, delete-orphan', back_populates='estimate')
    labour_items: Mapped[List["EstimateLabour"]] = relationship('EstimateLabour', cascade='all, delete-orphan', back_populates='estimate')
    creator: Mapped["User"] = relationship('User', foreign_keys=[created_by])
    approver: Mapped[Optional["User"]] = relationship('User', foreign_keys=[approved_by])
    
    def calculate_totals(self):
        """Calculate and update all totals"""
        self.parts_total = sum(part.total_price for part in self.parts) if self.parts else Decimal('0.00')
        self.labour_total = sum(labour.total_cost for labour in self.labour_items) if self.labour_items else Decimal('0.00')
        self.tax_amount = (self.parts_total + self.labour_total) * Decimal('0.10')
        self.grand_total = self.parts_total + self.labour_total + self.tax_amount
    
    def to_dict(self, include_details=False):
        """Convert estimate to dictionary"""
        data = {
            'id': self.id,
            'estimate_number': self.estimate_number,
            'customer_id': self.customer_id,
            'vehicle_id': self.vehicle_id,
            'insurance_company_id': self.insurance_company_id,
            'insurance_claim_number': self.insurance_claim_number,
            'is_insurance_claim': self.is_insurance_claim,
            'description': self.description,
            'estimated_completion_date': self.estimated_completion_date.isoformat() if self.estimated_completion_date else None,
            'status': self.status,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'rejection_reason': self.rejection_reason,
            'parts_total': float(self.parts_total),
            'labour_total': float(self.labour_total),
            'tax_amount': float(self.tax_amount),
            'grand_total': float(self.grand_total),
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_details:
            data['customer'] = self.customer.to_dict() if self.customer else None
            data['vehicle'] = self.vehicle.to_dict() if self.vehicle else None
            data['insurance_company'] = self.insurance_company.to_dict() if self.insurance_company else None
            data['parts'] = [part.to_dict() for part in self.parts]
            data['labour_items'] = [labour.to_dict() for labour in self.labour_items]
            data['creator'] = self.creator.to_dict() if self.creator else None
            data['approver'] = self.approver.to_dict() if self.approver else None
        
        return data
    
    def __repr__(self):
        return f'<Estimate {self.estimate_number}>'


class EstimatePart(db.Model):
    """Estimate part model"""
    __tablename__ = 'estimate_parts'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    estimate_id: Mapped[int] = mapped_column(Integer, ForeignKey('estimates.id'), nullable=False)
    part_name: Mapped[str] = mapped_column(String(200), nullable=False)
    part_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    estimate: Mapped["Estimate"] = relationship('Estimate', back_populates='parts')
    
    def to_dict(self):
        """Convert estimate part to dictionary"""
        return {
            'id': self.id,
            'estimate_id': self.estimate_id,
            'part_name': self.part_name,
            'part_number': self.part_number,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'total_price': float(self.total_price),
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<EstimatePart {self.part_name}>'


class EstimateLabour(db.Model):
    """Estimate labour model"""
    __tablename__ = 'estimate_labour'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    estimate_id: Mapped[int] = mapped_column(Integer, ForeignKey('estimates.id'), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    hours: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    hourly_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    estimate: Mapped["Estimate"] = relationship('Estimate', back_populates='labour_items')
    
    def to_dict(self):
        """Convert estimate labour to dictionary"""
        return {
            'id': self.id,
            'estimate_id': self.estimate_id,
            'description': self.description,
            'hours': float(self.hours),
            'hourly_rate': float(self.hourly_rate),
            'total_cost': float(self.total_cost),
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<EstimateLabour {self.description}>'
