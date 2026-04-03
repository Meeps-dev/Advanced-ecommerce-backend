from sqlalchemy.orm import Session, joinedload
from app.modules.cart.infrastructure.models.cart import Cart
from app.modules.cart.infrastructure.models.cart_item import CartItem


class CartRepository:

    def __init__(self, db: Session):
        self.db = db



    from sqlalchemy.orm import joinedload

    def get_cart_by_user(self, user_id: int):
         """Fetch cart with related items/products to avoid N+1 queries."""
         return self.db.query(Cart).options(
        joinedload(Cart.items).joinedload(CartItem.product),
        joinedload(Cart.user)  # 🔥 NEW: Load the user object too
    ).filter(Cart.user_id == user_id).first()



    def create_cart(self, user_id: int):

        cart = Cart(user_id=user_id)

        self.db.add(cart)
        self.db.flush()

        return cart
    


    def get_cart_item(self, cart_id: int, product_id: int):

        return self.db.query(CartItem).filter(
            CartItem.cart_id == cart_id,
            CartItem.product_id == product_id
        ).first()
    


    def create_cart_item(self, cart_id: int, product_id: int, quantity: int):

        item = CartItem(
            cart_id=cart_id,
            product_id=product_id,
            quantity=quantity
        )

        self.db.add(item)

        return item
    

    
    # --- GET CART BY ID ---
    def get_cart_by_id(self, cart_id: int):
        """
        Optimized to fetch the cart, all its items, and the product 
        details in a single database round-trip.
        """
        return self.db.query(Cart).options(
            joinedload(Cart.items).joinedload(CartItem.product)
        ).filter(
            Cart.id == cart_id
        ).first()


    def update_cart_item(self, item: CartItem, quantity: int):

        item.quantity = quantity

        return item
    


    def clear_cart(self, cart: Cart):

        self.db.query(CartItem).filter(
            CartItem.cart_id == cart.id
        ).delete()


    def remove_cart_item(self, cart_id: int, product_id: int):
        """
        Deletes a specific product from a specific cart.
        """
        self.db.query(CartItem).filter(
            CartItem.cart_id == cart_id,
            CartItem.product_id == product_id
        ).delete()
