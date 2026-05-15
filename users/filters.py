from django_filters import rest_framework as filters
from .models import Payment


class PaymentFilter(filters.FilterSet):
    # Фильтр по курсу (точное совпадение)
    course = filters.NumberFilter(field_name="course", lookup_expr="exact")

    # Фильтр по уроку (точное совпадение)
    lesson = filters.NumberFilter(field_name="lesson", lookup_expr="exact")

    # Фильтр по способу оплаты
    payment_method = filters.ChoiceFilter(choices=Payment.PaymentMethod.choices)

    # Фильтр по дате (конкретная дата)
    payment_date = filters.DateFilter(field_name="payment_date", lookup_expr="date")

    # Фильтр по диапазону дат
    payment_date_from = filters.DateFilter(field_name="payment_date", lookup_expr="gte")
    payment_date_to = filters.DateFilter(field_name="payment_date", lookup_expr="lte")

    # Фильтр по пользователю
    user = filters.NumberFilter(field_name="user", lookup_expr="exact")

    # Фильтр по сумме
    amount_min = filters.NumberFilter(field_name="amount", lookup_expr="gte")
    amount_max = filters.NumberFilter(field_name="amount", lookup_expr="lte")

    class Meta:
        model = Payment
        fields = [
            "course",
            "lesson",
            "payment_method",
            "payment_date",
            "payment_date_from",
            "payment_date_to",
            "user",
            "amount_min",
            "amount_max",
        ]
