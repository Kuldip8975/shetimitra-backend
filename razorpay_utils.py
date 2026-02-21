import razorpay

RAZORPAY_KEY_ID = "rzp_test_R9qLSasaJ4bKfi"
RAZORPAY_KEY_SECRET = "VlAZ41FvXVi2Gvioq71gLqVy"

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

def create_razorpay_order(amount):
    order = client.order.create({
        "amount": amount * 100,   # INR → paise
        "currency": "INR",
        "payment_capture": 1
    })
    return order
