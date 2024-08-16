from sqlalchemy import select
from app.models import Product, Combo
from app.helper import to_dict




def fetch_products_and_combos(db):
    stmt = select(Product, Combo).outerjoin(Combo, Product.id == Combo.product_id)
    results = db.execute(stmt).all()

    product_dict = {}
    for product, combo in results:
        product_id = product.id
        if product_id not in product_dict:
            product_dict[product_id] = {"product": to_dict(product), "combos": []}
        if combo:
            product_dict[product_id]["combos"].append(to_dict(combo))

    return [
        {"product": value["product"], "combos": value["combos"]}
        for value in product_dict.values()
    ]


def generate_bill(cart, db):
    total = 0
    invoice = []
    for product_id, quantity in cart.items():
        product = db.query(Product).filter(Product.id == product_id).first()
        combo = db.query(Combo).filter(Combo.product_id == product_id).first()

        if not product:
            raise Exception("Product not found")

        item_total = 0
        applied_combos = 0

        if combo and quantity >= combo.quantity:
            combo_group = quantity // combo.quantity
            remaining_items = quantity % combo.quantity
            item_total += remaining_items * product.price
            item_total += combo_group * combo.price
            applied_combos = combo_group
        else:
            item_total += quantity * product.price

        total += item_total

        invoice.append(
            {
                "product_id": product_id,
                "product_sku": product.sku,
                "quantity": quantity,
                "price_per_item": product.price,
                "combo_quantity": applied_combos,
                "combo_item_count": combo.quantity if combo else 0,
                "combo_price": combo.price if combo else None,
                "total_cost": item_total,
            }
        )
    return {"status": True, "total": total, "invoice": invoice}