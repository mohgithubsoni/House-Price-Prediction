// 1. Ye function tab chalta hai jab koi "Estimate Price" button dabata hai
async function onClickedEstimatePrice() {
    console.log("Estimate price button clicked");
    
    // HTML se values uthao
    var sqft = document.getElementById("uiSqft").value;
    var bhk = getBHKValue();
    var bath = getBathValue();
    var location = document.getElementById("uiLocations").value;
    var estPrice = document.getElementById("uiEstimatedPrice");

    // FastAPI server ka URL (Hamara local server)
    var url = "https://bengaluruhppredictor-4jyn.onrender.com/predict_home_price";

    // API ko data bhejo (POST request)
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            total_sqft: parseFloat(sqft),
            bhk: bhk,
            bath: bath,
            location: location
        })
    });

    const data = await response.json();
    // Result ko website par dikhao
    estPrice.innerHTML = "<h2>" + data.estimated_price.toString() + " Lakh</h2>";
}

// 2. Page load hote hi sari locations dropdown mein bhar do
async function onPageLoad() {
    console.log("document loaded, fetching locations...");
    var url = "https://bengaluruhppredictor-4jyn.onrender.com/get_location_names"; 
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        
        if(data && data.locations) {
            console.log("Locations received!");
            var locations = data.locations;
            var uiLocations = document.getElementById("uiLocations");
            
            // Purani list saaf karo placeholder ke alawa
            uiLocations.innerHTML = '<option value="" disabled selected>Select specific locality in Bengaluru</option>';
            
            for(var i in locations) {
                var opt = new Option(locations[i]);
                uiLocations.add(opt);
            }
        }
    } catch (error) {
        console.log("Backend waking up... please wait 1 minute and refresh.");
    }
}

// Ye helper functions hain selected radio button ki value nikalne ke liye
function getBathValue() {
    var uiBathrooms = document.getElementsByName("uiBathrooms");
    for(var i in uiBathrooms) {
      if(uiBathrooms[i].checked) {
          return parseInt(i)+1;
      }
    }
    return -1; 
}

function getBHKValue() {
    var uiBHK = document.getElementsByName("uiBHK");
    for(var i in uiBHK) {
      if(uiBHK[i].checked) {
          return parseInt(i)+1;
      }
    }
    return -1; 
}

window.onload = onPageLoad;