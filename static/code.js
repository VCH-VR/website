function hash(str) {
    // Custom seed/"Salt" for hash function
    let seed = 58511069;

    // I'm gonna be honest idk what the rest of this function is I stole it off stack overflow
    let h1 = 0xdeadbeef ^ seed, h2 = 0x41c6ce57 ^ seed;
    for (let i = 0, ch; i < str.length; i++) {
        ch = str.charCodeAt(i);
        h1 = Math.imul(h1 ^ ch, 2654435761);
        h2 = Math.imul(h2 ^ ch, 1597334677);
    }

    h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507) ^ Math.imul(h2 ^ (h2 >>> 13), 3266489909);
    h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507) ^ Math.imul(h1 ^ (h1 >>> 13), 3266489909);

    return 4294967296 * (2097151 & h2) + (h1 >>> 0);
}

async function checkLogin() {
    // Reads username and password and assigns them to a value
    username = document.getElementById("username").value;
    password = document.getElementById("password").value;
    // Hashes password
    password = hash(password);
    console.log("test");

    // Calls the PASS function in /student as seen in index.py, assigns reply to variable data
    const response = await fetch('https://undefined100.pythonanywhere.com/login', {
        method: 'PASS',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            "Access-Control-Allow-Methods": "PASS"
        },
        body: JSON.stringify({username, password})});
    return await response.text();
}

async function readLogin() {
    answer = checkLogin();

    answer.then(function(value) {
        if (value.valueOf() == "correct") {
        location.href = "patients";
        }
        else document.getElementById("message").innerHTML = value;
    });
}






async function getPatients() {
    const response = await fetch('https://undefined100.pythonanywhere.com/patientdata', {method: 'PULLLIST',});
    return await response.text();
}


async function fillPatients() {
    rawData = getPatients();

    rawData.then(function(value) {
        patientCount = (value.match(/{/g)||[]).length;
        patientList = document.getElementById("patientList");

        for (let i = 1; i <= patientCount; i++) {
            substring = value.substring(value.indexOf("{")+2, value.indexOf("}")-1);
            patientName = substring.substring(0, substring.indexOf("'"));
            birthday = substring.substring(substring.indexOf("'")+4);
            cleanPatientName = patientName.replace(/_/g, " ");
            cleanBirthday = birthday.substring(0, 2) + "/" + birthday.substring(2, 4) + "/" + birthday.substring(4);
            patientList.innerHTML += "<div><button onclick='display(" + '"' + birthday + patientName + '"' + ")'>" + cleanPatientName + ", " + cleanBirthday + "</button></div>";
            value = value.substring(value.indexOf("}")+1);
        }
    });
}

async function initializePatients() {
    fillPatients();
}

async function initializeDisplay() {
    const response = await fetch('https://undefined100.pythonanywhere.com/display', {method: 'PULL'});
    var patient = await response.text();

    document.getElementById("graph").src = "../static/patientFiles/" + patient + ".png";
    document.getElementById("graph2").src = "../static/patientFiles/" + patient + "2.png";
}





async function display(patient) {
    const response = await fetch('https://undefined100.pythonanywhere.com/display/' + patient, {method: 'GET'});
    location.href = "display/" + patient;
}




