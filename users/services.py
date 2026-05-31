import stripe


def create_stripe_product(course):
    """Создаёт продукт в Stripe"""
    product = stripe.Product.create(
        name=course.title,
        description=course.description,
        metadata={"course_id": course.id},
    )
    return product


def create_stripe_price(product_id, amount):
    """Создаёт цену в Stripe (сумма в копейках!)"""
    price = stripe.Price.create(
        product=product_id,
        unit_amount=int(amount * 100),  # рубли → копейки
        currency="rub",
    )
    return price


def create_checkout_session(price_id, success_url, cancel_url):
    """Создаёт сессию оплаты Stripe Checkout"""
    session = stripe.checkout.Session.create(
        success_url=success_url,
        cancel_url=cancel_url,
        payment_method_types=["card"],
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            },
        ],
        mode="payment",
    )
    return session
