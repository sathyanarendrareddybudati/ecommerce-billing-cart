from fastapi import FastAPI, status
from sqlalchemy.orm import Session
from app import models
from config.database import SessionLocal, engine
from constants import frontend_base_url
from fastapi.responses import JSONResponse
from app.controller import router as supermarket_router
from fastapi.middleware.cors import CORSMiddleware
from config.database import Base

app = FastAPI()

app = FastAPI(title="SuperMarket", openapi_url=None, docs_url=None, redoc_url=None)
app.include_router(supermarket_router)

origins = [
    frontend_base_url
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def add_initial_data(db: Session):
    initial_products = [
        {"sku": "A", "price": 50},
        {"sku": "B", "price": 30},
        {"sku": "C", "price": 20},
        {"sku": "D", "price": 15},
    ]
    initial_combo = [
        {"product_id": 1, "quantity": 3, "price": 130},
        {"product_id": 2, "quantity": 2, "price": 45},
    ]
    for product in initial_products:
        db_product = db.query(models.Product).filter(models.Product.sku == product["sku"]).first()
        if not db_product:
            new_product = models.Product(**product)
            db.add(new_product)
            
    for combo in initial_combo:
        db_combo = db.query(models.Combo).filter(
            models.Combo.product_id == combo["product_id"],
            models.Combo.quantity == combo["quantity"],
        ).first()
        if not db_combo:
            new_combo = models.Combo(**combo)
            db.add(new_combo)
    db.commit()


@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    add_initial_data(db)
    db.close()


@app.get("/api/v1/health")
async def health():
    context = {"status": True, "message": "state healthy"}
    return JSONResponse(status_code=status.HTTP_200_OK, content=context)