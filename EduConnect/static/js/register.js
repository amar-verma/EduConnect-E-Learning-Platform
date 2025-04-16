
// Bootstrap Validation Script
(function () {
    "use strict";
    const forms = document.querySelectorAll(".needs-validation");

    forms.forEach(function (form) {
        form.addEventListener(
            "submit",
            function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add("was-validated");
            },
            false
        );
    });

    // Password match validation
    const passwordInput = document.getElementById("password");
    const confirmPasswordInput =
        document.getElementById("confirm-password");

    confirmPasswordInput.addEventListener("input", function () {
        if (
            passwordInput.value === confirmPasswordInput.value &&
            confirmPasswordInput.value !== ""
        ) {
            confirmPasswordInput.classList.remove("is-invalid");
            confirmPasswordInput.classList.add("is-valid");
        } else {
            confirmPasswordInput.classList.remove("is-valid");
            confirmPasswordInput.classList.add("is-invalid");
        }
    });

    passwordInput.addEventListener("input", function () {
        if (
            passwordInput.value === confirmPasswordInput.value &&
            confirmPasswordInput.value !== ""
        ) {
            confirmPasswordInput.classList.remove("is-invalid");
            confirmPasswordInput.classList.add("is-valid");
        } else {
            confirmPasswordInput.classList.remove("is-valid");
            confirmPasswordInput.classList.add("is-invalid");
        }
    });
})();


document.addEventListener("DOMContentLoaded", function () {
    const registerButton = document.getElementById("register-btn");
    const container1 = document.querySelector(".container-1");
    const container2 = document.querySelector(".container-2");
    const form1 = container1.querySelector("form"); // Get the form in container-1
    const passwordInput = document.getElementById("password");
    const confirmPasswordInput = document.getElementById("confirm-password");

    // Add event listener for the register button
    registerButton.addEventListener("click", function () {
        // Validate container-1 form first
        if (form1.checkValidity() === false) {
            // If form is invalid, stop the process and show validation messages
            form1.classList.add("was-validated");
            return; // Prevent going to container-2
        }

        // Check if password and confirm password match
        if (passwordInput.value !== confirmPasswordInput.value || passwordInput.value === "") {
            confirmPasswordInput.classList.remove("is-valid");
            confirmPasswordInput.classList.add("is-invalid");
            return; // Prevent going to container-2
        }

        // If everything is valid, hide container-1 and show container-2
        // container1.style.display = "none";
        // container2.style.display = "block";
    });

    // Password and confirm password live validation
    passwordInput.addEventListener("input", validatePasswords);
    confirmPasswordInput.addEventListener("input", validatePasswords);

    function validatePasswords() {
        if (
            passwordInput.value === confirmPasswordInput.value &&
            confirmPasswordInput.value !== ""
        ) {
            confirmPasswordInput.classList.remove("is-invalid");
            confirmPasswordInput.classList.add("is-valid");
        } else {
            confirmPasswordInput.classList.remove("is-valid");
            confirmPasswordInput.classList.add("is-invalid");
        }
    }

    // Additional validation for container-2 (Profile Picture Selection)
    const submitButton = container2.querySelector("button[type='submit']");
    const profilePicInput = document.getElementById("selected-image-src");
    submitButton.addEventListener("click", function (event) {
        // Ensure a profile picture is selected
        if (profilePicInput.value === "") {
            event.preventDefault(); // Prevent form submission
            profilePicInput.classList.add("is-invalid"); // Add invalid class
            // alert("Please select a profile picture."); // Show alert or other feedback
        } else {
            profilePicInput.classList.remove("is-invalid");
        }
    });
});


// Function to handle image selection
function selectImage(imageSrc, imageName) {
    document.getElementById('profile-pic').src = imageSrc;
    document.getElementById('profile-pic').style.display = 'block'; // Show selected image
    document.getElementById('selected-image-src').value = imageSrc; // Set value of input field
    document.getElementById('selected-pic-name').textContent = imageName; // Display image name
    document.getElementById('selected-image-src').classList.remove('is-invalid'); // Remove invalid class if any image is selected
}

// Bootstrap form validation
(function () {
    'use strict';
    window.addEventListener('load', function () {
        var forms = document.getElementsByClassName('needs-validation');
        Array.prototype.filter.call(forms, function (form) {
            form.addEventListener('submit', function (event) {
                // Validate if an image has been selected
                var imageInput = document.getElementById('selected-image-src');
                if (imageInput.value === '') {
                    event.preventDefault();
                    event.stopPropagation();
                    imageInput.classList.add('is-invalid'); // Add Bootstrap invalid class
                }

                if (form.checkValidity() === false) {
                    event.preventDefault();
                    event.stopPropagation();
                }

                form.classList.add('was-validated');
            }, false);
        });
    }, false);
})();


// Bootstrap form validation
(function () {
    'use strict';
    window.addEventListener('load', function () {
        var forms = document.getElementsByClassName('needs-validation');
        Array.prototype.filter.call(forms, function (form) {
            form.addEventListener('submit', function (event) {
                if (form.checkValidity() === false) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    }, false);
})();

function selectImage(imageSrc, imageName) {
    // Update the profile picture
    document.getElementById('profile-pic').src = imageSrc;

    // Display the name of the selected image
    document.getElementById('selected-pic-name').textContent = imageName;

    // Store the selected image source in the input text field
    document.getElementById('selected-image-src').value = imageSrc;
}


// Example data for countries, states, and cities
const countries = [
    { name: 'India', states: ['Maharashtra', 'Karnataka', 'Tamil Nadu', 'Delhi', 'Uttar Pradesh', 'West Bengal', 'Rajasthan'] },
    { name: 'USA', states: ['California', 'Texas', 'Florida', 'New York', 'Illinois', 'Pennsylvania', 'Ohio'] },
    { name: 'Canada', states: ['Ontario', 'Quebec', 'British Columbia', 'Alberta', 'Nova Scotia', 'Manitoba', 'Saskatchewan'] },
    { name: 'United Kingdom', states: ['England', 'Scotland', 'Wales', 'Northern Ireland'] },
    { name: 'Australia', states: ['New South Wales', 'Victoria', 'Queensland', 'Western Australia', 'South Australia', 'Tasmania', 'Australian Capital Territory'] },
    { name: 'Germany', states: ['Bavaria', 'Berlin', 'North Rhine-Westphalia', 'Hesse', 'Saxony', 'Baden-Württemberg', 'Lower Saxony'] },
    { name: 'France', states: ['Île-de-France', 'Provence-Alpes-Côte d\'Azur', 'Auvergne-Rhône-Alpes', 'Nouvelle-Aquitaine', 'Occitanie'] },
    { name: 'Brazil', states: ['São Paulo', 'Rio de Janeiro', 'Minas Gerais', 'Bahia', 'Paraná', 'Santa Catarina'] },
    { name: 'South Africa', states: ['Gauteng', 'Western Cape', 'KwaZulu-Natal', 'Eastern Cape', 'Limpopo'] },
    { name: 'Other', states: ['Other'] }
];

const states = {
    'India': ['Maharashtra', 'Karnataka', 'Tamil Nadu', 'Delhi', 'Uttar Pradesh', 'West Bengal', 'Rajasthan'],
    'USA': ['California', 'Texas', 'Florida', 'New York', 'Illinois', 'Pennsylvania', 'Ohio'],
    'Canada': ['Ontario', 'Quebec', 'British Columbia', 'Alberta', 'Nova Scotia', 'Manitoba', 'Saskatchewan'],
    'United Kingdom': ['England', 'Scotland', 'Wales', 'Northern Ireland'],
    'Australia': ['New South Wales', 'Victoria', 'Queensland', 'Western Australia', 'South Australia', 'Tasmania', 'Australian Capital Territory'],
    'Germany': ['Bavaria', 'Berlin', 'North Rhine-Westphalia', 'Hesse', 'Saxony', 'Baden-Württemberg', 'Lower Saxony'],
    'France': ['Île-de-France', 'Provence-Alpes-Côte d\'Azur', 'Auvergne-Rhône-Alpes', 'Nouvelle-Aquitaine', 'Occitanie'],
    'Brazil': ['São Paulo', 'Rio de Janeiro', 'Minas Gerais', 'Bahia', 'Paraná', 'Santa Catarina'],
    'South Africa': ['Gauteng', 'Western Cape', 'KwaZulu-Natal', 'Eastern Cape', 'Limpopo'],
    'Other': ['-']
};

const cities = {
    'Maharashtra': ['Mumbai', 'Pune', 'Nagpur', 'Nashik', 'Aurangabad'],
    'Karnataka': ['Bengaluru', 'Mysuru', 'Mangalore', 'Hubli', 'Belagavi'],
    'Tamil Nadu': ['Chennai', 'Coimbatore', 'Madurai', 'Trichy', 'Salem'],
    'Delhi': ['New Delhi', 'Old Delhi', 'Dwarka', 'Connaught Place'],
    'Uttar Pradesh': ['Lucknow', 'Kanpur', 'Agra', 'Varanasi', 'Noida'],
    'West Bengal': ['Kolkata', 'Siliguri', 'Howrah', 'Durgapur'],
    'Rajasthan': ['Jaipur', 'Udaipur', 'Jodhpur', 'Kota', 'Ajmer'],
    'California': ['Los Angeles', 'San Francisco', 'San Diego', 'Sacramento', 'Oakland'],
    'Texas': ['Houston', 'Dallas', 'Austin', 'San Antonio', 'Fort Worth'],
    'Florida': ['Miami', 'Orlando', 'Tampa', 'Jacksonville', 'Tallahassee'],
    'New York': ['New York City', 'Buffalo', 'Rochester', 'Albany', 'Syracuse'],
    'Illinois': ['Chicago', 'Aurora', 'Naperville', 'Peoria', 'Rockford'],
    'Pennsylvania': ['Philadelphia', 'Pittsburgh', 'Allentown', 'Erie', 'Reading'],
    'Ohio': ['Columbus', 'Cleveland', 'Cincinnati', 'Toledo', 'Akron'],
    'Ontario': ['Toronto', 'Ottawa', 'Mississauga', 'Hamilton', 'London'],
    'Quebec': ['Montreal', 'Quebec City', 'Gatineau', 'Sherbrooke', 'Trois-Rivières'],
    'British Columbia': ['Vancouver', 'Victoria', 'Surrey', 'Burnaby', 'Kelowna'],
    'Alberta': ['Calgary', 'Edmonton', 'Red Deer', 'Lethbridge', 'Fort McMurray'],
    'Nova Scotia': ['Halifax', 'Sydney', 'Truro', 'New Glasgow', 'Bridgewater'],
    'Manitoba': ['Winnipeg', 'Brandon', 'Thompson', 'Portage la Prairie', 'Steinbach'],
    'Saskatchewan': ['Saskatoon', 'Regina', 'Prince Albert', 'Moose Jaw', 'Swift Current'],
    'England': ['London', 'Manchester', 'Birmingham', 'Leeds', 'Liverpool'],
    'Scotland': ['Edinburgh', 'Glasgow', 'Aberdeen', 'Dundee', 'Inverness'],
    'Wales': ['Cardiff', 'Swansea', 'Newport', 'Wrexham', 'Bangor'],
    'Northern Ireland': ['Belfast', 'Derry', 'Lisburn', 'Newtownabbey', 'Armagh'],
    'New South Wales': ['Sydney', 'Newcastle', 'Wollongong', 'Maitland', 'Tweed Heads'],
    'Victoria': ['Melbourne', 'Geelong', 'Ballarat', 'Bendigo', 'Shepparton'],
    'Queensland': ['Brisbane', 'Gold Coast', 'Cairns', 'Townsville', 'Rockhampton'],
    'Western Australia': ['Perth', 'Mandurah', 'Bunbury', 'Albany', 'Geraldton'],
    'South Australia': ['Adelaide', 'Mount Gambier', 'Murray Bridge', 'Whyalla', 'Port Augusta'],
    'Tasmania': ['Hobart', 'Launceston', 'Devonport', 'Burnie', 'Bicheno'],
    'Australian Capital Territory': ['Canberra'],
    'Bavaria': ['Munich', 'Nuremberg', 'Augsburg', 'Regensburg', 'Ingolstadt'],
    'Berlin': ['Berlin'],
    'North Rhine-Westphalia': ['Cologne', 'Düsseldorf', 'Dortmund', 'Essen', 'Bielefeld'],
    'Hesse': ['Frankfurt', 'Wiesbaden', 'Darmstadt', 'Kassel', 'Offenbach'],
    'Saxony': ['Dresden', 'Leipzig', 'Chemnitz', 'Zschopau', 'Riesa'],
    'Baden-Württemberg': ['Stuttgart', 'Mannheim', 'Karlsruhe', 'Heidelberg', 'Freiburg'],
    'Lower Saxony': ['Hanover', 'Braunschweig', 'Oldenburg', 'Osnabrück', 'Wolfsburg'],
    'Île-de-France': ['Paris', 'Versailles', 'Boulogne-Billancourt', 'Montreuil', 'Argenteuil'],
    'Provence-Alpes-Côte d\'Azur': ['Marseille', 'Nice', 'Toulon', 'Aix-en-Provence', 'Avignon'],
    'Auvergne-Rhône-Alpes': ['Lyon', 'Saint-Étienne', 'Grenoble', 'Clermont-Ferrand', 'Annecy'],
    'Nouvelle-Aquitaine': ['Bordeaux', 'Limoges', 'Poitiers', 'Angoulême', 'Périgueux'],
    'Occitanie': ['Toulouse', 'Montpellier', 'Nîmes', 'Perpignan', 'Toulon'],
    'São Paulo': ['São Paulo', 'Campinas', 'Santos', 'Ribeirão Preto', 'Sorocaba'],
    'Rio de Janeiro': ['Rio de Janeiro', 'Niterói', 'Duque de Caxias', 'Nova Iguaçu', 'Cabo Frio'],
    'Minas Gerais': ['Belo Horizonte', 'Uberlândia', 'Contagem', 'Juiz de Fora', 'Montes Claros'],
    'Bahia': ['Salvador', 'Feira de Santana', 'Vitória da Conquista', 'Camaçari', 'Juazeiro'],
    'Paraná': ['Curitiba', 'Londrina', 'Maringá', 'Cascavel', 'Ponta Grossa'],
    'Santa Catarina': ['Florianópolis', 'Joinville', 'Blumenau', 'Itajaí', 'São José'],
    'Gauteng': ['Johannesburg', 'Pretoria', 'Ekurhuleni', 'Midrand', 'Soweto'],
    'Western Cape': ['Cape Town', 'Stellenbosch', 'Paternoster', 'George', 'Knysna'],
    'KwaZulu-Natal': ['Durban', 'Pietermaritzburg', 'Richards Bay', 'Newcastle', 'Umlazi'],
    'Eastern Cape': ['Port Elizabeth', 'East London', 'Mthatha', 'Grahamstown', 'Bhisho'],
    'Limpopo': ['Polokwane', 'Lephalale', 'Makhado', 'Musina', 'Thohoyandou'],
    '-': ['-']
};


// Populate countries
const countrySelect = document.getElementById('country');
countries.forEach(country => {
    const option = document.createElement('option');
    option.value = country.name;
    option.textContent = country.name;
    countrySelect.appendChild(option);
});

// Event listener for country change
countrySelect.addEventListener('change', function () {
    const selectedCountry = this.value;
    const stateSelect = document.getElementById('state');
    const citySelect = document.getElementById('city');

    // Clear previous selections
    stateSelect.innerHTML = '<option value="" style="display: none;">Select State</option>';
    citySelect.innerHTML = '<option value="" style="display: none;">Select City</option>';

    // Populate states based on selected country
    if (selectedCountry && states[selectedCountry]) {
        states[selectedCountry].forEach(state => {
            const option = document.createElement('option');
            option.value = state;
            option.textContent = state;
            stateSelect.appendChild(option);
        });
    }
});

// Event listener for state change
document.getElementById('state').addEventListener('change', function () {
    const selectedState = this.value;
    const citySelect = document.getElementById('city');

    // Clear previous city selections
    citySelect.innerHTML = '<option value="" style="display: none;">Select City</option>';

    // Populate cities based on selected state
    if (selectedState && cities[selectedState]) {
        cities[selectedState].forEach(city => {
            const option = document.createElement('option');
            option.value = city;
            option.textContent = city;
            citySelect.appendChild(option);
        });
    }
});

