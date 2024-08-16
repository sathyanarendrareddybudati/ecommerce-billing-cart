import React, { useState } from "react";

function ProductCard({ product, offers, addItemToCart, removeItemFromCart }) {
  const [quantity, setQuantity] = useState(1);

  const handleAdd = () => {
    addItemToCart(product.id, product.sku, quantity);
  };

  const handleRemove = () => {
    removeItemFromCart(product.id, quantity);
  };

  const handleQuantityChange = (e) => {
    const newQuantity = parseInt(e.target.value, 10);
    if (newQuantity > 0) {
      setQuantity(newQuantity);
    }
  };

  return (
    <div className="product-card">
      <div className="product-info">
        <h3>{product.sku}</h3>
        <p>Price: Rs {product.price}</p>
        {offers && offers.length > 0
          ? offers.map((offer, index) => (
              <h4 key={index}>
                Buy {offer.quantity} at {offer.price}
              </h4>
            ))
          : null}
      </div>
      <div>
        <div className="product-actions">
          <button onClick={handleAdd} className="product-button">
            +
          </button>
          <input
            type="number"
            value={quantity}
            onChange={handleQuantityChange}
            className="product-quantity-input"
            min="1"
          />
          <button onClick={handleRemove} className="product-button">
            -
          </button>
        </div>
      </div>
    </div>
  );
}

export default ProductCard;
