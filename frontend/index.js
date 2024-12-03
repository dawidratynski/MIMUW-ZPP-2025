let map;

const MAP_START_POSITION = { lat: 52.212, lng: 20.982 };

async function initMap() {

    // Request needed libraries.
    //@ts-ignore
    const { Map, InfoWindow } = await google.maps.importLibrary("maps");
    const { AdvancedMarkerElement, PinElement } = await google.maps.importLibrary("marker");

    map = new Map(document.getElementById("map"), {
        zoom: 8,
        center: MAP_START_POSITION,
        mapId: "CleanTheWorld Map Demo",
    });

    const infoWindow = new InfoWindow();

    // Use search params from this url
    // This will be done by some fancy ui in the future
    const queryParams = new URLSearchParams(new URL(window.location).search);

    // Fetch data from the API
    fetch('/api/v1/item/search?' + queryParams.toString())
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch data from api');
            }
            return response.json();
        })
        .then(data => {
            data.forEach(item => {
                const { id, latitude, longitude, type } = item;
                const photo_url = '/static/photos/test.jpg';

                const pin_background_color = ({
                    plastic: 'Gold',
                    paper: 'SteelBlue',
                    glass: 'MediumSeaGreen',
                    other: 'LightGray',
                })[type] || 'LightSalmon';

                const pin_glyph_color = ({
                    plastic: 'DarkOrange',
                    paper: 'MidnightBlue',
                    glass: 'DarkGreen',
                    other: 'DarkGray',
                })[type] || 'DarkRed';

                const pin = new PinElement({
                    borderColor: "black",
                    background: pin_background_color,
                    glyphColor: pin_glyph_color,
                });

                const marker = new AdvancedMarkerElement({
                    map: map,
                    position: { lat: latitude, lng: longitude },
                    title: `Item #${id}, type: ${type}`,
                    content: pin.element,
                    gmpClickable: true,
                });

                marker.addListener('click', ({ domEvent, latLng }) => {
                    const { target } = domEvent;

                    infoWindow.close();
                    infoWindow.setContent(
                        `<h2>${marker.title}</h2>` + 
                        `<img src=${photo_url} alt="photo" height="300">`
                    );
                    infoWindow.open(marker.map, marker);
                });

            });
        })
        .catch(error => {
            console.error('An error occured while loading items:', error);
        });

}

initMap();
