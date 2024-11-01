import stripe
import logging
from config import STRIPE_API_KEY, PRODUCT_ID

stripe.api_key = STRIPE_API_KEY


async def create_customer(telegram_id: int, first_name: str, last_name: str = None, username: str = None):
  existing_customers = stripe.Customer.list(limit=100)
  for customer in existing_customers.auto_paging_iter():
    if customer.metadata.get("telegram_id") == str(telegram_id):
      return customer  
  
  name = f"{first_name} {last_name}" if last_name else first_name
  description_parts = [f"Telegram user ID: {telegram_id}"]
  if username:
    description_parts.append(f"username: @{username}")
  description = " | ".join(description_parts) 
  
  customer = stripe.Customer.create(
    name=name,
    description=description,
    metadata={
      "telegram_id": telegram_id,
      "telegram_username": username or "",
      "first_name": first_name,
      "last_name": last_name or ""
    }
  )
  return customer

  

async def get_prices():
  prices = stripe.Price.list(product=PRODUCT_ID)
  active_prices = [
  {
    "price_id": price["id"],
    "interval": price["recurring"]["interval"],
    "amount": f"{price['unit_amount'] / 100:.2f}",
    "currency": price["currency"].upper()
  }
  for price in prices["data"] if price["active"]
  ]
  return active_prices


async def create_checkout_session(customer_id: str, price_id: str):
  session = stripe.checkout.Session.create(
    payment_method_types=["card"],
    mode="subscription",
    customer=customer_id,
    line_items=[
      {"price": price_id, "quantity": 1},
      ],
    success_url=f"https://t.me/+J3wswkYhjdtkMjY0",
    cancel_url=f"https://t.me/AtasSubscriptionbot",
  )
  return session.url  

