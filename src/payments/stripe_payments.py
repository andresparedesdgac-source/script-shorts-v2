"""
Módulo de pagos con Stripe — Assets Solutions AI
Proyecto 02: Script + Shorts Studio
"""

import os
import stripe

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_BASIC_PRICE_ID = os.getenv("STRIPE_BASIC_PRICE_ID", "")
STRIPE_PRO_PRICE_ID = os.getenv("STRIPE_PRO_PRICE_ID", "")

stripe.api_key = STRIPE_SECRET_KEY

PLANES = {
    "free":  {"nombre": "Free",  "precio": 0,  "scripts_limit": 3,   "price_id": None},
    "basic": {"nombre": "Basic", "precio": 19, "scripts_limit": 50,  "price_id": STRIPE_BASIC_PRICE_ID},
    "pro":   {"nombre": "Pro",   "precio": 39, "scripts_limit": 999, "price_id": STRIPE_PRO_PRICE_ID},
}

def crear_checkout_session(plan: str, usuario_id: str, usuario_email: str, app_url: str = "http://localhost:8501") -> str:
    info_plan = PLANES.get(plan)
    if not info_plan or not info_plan["price_id"]:
        raise ValueError(f"Plan {plan} no configurado o sin price_id")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{"price": info_plan["price_id"], "quantity": 1}],
        customer_email=usuario_email,
        metadata={"user_id": usuario_id, "plan": plan},
        success_url=f"{app_url}?pago=exitoso&plan={plan}",
        cancel_url=f"{app_url}?pago=cancelado",
    )
    return session.url

def verificar_suscripcion(stripe_sub_id: str) -> dict:
    try:
        sub = stripe.Subscription.retrieve(stripe_sub_id)
        return {"status": sub.status, "plan": sub.metadata.get("plan", "basic")}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def cancelar_suscripcion(stripe_sub_id: str) -> bool:
    try:
        stripe.Subscription.modify(stripe_sub_id, cancel_at_period_end=True)
        return True
    except Exception:
        return False
