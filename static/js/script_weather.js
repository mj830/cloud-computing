const container = document.querySelector('.container_weather');
const search = document.querySelector('.search-box_weather button');
const weatherBox = document.querySelector('.weather-box');
const weatherDetails = document.querySelector('.weather-details');
const error404 = document.querySelector('.not-found');


search.addEventListener('click', () => {

    // Feel free to use mine :)
    const APIKey = '185dbcc57e27f9315a49d3f1c762ebd7';
    const city = document.querySelector('.search-box_weather input').value;

    if (city === '')
        return;

    fetch(`https://api.openweathermap.org/data/2.5/weather?q=${city}&units=metric&appid=${APIKey}`)
        .then(response => response.json())
        .then(json => {

            if (json.cod === '404') {

                container.style.height = '400px';

                weatherBox.style.display = 'none';
                weatherDetails.style.display = 'none';

                error404.style.display = 'block';
                error404.classList.add('fadeIn');

                return;

            }

            error404.style.display = 'none';
            error404.classList.remove('fadeIn');

            const image = document.querySelector('.weather-box img');
            const temperature = document.querySelector('.weather-box .temperature');
            const description = document.querySelector('.weather-box .description');
            const humidity = document.querySelector('.weather-details .humidity span');
            const wind = document.querySelector('.weather-details .wind span');

            const currentTime = Math.floor(Date.now() / 1000); // 当前时间的Unix时间戳
            const sunriseTime = json.sys.sunrise; // 日出时间的Unix时间戳
            const sunsetTime = json.sys.sunset; // 日落时间的Unix时间戳

            // 判断当前时间是白天还是黑夜
            const isDayTime = (currentTime >= sunriseTime && currentTime < sunsetTime);

            switch (json.weather[0].id) {
                case 800:
                    image.src = isDayTime ? '../static/weather_image/clear.png' : '../static/weather_image/moon.png';
                    break;

                case 801:
                    image.src = isDayTime ? '../static/weather_image/partly_cloudy.png' : '../static/weather_image/cloud_moon.png';
                    break;

                case 802:
                    image.src = isDayTime ? '../static/weather_image/s_cloud.png' : '../static/weather_image/s_cloud.png';
                    break;

                case 803:
                case 804:
                    image.src = isDayTime ? '../static/weather_image/cloud.png' : '../static/weather_image/cloud.png';
                    break;

                case 200:
                case 201:
                case 202:
                case 230:
                case 231:
                case 232:
                    image.src = isDayTime ? '../static/weather_image/storm.png' : '../static/weather_image/storm.png';
                    break;
                
                case 210:
                case 211:
                case 212:
                case 221:
                    image.src = isDayTime ? '../static/weather_image/thunder.png' : '../static/weather_image/thunder.png';
                    break;

                case 300:
                case 301:
                case 302:
                case 310:
                case 311:
                case 312:
                case 313:
                case 314:
                case 321:
                    image.src = isDayTime ? '../static/weather_image/drizzle.png' : '../static/weather_image/drizzle.png';
                    break;

                case 500:
                    image.src = isDayTime ? '../static/weather_image/light_rain.png' : '../static/weather_image/light_rain.png';
                    break;

                case 501:
                    image.src = isDayTime ? '../static/weather_image/moderate_rain.png' : '../static/weather_image/moderate_rain.png';
                    break;

                case 502:
                case 503:
                    image.src = isDayTime ? '../static/weather_image/heavy_rain.png' : '../static/weather_image/heavy_rain.png';
                    break;

                case 504:
                    image.src = isDayTime ? '../static/weather_image/torrential_rain.png' : '../static/weather_image/torrential_rain.png';
                    break;

                case 511:
                    image.src = isDayTime ? '../static/weather_image/freezing.png' : '../static/weather_image/freezing.png';
                    break;

                case 520:
                case 521:
                case 522:
                case 531:
                    image.src = isDayTime ? '../static/weather_image/rain.png' : '../static/weather_image/rainy_night.png';
                    break;

                case 600:
                case 601:
                case 620:
                case 621:
                    image.src = isDayTime ? '../static/weather_image/snow.png' : '../static/weather_image/snow.png';
                    break;

                case 622:
                case 602:
                    image.src = isDayTime ? '../static/weather_image/snow_storm.png' : '../static/weather_image/snow_storm.png';
                    break;

                case 611:
                case 612:
                case 613:
                case 615:
                case 616:
                    image.src = isDayTime ? '../static/weather_image/sleet.png' : '../static/weather_image/sleet.png';
                    break;

                case 701:
                    image.src = isDayTime ? '../static/weather_image/mist.png' : '../static/weather_image/mist_night.png';
                    break;

                case 721:
                    image.src = isDayTime ? '../static/weather_image/haze.png' : '../static/weather_image/haze.png';
                    break;

                case 741:
                    image.src = isDayTime ? '../static/weather_image/fog.png' : '../static/weather_image/fog.png';
                    break;

                case 711:
                case 731:
                case 751:
                case 761:
                case 762:
                    image.src = isDayTime ? '../static/weather_image/dust.png' : '../static/weather_image/dust.png';
                    break;

                case 771:
                    image.src = isDayTime ? '../static/weather_image/wind.png' : '../static/weather_image/wind.png';
                    break;

                case 781:
                    image.src = isDayTime ? '../static/weather_image/tornado.png' : '../static/weather_image/tornado.png';
                    break;

                default:
                    image.src = '';
            }

            temperature.innerHTML = `${parseInt(json.main.temp)}<span>°C</span>`;
            description.innerHTML = `${json.weather[0].description}`;
            humidity.innerHTML = `${json.main.humidity}%`;
            wind.innerHTML = `${parseInt(json.wind.speed)}Km/h`;

            weatherBox.style.display = '';
            weatherDetails.style.display = '';
            weatherBox.classList.add('fadeIn');
            weatherDetails.classList.add('fadeIn');

            container.style.height = '590px';

        });

});
