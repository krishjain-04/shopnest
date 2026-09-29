from io import BytesIO

from django.core.mail import EmailMessage
from django.conf import settings

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def generate_invoice_pdf(order):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Title'],
        alignment=TA_CENTER,
        fontSize=24,
        spaceAfter=20,
    )

    right_style = ParagraphStyle(
        'Right',
        parent=styles['Normal'],
        alignment=TA_RIGHT,
    )

    story = []

    # Shop name
    story.append(Paragraph("SHOPNEST", title_style))
    story.append(Paragraph("E-commerce Invoice", styles['Heading2']))
    story.append(Spacer(1, 10))

    # Order information
    order_info = [
        ["Order ID", order.order_id],
        ["Order Date", order.created_at.strftime("%d %B %Y, %I:%M %p")],
        ["Payment Method", order.payment_method],
        ["Payment Status", order.payment_status],
        ["Order Status", order.status],
    ]

    order_table = Table(order_info, colWidths=[120, 350])

    order_table.setStyle(
        TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('PADDING', (0, 0), (-1, -1), 7),
        ])
    )

    story.append(order_table)
    story.append(Spacer(1, 20))

    # Customer
    story.append(Paragraph("Customer Details", styles['Heading2']))
    story.append(
        Paragraph(
            f"<b>Name:</b> {order.address.full_name}<br/>"
            f"<b>Email:</b> {order.user.email}<br/>"
            f"<b>Phone:</b> {order.address.phone}<br/>"
            f"<b>Address:</b> {order.address.address_line}<br/>"
            f"{order.address.landmark or ''}<br/>"
            f"{order.address.city}, {order.address.state} - "
            f"{order.address.pincode}",
            styles['Normal']
        )
    )

    story.append(Spacer(1, 20))

    # Products
    story.append(Paragraph("Order Items", styles['Heading2']))

    data = [
        ["Product", "Qty", "Price", "Subtotal"]
    ]

    items = order.items.select_related('product').all()

    for item in items:
        data.append([
            item.product.name,
            str(item.quantity),
            f"₹{item.price}",
            f"₹{item.subtotal}",
        ])

    data.append([
        "",
        "",
        "Total",
        f"₹{order.total_amount}",
    ])

    items_table = Table(
        data,
        colWidths=[250, 50, 90, 90]
    )

    items_table.setStyle(
        TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#212529')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),

            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),

            ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),

            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),

            ('PADDING', (0, 0), (-1, -1), 7),
        ])
    )

    story.append(items_table)
    story.append(Spacer(1, 25))

    story.append(
        Paragraph(
            "Thank you for shopping with SHOPNEST!",
            ParagraphStyle(
                'ThankYou',
                parent=styles['Normal'],
                alignment=TA_CENTER,
                fontSize=11,
            )
        )
    )

    doc.build(story)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf


def send_invoice_email(order):
    pdf = generate_invoice_pdf(order)

    customer_email = order.user.email

    if not customer_email:
        return False

    subject = f"SHOPNEST - Invoice for Order {order.order_id}"

    message = f"""
Hello {order.address.full_name},

Thank you for shopping with SHOPNEST.

Your order {order.order_id} has been placed successfully.

Total Amount: ₹{order.total_amount}

Your invoice is attached to this email.

Thank you,
SHOPNEST Support
"""

    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[customer_email],
    )

    email.attach(
        f"invoice_{order.order_id}.pdf",
        pdf,
        "application/pdf",
    )

    email.send(fail_silently=True)

    return True