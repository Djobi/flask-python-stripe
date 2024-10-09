import os
import stripe
import json
import boto3

import smtplib

from flask import Flask, render_template, jsonify, request, url_for, redirect
from flask_mail import Mail, Message
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from waitress import serve

load_dotenv()
# load_dotenv(find_dotenv())

# app = Flask(__name__)
# stripe.api_version = '2024-06-20'
# stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# For sample support and debugging, not required for production:
stripe.set_app_info(
    'stripe-samples/your-sample-name',
    version='0.0.1',
    url='https://github.com/stripe-samples')

stripe.api_version = '2024-06-20'
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
static_dir = str(os.path.abspath(os.path.join(__file__ , "..", os.getenv("STATIC_DIR"))))
# app = Flask(__name__, static_folder=static_dir, static_url_path="", template_folder=static_dir)
app = Flask(__name__, static_folder='../client', static_url_path="", template_folder='../client')


# app.config['SECRET_KEY'] = "tsfyguaistyatuis589566875623568956"
app.config['MAIL_SERVER'] = "smtp.googlemail.com"
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "georges.abitbole.08@gmail.com"
app.config['MAIL_PASSWORD'] = "jrcsxerssivbrkfp"
mail = Mail(app)


# @app.route('/')
@app.route('/', methods=['GET'])
def get_root():
    return render_template('index.html')


# 1. Define the file to store membership data
members_file = 'members.json'

#--------------------------
# Modifs 1 - 8.10.24 ...
# Function to load members from the file
# def load_members():
#    if os.path.exists(members_file):
#        with open(members_file, 'r') as file:
#            return json.load(file)
#    else:
#        return []

# Function to save members to the file
#def save_members(members):
#    with open(members_file, 'w') as file:
#        json.dump(members, file, indent=4)
#
# End modifs 1 ...


# Modifs 2 - 8.10.2024 - Modifying the load_members() and save_members() functions to interact with S3. 
s3 = boto3.client('s3')
BUCKET_NAME = 'pdci-uploading-files'    # Replace with your S3 bucket name
S3_FILE_KEY = 'members.json'      # The name of the file in your S3 bucket

# Download the file from S3 and load the members
def load_members():
    try:
        # Download the file from S3
        s3.download_file(BUCKET_NAME, S3_FILE_KEY, '/tmp/members.json')

        # Load members from the local temporary file
        with open('/tmp/members.json', 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading members: {e}")
        return []  # Return an empty list if the file doesn't exist

# Save the members back to S3
def save_members(members):
    try:
        # Save the members to a temporary file
        with open('/tmp/members.json', 'w') as file:
            json.dump(members, file, indent=4)

        # Upload the file back to S3
        s3.upload_file('/tmp/members.json', BUCKET_NAME, S3_FILE_KEY)
    except Exception as e:
        print(f"Error saving members: {e}")

# End Modifs 2 8.10.2024
#-------------------------
# Function to send the receipt to registered Members goes here ...
def send_receipt_email(msg): 
        try:
            mail.send(msg)
            return "Email sent..."
        except Exception as e:
            print(e)
            return f"the email was not sent {e}"
# --> End1



# 2. @app.route('/submit', methods=['POST'])
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    # if request.method == 'POST': 
    # Save Registered members, prepare the receipt, update total members, redirect to /payment_page
    
    msg_district = request.form['district']
    msg_delegation = request.form['delegation']
    msg_membershipline = request.form['membership_line']

     
    msg_title = request.form['title']
    msg_lname = request.form['last-name']
    msg_fname = request.form['first-name']
    msg_dob = request.form['dob']
    msg_adherentnumber = request.form['adherent-number']
    msg_elector_number = request.form['elector-number']
    msg_email = request.form['email']
    msg_phone = request.form['phone']
    msg_address = request.form['address']
    msg_postal_code = request.form['postal-code']
    msg_city = request.form['city']
    msg_country = request.form['country']
    msg_membership_date = request.form['membership-date']
    msg_amount = request.form['total-amount']

    sender = "noreply@app.com"
    msg = Message(msg_title,sender=sender,recipients=[msg_email])
    msg_body = """
    Bienvenu(e) au PDCI-RDA! Nous sommes ravis de confirmer votre adhésion et de vous accueillir au sein de notre Parti. Ceci est votre reçu d'adhésion. Merci de bien le conserver...
    """
    msg.body = " "
    data = {
        # 'app_logo': img_data,
        'district': msg_district,
        'delegation': msg_delegation,
        'membership_line': msg_membershipline,
        'app_name': "PDCI-RDA",
        'title': msg_title,
        'lastname': msg_lname,
        'firstname':msg_fname,        
        'bday':msg_dob,
        'adhenum':msg_adherentnumber,
        'elecnum':msg_elector_number,
        'email':msg_email,
        'phone':msg_phone,
        'address':msg_address,
        'zipcode':msg_postal_code, 
        'city':msg_city, 
        'country':msg_country,
        'dadhes':msg_membership_date,
        'amount': msg_amount,
        'body': msg_body,
    }


    msg.html = render_template("email.html", data=data)

    new_member = { 
        'title': request.form['title'],
        'last_name': request.form['last-name'],
        'first_name': request.form['first-name'],
        'adherent_number': request.form['adherent-number'],
        'elector_number': request.form['elector-number'],
        'profession': request.form['profession'],
        'dob': request.form['dob'],
        'admin_piece': request.form['admin-piece'],
        'issue_date': request.form['issue-date'],
        'email': request.form['email'],
        'phone': request.form['phone'],
        'address': request.form['address'],
        'postal_code': request.form['postal-code'],
        'city': request.form['city'],
        'country': request.form['country'],
        'region': request.form['region'],
        'membership_date': request.form['membership-date'], 
        'district': request.form['district'],           
        'delegation': request.form['delegation'],
        'membership_line': request.form['membership_line'],
        'section': request.form['section'],
        'organe_Parti': request.form['orga'],
        'association': request.form['asso'],
        'total_amount': request.form['total-amount']
    }

    members = load_members()
    members.append(new_member)
    save_members(members)
    
    send_receipt_email(msg)
    
    return jsonify(success=True)
# --> end2


# 3.Normal Flow inmplementation ...
# Route to handle form submission
# @app.route('/membershipForm', methods=['POST'])
@app.route('/submit_form', methods=['POST'])
def submit_form():
    # Get the form data (selected membership line, donation, total amount, etc.)

    selected_membership_line = request.form['membership_line']
    global_total_amount = request.form['total-amount']

    name = request.form['last-name']
    email = request.form['email']
    amount = int(request.form['total-amount'])  # Stripe works in cents
    country = request.form['country']

    # Redirect to the payment page (stripeFinal equivalent)
    return redirect(url_for('payment_page', membershipLine = selected_membership_line, amount=amount, email=email, name=name, country=country))



# Route to display the payment page
@app.route('/payment_page')
def payment_page():
    
    print('I am rendering the Payment Page now ...')
    
    membershipline = request.args.get('membershipLine') 
    amount = request.args.get('amount')
    email = request.args.get('email')
    name = request.args.get('name')
    country = request.args.get('country')

    return render_template('payment_page.html', membershipline= membershipline, amount=amount, email=email, name=name, country=country)



@app.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    data = request.json
       
    print('10. Creating Payment Intent - Here is the amount:', data['amount'])

    amount = (data['amount'])[0:len(data['amount']) -5 ]
    iamount = int(amount) * 100     # Stripe accepts amounts in cents

    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    country = data['country']

    payment_intent = stripe.PaymentIntent.create(
        amount=iamount,
        currency='eur',
        automatic_payment_methods={'enabled': True},
        metadata={
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'country': country
        }
    )
    return jsonify({'clientSecret': payment_intent.client_secret})

# --> end 3



@app.route('/total_members', methods=['GET'])
def total_members():
    members = load_members()
    return jsonify(total_members=len(members))



@app.route('/config', methods=['GET'])
def get_config():
    return jsonify({
        'publishableKey': os.getenv('STRIPE_PUBLISHABLE_KEY')
    })



# @app.route('/success')
#def payment_success():
#    return "Payment succeeded! Thank you for your purchase."


# Modif - 27.09.2024 TDL ...
@app.route('/payment_success', methods=['POST'])
def payment_success():
    # Here, you would confirm the payment using Stripe's API, or simply handle a webhook from Stripe
    # After payment is confirmed, prepare the membership receipt and send it
    # Save Registered members, prepare the receipt, update total members ...

    # msg_email = request.form['email']  # Get the email of the member
    # msg_title = "Receipt for Your PDCI-RDA Membership"
    msg_subject = "Receipt for Your PDCI-RDA Membership"

    
    msg_district = request.form['district']
    msg_delegation = request.form['delegation']
    msg_membershipline = request.form['membership_line']     
    msg_title = request.form['title']
    msg_lname = request.form['last-name']
    msg_fname = request.form['first-name']
    msg_dob = request.form['dob']
    msg_adherentnumber = request.form['adherent-number']
    msg_elector_number = request.form['elector-number']
    msg_email = request.form['email']
    msg_phone = request.form['phone']
    msg_address = request.form['address']
    msg_postal_code = request.form['postal-code']
    msg_city = request.form['city']
    msg_country = request.form['country']
    msg_membership_date = request.form['membership-date']
    msg_amount = request.form['total-amount']

    sender = "noreply@app.com"
    msg = Message(msg_title,sender=sender,recipients=[msg_email])
    msg_body = """
    Bienvenu(e) au PDCI-RDA! Nous sommes ravis de confirmer votre adhésion et de vous accueillir au sein de notre Parti. Ceci est votre reçu d'adhésion. Merci de bien le conserver...
    """
    msg.body = " "
    data = {
        # 'app_logo': img_data,
        'district': msg_district,
        'delegation': msg_delegation,
        'membership_line': msg_membershipline,
        'app_name': "PDCI-RDA",
        'title': msg_title,
        'lastname': msg_lname,
        'firstname':msg_fname,        
        'bday':msg_dob,
        'adhenum':msg_adherentnumber,
        'elecnum':msg_elector_number,
        'email':msg_email,
        'phone':msg_phone,
        'address':msg_address,
        'zipcode':msg_postal_code, 
        'city':msg_city, 
        'country':msg_country,
        'dadhes':msg_membership_date,
        'amount': msg_amount,
        'body': msg_body,
    }


    msg.html = render_template("email.html", data=data)

    new_member = { 
        'title': request.form['title'],
        'last_name': request.form['last-name'],
        'first_name': request.form['first-name'],
        'adherent_number': request.form['adherent-number'],
        'elector_number': request.form['elector-number'],
        'profession': request.form['profession'],
        'dob': request.form['dob'],
        'admin_piece': request.form['admin-piece'],
        'issue_date': request.form['issue-date'],
        'email': request.form['email'],
        'phone': request.form['phone'],
        'address': request.form['address'],
        'postal_code': request.form['postal-code'],
        'city': request.form['city'],
        'country': request.form['country'],
        'region': request.form['region'],
        'membership_date': request.form['membership-date'], 
        'district': request.form['district'],           
        'delegation': request.form['delegation'],
        'membership_line': request.form['membership_line'],
        'section': request.form['section'],
        'organe_Parti': request.form['orga'],
        'association': request.form['asso'],
        'total_amount': request.form['total-amount']
    }
    
    # Save the new member to the database or file
    members = load_members()
    members.append(new_member)
    save_members(members)

    # send_receipt_email(msg_email, msg_subject)
    send_receipt_email(msg)
    
    return jsonify({"success": True})
# End Modif 27.09.2024




@app.route('/failure')
def payment_failure():
    return "Payment failed. Please try again or contact support."



@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        return 'Invalid signature', 400

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']

        send_email(
            "Payment Successful",
            payment_intent['metadata']['email'],
            f"Dear {payment_intent['metadata']['first_name']} {payment_intent['metadata']['last_name']},\n\n"
            f"Thank you for your payment of {payment_intent['amount_received']/100:.2f} EUR."
        )

    return 'Success', 200


# Modif - 26.09.2024 TDL ....
# @app.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():

    print('Payment')
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return jsonify(success=False), 400
    
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify(success=False), 400
    

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        email = payment_intent['receipt_email']
        
        # Send receipt email and save membership
        send_receipt_email(email, "Your Membership Receipt")

        # Add logic to save the member here

    return jsonify(success=True), 200

# End Modif 26.09.2024



if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=4242)
