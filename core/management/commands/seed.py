from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from inventory.models import Category, Supplier, Product, Order, OrderItem, StockMovement
import random
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # Admin user
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@invstock.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created admin user (admin / admin123)'))

        # Demo user
        if not User.objects.filter(username='demo').exists():
            User.objects.create_user('demo', 'demo@invstock.com', 'demo123')
            self.stdout.write(self.style.SUCCESS('Created demo user (demo / demo123)'))

        # Categories
        categories_data = [
            ('Electronics', 'Electronic components and devices'),
            ('Office Supplies', 'Paper, pens, and stationery'),
            ('Furniture', 'Desks, chairs, and storage'),
            ('Food & Beverage', 'Snacks, drinks, and consumables'),
            ('Tools & Equipment', 'Workshop and maintenance tools'),
            ('Clothing', 'Uniforms and workwear'),
        ]
        categories = []
        for name, desc in categories_data:
            cat, _ = Category.objects.get_or_create(name=name, defaults={'description': desc})
            categories.append(cat)
        self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} categories'))

        # Suppliers
        suppliers_data = [
            ('TechSupply Co', 'orders@techsupply.com', '+1-555-0100', 'New York, NY'),
            ('Office World', 'sales@officeworld.com', '+1-555-0200', 'Los Angeles, CA'),
            ('Furniture Plus', 'info@furnitureplus.com', '+1-555-0300', 'Chicago, IL'),
            ('FoodDist Ltd', 'supply@fooddist.com', '+1-555-0400', 'Houston, TX'),
            ('ToolMaster', 'orders@toolmaster.com', '+1-555-0500', 'Phoenix, AZ'),
        ]
        suppliers = []
        for name, email, phone, addr in suppliers_data:
            sup, _ = Supplier.objects.get_or_create(name=name, defaults={'contact_email': email, 'phone': phone, 'address': addr})
            suppliers.append(sup)
        self.stdout.write(self.style.SUCCESS(f'Created {len(suppliers)} suppliers'))

        # Products
        products_data = [
            ('Laptop Dell XPS 15', 'ELEC-001', 0, 0, '1299.99', 12, 5),
            ('Wireless Mouse', 'ELEC-002', 0, 0, '29.99', 85, 20),
            ('USB-C Hub 7-port', 'ELEC-003', 0, 0, '49.99', 45, 15),
            ('Monitor 27" 4K', 'ELEC-004', 0, 0, '449.99', 8, 5),
            ('Mechanical Keyboard', 'ELEC-005', 0, 0, '129.99', 22, 10),
            ('A4 Paper Ream', 'OFFC-001', 1, 1, '8.99', 200, 50),
            ('Blue Ballpoint Pens x10', 'OFFC-002', 1, 1, '4.99', 150, 30),
            ('Stapler Heavy Duty', 'OFFC-003', 1, 1, '24.99', 35, 10),
            ('File Cabinet 4-drawer', 'FURN-001', 2, 2, '299.99', 6, 3),
            ('Ergonomic Chair', 'FURN-002', 2, 2, '399.99', 15, 5),
            ('Standing Desk', 'FURN-003', 2, 2, '549.99', 4, 2),
            ('Coffee Beans 1kg', 'FOOD-001', 3, 3, '19.99', 60, 20),
            ('Mineral Water 24-pack', 'FOOD-002', 3, 3, '12.99', 100, 30),
            ('Power Drill 18V', 'TOOL-001', 4, 4, '89.99', 18, 5),
            ('Safety Goggles', 'TOOL-002', 4, 4, '14.99', 40, 15),
            ('Work Gloves L', 'TOOL-003', 4, 4, '9.99', 7, 10),  # Low stock
            ('Hi-Vis Jacket M', 'CLTH-001', 5, 4, '34.99', 5, 8),  # Low stock
            ('Hard Hat White', 'CLTH-002', 5, 4, '19.99', 3, 5),   # Low stock
        ]
        products = []
        for name, sku, cat_i, sup_i, price, qty, reorder in products_data:
            prod, _ = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': name,
                    'category': categories[cat_i],
                    'supplier': suppliers[min(sup_i, len(suppliers)-1)],
                    'unit_price': Decimal(price),
                    'quantity_in_stock': qty,
                    'reorder_level': reorder,
                    'reorder_quantity': reorder * 5,
                }
            )
            products.append(prod)
        self.stdout.write(self.style.SUCCESS(f'Created {len(products)} products'))

        # Stock movements
        for product in products[:8]:
            for _ in range(3):
                StockMovement.objects.get_or_create(
                    product=product,
                    movement_type=random.choice(['in', 'out', 'in']),
                    quantity=random.randint(5, 50),
                    reference=f"REF-{random.randint(1000,9999)}",
                    defaults={'notes': 'Initial stock movement'}
                )
        self.stdout.write(self.style.SUCCESS('Created stock movements'))

        # Orders
        statuses = ['pending', 'processing', 'completed', 'completed', 'completed']
        for i in range(10):
            order_num = f"ORD-2024-{i+1:04d}"
            if not Order.objects.filter(order_number=order_num).exists():
                order = Order.objects.create(
                    order_number=order_num,
                    order_type=random.choice(['sales', 'purchase']),
                    status=random.choice(statuses),
                    supplier=random.choice(suppliers) if random.random() > 0.5 else None,
                    total_amount=Decimal(str(round(random.uniform(100, 5000), 2))),
                    notes=f'Sample order {i+1}'
                )
                # Add order items
                selected_products = random.sample(products, random.randint(1, 4))
                for p in selected_products:
                    qty = random.randint(1, 20)
                    OrderItem.objects.create(
                        order=order,
                        product=p,
                        quantity=qty,
                        unit_price=p.unit_price,
                    )
        self.stdout.write(self.style.SUCCESS('Created 10 sample orders'))

        self.stdout.write(self.style.SUCCESS('\n=== SEEDING COMPLETE ==='))
        self.stdout.write('Admin login: admin / admin123')
        self.stdout.write('Demo login:  demo / demo123')
