"""
Webhook de Stripe — Assets Solutions AI
Proyecto 02: Script + Shorts Studio

Recibe notificaciones de Stripe y actualiza el plan del usuario en Supabase.
Corre como servicio separado en Railway.
"""

import os
import stripe
from flask import Flask, request, jsonify
from supabase import create_client

app = Flask(__name__)

# ── Config ──
STRIPE_SECRET_KEY        = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET    = os.getenv("STRIPE_WEBHOOK_SECRET", "")
SUPABASE_URL             = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY     = os.getenv("SUPABASE_SERVICE_KEY", "")

stripe.api_key = STRIPE_SECRET_KEY

PLAN_POR_PRECIO = {
    os.getenv("STRIPE_BASIC_PRICE_ID", ""): "basic",
    os.getenv("STRIPE_PRO_PRICE_ID", ""):   "pro",
}

LIMITES_POR_PLAN = {
    "free":  3,
    "basic": 50,
    "pro":   999,
}


def obtener_supabase():
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def actualizar_plan_usuario(user_id: str, plan: str):
    """Actualiza el plan y límite del usuario en Supabase."""
    supabase = obtener_supabase()
    supabase.table("users").update({
        "plan": plan,
        "scripts_limit": LIMITES_POR_PLAN.get(plan, 3),
        "scripts_used": 0,  # Resetea el contador al cambiar de plan
    }).eq("id", user_id).execute()
    print(f"✅ Plan actualizado: usuario {user_id} → {plan}")


def guardar_suscripcion(user_id: str, stripe_sub_id: str, plan: str, period_end: int):
    """Guarda o actualiza la suscripción en Supabase."""
    supabase = obtener_supabase()
    # Verificar si ya existe
    existing = supabase.table("subscriptions")\
        .select("id")\
        .eq("user_id", user_id)\
        .execute()

    if existing.data:
        supabase.table("subscriptions").update({
            "stripe_sub_id": stripe_sub_id,
            "plan": plan,
            "status": "active",
            "current_period_end": period_end,
        }).eq("user_id", user_id).execute()
    else:
        supabase.table("subscriptions").insert({
            "user_id": user_id,
            "stripe_sub_id": stripe_sub_id,
            "plan": plan,
            "status": "active",
            "current_period_end": period_end,
        }).execute()


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload   = request.data
    sig_header = request.headers.get("Stripe-Signature", "")

    # ── Verificar firma de Stripe ──
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        print("❌ Firma inválida")
        return jsonify({"error": "Invalid signature"}), 400
    except Exception as e:
        print(f"❌ Error construyendo evento: {e}")
        return jsonify({"error": str(e)}), 400

    event_type = event["type"]
    print(f"📨 Evento recibido: {event_type}")

    # ── Pago exitoso — activar plan ──
    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("metadata", {}).get("user_id")
        plan    = session.get("metadata", {}).get("plan", "basic")

        if user_id:
            actualizar_plan_usuario(user_id, plan)
        else:
            print("⚠️ No se encontró user_id en metadata")

    # ── Suscripción renovada ──
    elif event_type == "invoice.payment_succeeded":
        invoice = event["data"]["object"]
        sub_id  = invoice.get("subscription")

        if sub_id:
            sub = stripe.Subscription.retrieve(sub_id)
            user_id  = sub.metadata.get("user_id")
            price_id = sub["items"]["data"][0]["price"]["id"]
            plan     = PLAN_POR_PRECIO.get(price_id, "basic")
            period_end = sub["current_period_end"]

            if user_id:
                actualizar_plan_usuario(user_id, plan)
                guardar_suscripcion(user_id, sub_id, plan, period_end)

    # ── Suscripción cancelada — bajar a Free ──
    elif event_type in ("customer.subscription.deleted", "customer.subscription.updated"):
        sub     = event["data"]["object"]
        user_id = sub.metadata.get("user_id")
        status  = sub.get("status")

        if user_id and status in ("canceled", "unpaid", "past_due"):
            actualizar_plan_usuario(user_id, "free")
            supabase = obtener_supabase()
            supabase.table("subscriptions").update({
                "status": status
            }).eq("user_id", user_id).execute()

    return jsonify({"status": "ok"}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "webhook"}), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
