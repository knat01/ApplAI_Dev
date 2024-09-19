import streamlit as st
import stripe
from firebase_admin import firestore
from config import STRIPE_API_KEY

stripe.api_key = STRIPE_API_KEY
db = firestore.client()

def show_upgrade_options():
    st.subheader("Upgrade Your Plan")
    
    user_id = st.session_state.user['uid']
    user_doc = db.collection('users').document(user_id).get()
    user_data = user_doc.to_dict()
    
    current_plan = user_data.get('plan', 'Free')
    applications_count = user_data.get('applications_count', 0)
    
    st.write(f"Current Plan: {current_plan}")
    st.write(f"Applications Submitted: {applications_count}")
    
    if current_plan == 'Free' and applications_count >= 25:
        st.warning("You've reached the limit of free applications. Please upgrade to continue.")
    
    plans = {
        'Pro': {'price': 9.99, 'applications': 'Unlimited'},
        'Enterprise': {'price': 19.99, 'applications': 'Unlimited + Priority Support'}
    }
    
    selected_plan = st.selectbox("Select a Plan to Upgrade", list(plans.keys()))
    
    st.write(f"Price: ${plans[selected_plan]['price']}/month")
    st.write(f"Applications: {plans[selected_plan]['applications']}")
    
    if st.button("Upgrade Now"):
        try:
            # Create Stripe Checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(plans[selected_plan]['price'] * 100),
                        'product_data': {
                            'name': f'{selected_plan} Plan',
                        },
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url='https://yourdomain.com/success',
                cancel_url='https://yourdomain.com/cancel',
            )
            
            # Update user's plan in Firestore
            db.collection('users').document(user_id).update({
                'plan': selected_plan,
                'stripe_customer_id': checkout_session.customer
            })
            
            # Redirect to Stripe Checkout
            st.markdown(f"<a href='{checkout_session.url}' target='_blank'>Click here to complete your payment</a>", unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

def check_subscription_status(user_id):
    user_doc = db.collection('users').document(user_id).get()
    user_data = user_doc.to_dict()
    
    if 'stripe_customer_id' in user_data:
        try:
            customer = stripe.Customer.retrieve(user_data['stripe_customer_id'])
            subscriptions = stripe.Subscription.list(customer=customer.id, limit=1)
            
            if subscriptions.data:
                subscription = subscriptions.data[0]
                if subscription.status == 'active':
                    return True
            
        except stripe.error.StripeError as e:
            st.error(f"An error occurred while checking subscription status: {str(e)}")
    
    return False
