from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from app.schemas import CartItem
from app.service import fetch_products_and_combos, generate_bill

router = APIRouter(
    tags=["Platform"],
)

@router.get("/api/v1/products/")
def products_with_offers(db: Session = Depends(get_db)):
    product_and_combos = fetch_products_and_combos(db)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": True, "products_and_combos": product_and_combos},
    )

@router.post("/api/v1/calculate_total/")
def calculate_total(cart: List[CartItem], db: Session = Depends(get_db)):
    try:
        cart_dict = {item.id: item.quantity for item in cart}

        invoice_info = generate_bill(cart_dict, db)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": True, **invoice_info},
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"status": False, "message": str(e)}
        )
