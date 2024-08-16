import React, { useState, useEffect } from "react";
import axios from "axios";
import ProductCard from "../../components/ProductCard";
import "./Cart.css";

function Cart() {
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [total, setTotal] = useState(null);
  const [invoice, setInvoice] = useState(null);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await axios.get(
        process.env.REACT_APP_BACKEND_BASE_URL + "/products/"
      );
      setProducts(response.data.products_and_combos);
    } catch (error) {
      console.error("There was an error fetching products!", error);
    }
  };

  const addItemToCart = (product_id, sku, quantity) => {
    setCart((prevCart) => {
      const itemIndex = prevCart.findIndex(
        (cartItem) => cartItem.id === product_id
      );
      if (itemIndex >= 0) {
        const updatedCart = [...prevCart];
        updatedCart[itemIndex] = {
          ...updatedCart[itemIndex],
          quantity: updatedCart[itemIndex].quantity + quantity,
        };
        return updatedCart;
      } else {
        return [...prevCart, { id: product_id, sku: sku, quantity: quantity }];
      }
    });
  };

  const removeItemFromCart = (product_id, quantity) => {
    setCart((prevCart) => {
      const itemIndex = prevCart.findIndex(
        (cartItem) => cartItem.id === product_id
      );
      if (itemIndex >= 0) {
        const updatedCart = [...prevCart];
        if (updatedCart[itemIndex].quantity > quantity) {
          updatedCart[itemIndex] = {
            ...updatedCart[itemIndex],
            quantity: updatedCart[itemIndex].quantity - quantity,
          };
        } else {
          updatedCart.splice(itemIndex, 1);
        }
        return updatedCart;
      }
      return prevCart;
    });
  };

  useEffect(() => {
    calculateTotal();
  }, [cart]);

  const calculateTotal = async () => {
    try {
      const response = await axios.post(
        process.env.REACT_APP_BACKEND_BASE_URL + "/calculate_total/",
        cart
      );
      setTotal(response.data.total);
      setInvoice(response.data.invoice);
    } catch (error) {
      console.error("There was an error calculating the total!", error);
    }
  };

  function invoiceCalculation(item) {
    let combo_calculation = '';
    let unit_calculation = '';

    if (item.combo_quantity > 0) {
      combo_calculation += `${item.combo_price} * ${item.combo_quantity}`;
    }
    
    const remainingQuantity = item.quantity - item.combo_quantity * item.combo_item_count;
    if (remainingQuantity !== 0) {
      unit_calculation += `${item.price_per_item} * ${remainingQuantity}`;
    }
  
    return combo_calculation && unit_calculation? combo_calculation + ' + ' + unit_calculation: combo_calculation+unit_calculation;
  }

  return (
    <div className="cart-container">
      <div className="cart-product-list">
        <h2>Products</h2>
        <div className="cart-product-cards">
          {products.map((product, index) => (
            <ProductCard
              key={index}
              product={product.product}
              offers={product.combos}
              addItemToCart={addItemToCart}
              removeItemFromCart={removeItemFromCart}
            />
          ))}
        </div>
      </div>
      <div className="cart-items-container">
        <div>
          <h2>Cart</h2>
          <div className="cart-table-container">
            <table className="cart-table">
              <thead>
                <tr>
                  <th>Item</th>
                  <th>Quantity</th>
                </tr>
              </thead>
              <tbody>
                {cart.map((cartItem, index) => (
                  <tr key={index}>
                    <td>{cartItem.sku}</td>
                    <td>{cartItem.quantity}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        <div className="cart-footer">
          {invoice && (
            <div>
              <table className="invoice-table">
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Quantity</th>
                    <th>Price per Item</th>
                    <th>Combo Applied</th>
                    <th>Combo Price</th>
                    <th>Total Cost</th>
                    <th>Calculation Breakdown</th>
                  </tr>
                </thead>
                <tbody>
                  {invoice.map((item, index) => (
                    <tr key={index}>
                      <td>{item.product_sku}</td>
                      <td>{item.quantity}</td>
                      <td>{item.price_per_item}</td>
                      <td>{item.combo_quantity ? "Yes" : "No"}</td>
                      <td>{item.combo_price}</td>
                      <td>{item.total_cost}</td>
                      <td>
                       {invoiceCalculation(item)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {total !== null && <h2>Total: Rs {total}</h2>}
        </div>
      </div>
    </div>
  );
}

export default Cart;
