from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    """
    Ek single product jo store me bikta hai.
    stock_quantity track karta hai ki abhi kitna maal available hai —
    yehi field baad me analytics.py me demand-score calculate karne
    ke kaam aata hai.
    """
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # naye products sabse upar dikhein

    def __str__(self):
        return self.title

    @property
    def in_stock(self):
        """Quick check — admin panel aur future views me useful hai."""
        return self.stock_quantity > 0


class Order(models.Model):
    """
    Ek customer order. Har order ek user se linked hota hai aur
    ismein multiple OrderItem ho sakte hain (see below).
    """
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    # device_ip optional hai — future me fraud-detection jaisa feature
    # add karna ho to yeh already available rahega
    device_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    """
    Order aur Product ke beech ka join table — ek order ke andar
    multiple products ho sakte hain, alag-alag quantity ke saath.
    price_at_purchase isliye store karte hain kyunki product ka price
    future me badal sakta hai, lekin purani order ki billing history
    change nahi honi chahiye.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"
