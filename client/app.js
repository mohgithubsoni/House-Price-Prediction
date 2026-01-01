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
    var url = "http://127.0.0.1:8000/predict_home_price";

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
    console.log( "document loaded" );
    // Hum ek endpoint banayenge jo locations ki list dega (Abhi banate hain)
    var url = "http://127.0.0.1:8000/get_location_names"; 
    
    const response = await fetch(url);
    const data = await response.json();
    
    if(data) {
        var locations = data.locations;
        var uiLocations = document.getElementById("uiLocations");
        for(var i in locations) {
            var opt = new Option(locations[i]);
            uiLocations.add(opt);
        }
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