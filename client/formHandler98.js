let membershipAmount1 = 0;
let donationAmount1 = 0;
let selectedMembershipLine = ''; // This will store the membership line


/* ----------------------------------------- */
/* The Adhesion button radios part           */
/* ----------------------------------------- */
const options = [
    { label: 'Adhesion ou renouvellement de base', price: 25 },
    { label: 'Adhesion ou renouvellement pour les Cadres & GCR', price: 75 },
    { label: 'Adhesion ou renouvellement pour les membres du Comité des Sages (CS)', price: 153 },
    { label: 'Adhesion ou renouvellement pour les membres du Bureau politiques (BP)', price: 763 },
    { label: 'Adhesion ou renouvellement pour le Secrétariat Exécutif', price: 1527 },
    { label: 'Adhesion ou renouvellement pour les Vice présidents', price: 2290 },
    { label: 'Adhesion ou renouvellement pour le Président du Parti', price: 7634 },
    { label: 'Adhesion ou renouvellement Tarif réduit (-25 ans, étudiants)', price: 15 }
];

const form = document.getElementById('membershipForm1');
const selectedChoice = document.getElementById('selectedChoice');
const totalAmount = document.getElementById('totalAmount');
const donationAmount = document.getElementById('donationAmount');


let selectedPrice = 0;


options.forEach(option => {
    const div = document.createElement('div');
    div.className = 'option';

    const label = document.createElement('label');
    label.innerHTML = `
        <input type="radio" name="membership" value="${option.label}" data-price="${option.price}">
        ${option.label}
    `;

    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'amount';
    button.innerText = `${option.price} €`;


    // Event listen for radio button click (for selecting membership)
    label.querySelector('input').addEventListener('click', () => {
        selectedChoice.innerText = `Votre choix: ${option.label} (${option.price}€)`;
        selectedMembershipLine = option.label; // Store the membership line

        selectedPrice = option.price;
        console.log(selectedPrice);
        updateTotal(); // Update the total amount
    });


    // Event listen for amount button click
    button.addEventListener('click', () => {
        label.querySelector('input').checked = true;
        selectedChoice.innerText = `Votre choix: ${option.label} (${option.price}€)`;
        selectedMembershipLine = option.label; // Store the membership line

        selectedPrice = option.price;
        console.log(selectedPrice);
        updateTotal(); // Update the total amount
    });

    
    // console.log(selected_membership_line);
    // console.log(form);

    div.appendChild(label);
    div.appendChild(button);
    form.appendChild(div);
});


// Event listener for donation amount input change
donationAmount.addEventListener('input', updateTotal);


// This function updates the total and membership line in the form
function updateTotal() {
    const total = selectedPrice + parseFloat(donationAmount.value || 0);
    totalAmount.innerText = `Montant total : ${total.toFixed(2)}€`;
    
    // Update hidden input fields to pass data to the form
    document.getElementById('total-amount').value = `${total.toFixed(2)} €`;
    document.getElementById('membership-line').value = selectedMembershipLine;

    // Last modif ...
    document.addEventListener('DOMContentLoaded', () => {
        const membershipLineElement = document.getElementById('display-membership-line');
        const membershipLine = document.getElementById('membership-line').value;


        console.log( membershipLineElement.nextElementSibling).value;
        console.log(membershipLine);
    
        if (membershipLine) {
            membershipLineElement.innerText = `Membership Line: ${membershipLine}`;
        }
    });    

}


// Initial total update
updateTotal();



/* ----------------------------------------- */
/* The main membership Registration part ... */
/* ----------------------------------------- */   

document.getElementById('membershipForm').addEventListener('submit', function(event) {
    event.preventDefault();
    let formData = new FormData(this);

    fetch('/submit', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Membership successfully registered!');
            updateTotalMembers();
            resetForm();
        } else {
            alert('There was an error registering the membership.');
        }
    });
});



function resetForm() {
    document.getElementById('membershipForm').reset();
}

function updateTotalMembers() {
    fetch('/total_members')
        .then(response => response.json())
        .then(data => {
            document.getElementById('totalMembers').innerText = 'Nombre Total Inscrits : ' + data.total_members;
        });
}


/* --------------------------------------------*/
/* Global integration part ...  Adhesion + Don */
/*---------------------------------------------*/

document.addEventListener('DOMContentLoaded', async () => {
    const membershipForm = document.getElementById('membershipForm');
    const paymentForm = document.getElementById('payment-form');
    const submitPaymentButton = document.getElementById('submit-payment');
    const errorMessage = document.getElementById('error-messages');

    membershipForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Get form data
        const formData = new FormData(membershipForm);
        const amount = formData.get('total-amount');
        const firstName = formData.get('first-name');
        const lastName = formData.get('last-name');
        const email1 = formData.get('email');
        const country = formData.get('country');
        const membershipline = formData.get('membership_line');

        // Modif 24.09.2024
        // Gather  the user's data
        console.log('100. Continue Button clicked ! Now we gather the useful data');
        
        // Hide membership options
        document.getElementById('membershipForm1').style.display = 'none';
        document.getElementById('radioButtonSection').style.display = 'none';

        // Show final confirmation and payment
        document.getElementById('selectedChoice').style.display = 'block';
        

        document.getElementById('first_name').textContent = firstName;
        document.getElementById('last_name').textContent = lastName;
        document.getElementById('email1').textContent = email1;
        // document.getElementById('email').innerHTML = email;
        document.getElementById('membership_line').innerHTML = selectedMembershipLine;
        document.getElementById('total_amount').innerHTML = amount;
                
        // Update Pay button to show total amount
        document.getElementById('submit-payment').innerHTML = `Pay ${amount} Now`;

        //Verification - 24.09.2024 ...
        /*
        console.log('200. Let us verify the Useful data');
        console.log("Email captured: ", email1);

        console.log(document.getElementById('first_name').textContent);
        console.log(document.getElementById('last_name').textContent);

        console.log(document.getElementById('email1').textContent);

        console.log(document.getElementById('membership_line').innerHTML);
        console.log(document.getElementById('total_amount').innerHTML);
        */
        // End Modif 24.09.2024

        // Fecth the Client secret and initialyze elements
        // Send data to server to create payment intent
        const {clientSecret} = await fetch("/create-payment-intent", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                amount,
                firstName,
                lastName,
                email,
                country
            })
        }).then(r => r.json());

        // Fetch the publisable key and init Stripe
        const {publishableKey} = await fetch("/config").then(r => r.json());
        const stripe = Stripe(publishableKey);

        const elements = stripe.elements({clientSecret});
        const paymentElement = elements.create('payment');
        paymentElement.mount('#payment-element');

        // Modif - 23.09.2024 Hiding the Radio buttons after form Submission ...
        document.getElementById('membershipForm1').style.display = 'none';

        // End Modif 23.09.2024 ...
        
        membershipForm.style.display = 'none';
        paymentForm.style.display = 'block';

        submitPaymentButton.addEventListener('click', async () => {
            const {error} = await stripe.confirmPayment({
                elements,
                confirmParams: {
                    return_url: window.location.origin + "/success",
                },
            });

            if (error) {
                errorMessage.textContent = error.message;
                console.error("Error confirming payment:", error);
            }
        });
    });
});


