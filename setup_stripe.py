"""
Script de configuración de Stripe — Ejecutar UNA sola vez
Crea los productos Basic y Pro en Stripe y muestra los price_ids

Uso:
    python setup_stripe.py
"""

import stripe

stripe.api_key = "sk_test_51TBOC9A4vEOorl34R1Iq6eGnHDRCNkumVURxSOQvJPp4kUm79UZ7ZATYFv7CyuyUpGC5tZ5m7mKefB3K2VQnCciE00ZITQm38O"

print("Creando productos en Stripe...")

# ── Basic Plan ──
product_basic = stripe.Product.create(
    name="Script & Shorts Studio — Basic",
    description="50 scripts al mes para creadores de contenido",
)
price_basic = stripe.Price.create(
    product=product_basic.id,
    unit_amount=1900,
    currency="usd",
    recurring={"interval": "month"},
)
print(f"\n✅ Plan Basic creado")
print(f"   Product ID: {product_basic.id}")
print(f"   Price ID:   {price_basic.id}")

# ── Pro Plan ──
product_pro = stripe.Product.create(
    name="Script & Shorts Studio — Pro",
    description="Scripts ilimitados para creadores profesionales",
)
price_pro = stripe.Price.create(
    product=product_pro.id,
    unit_amount=3900,
    currency="usd",
    recurring={"interval": "month"},
)
print(f"\n✅ Plan Pro creado")
print(f"   Product ID: {product_pro.id}")
print(f"   Price ID:   {price_pro.id}")

print("\n" + "="*50)
print("Agrega estas líneas a tu archivo .env:")
print("="*50)
print(f"STRIPE_BASIC_PRICE_ID={price_basic.id}")
print(f"STRIPE_PRO_PRICE_ID={price_pro.id}")
print(f"STRIPE_PUBLISHABLE_KEY=pk_test_51TBOC9A4vEOorl34Tkc7xgwaKsWcovjdw71mxMyQin8bWVLEF1t6XcMpyNKQOEWHsM5lDJTDUEmLbATsgCDqsUEb006l782WJ5")
print(f"STRIPE_SECRET_KEY=sk_test_51TBOC9A4vEOorl34R1Iq6eGnHDRCNkumVURxSOQvJPp4kUm79UZ7ZATYFv7CyuyUpGC5tZ5m7mKefB3K2VQnCciE00ZITQm38O")
print("="*50)
