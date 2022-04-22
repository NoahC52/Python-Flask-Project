// Api stuff
let url_final = "https://api.openweathermap.org/data/2.5/weather?lat=";
let key = "&appid=f1cabbb0e1f9b185fd3b70cd8240f3b0";
let api = "https://api.openweathermap.org/geo/1.0/zip?zip=";

async function weather_f() {
    let country = document.getElementById("country");
    let zip = document.getElementById("zipcode");
    let sum = api + zip.value + "," + country.value + key;

    axios.get(sum)
        .then(async function (response) {
            console.log(response);
            let lon = response.data.lon
            let lat = response.data.lat
            let sum_final = url_final + lat + "&lon=" + lon + key + "&units=imperial";

            await
                axios.get(sum_final)
                .then(function (data) {
                    console.log(data);
                    let temp = data.data.main.temp;
                    let feels = data.data.main.feels_like;
                    let humidity = data.data.main.humidity;
                    let name = data.data.name;
                    let temp_rounded = Math.floor(temp)
                    let feel_rounded = Math.floor(feels)
                    let parsed = document.getElementById("name_place");
                    let parsed2 = document.getElementById("temp");
                    let parsed3 = document.getElementById("humidity");
                    parsed.textContent = `Here's the weather for ${name}!`
                    parsed2.textContent = `The temperature is currently ${temp_rounded}° fahrenheit and it feels like ${feel_rounded}° fahrenheit.`
                    parsed3.textContent = `The humidity is currently ${humidity}%`
                })
        })
}