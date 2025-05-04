<script setup>
import { ref, watch } from 'vue'
import { GoogleMap, AdvancedMarker } from 'vue3-google-map'
import { GOOGLE_MAPS_API_KEY } from '@/env'
import { useAuth0 } from '@auth0/auth0-vue';
import { AUTH0_AUDIENCE } from '@/env'

const { getAccessTokenSilently, user, isAuthenticated } = useAuth0();

const mapCenter = ref({ lat: 52.212, lng: 20.982 })
const mapRef = ref(null)

const itemMarkers = ref([])
const selectedItem = ref(null)

const itemQueryUrl = "http://localhost:9090/api/v1/items/"
const photoUrlPrefix = "http://localhost:9090"

const colorMapping = {
    "paper": {
        background: "blue",
        borderColor: "darkblue",
        glyphColor: "white"
    },
    "metal": {
        background: "red",
        borderColor: "darkred",
        glyphColor: "white"
    },
    "plastic": {
        background: "yellow",
        borderColor: "goldenrod",
        glyphColor: "black"
    },
    "glass": {
        background: "green",
        borderColor: "darkgreen",
        glyphColor: "white"
    },
    "unknown": {
        background: "gray",
        borderColor: "darkgray",
        glyphColor: "white"
    },
    "multi": {
        background: "lightgray",
        borderColor: "gray",
        glyphColor: "black"
    }
};

const isFilterPanelVisible = ref(false)

// Query filters
const contains_item_type = ref('')
const created_before = ref('')
const created_after = ref('')
const collected = ref(false)
const author_id = ref(null)
const onlyMine = ref(false)

const contains_item_type_options = {
    any: '',
    paper: 'paper',
    plastic: 'plastic',
    glass: 'glass',
    metal: 'metal',
    unknown: 'unknown',
}

watch([onlyMine, user, isAuthenticated], () => {
    if (onlyMine.value && isAuthenticated.value && user.value?.sub) {
        author_id.value = user.value.sub;
    } else if (!onlyMine.value) {
        author_id.value = null;
    }
});

async function fetchWithAuth(url, queryParams = '') {
    const fullUrl = queryParams ? `${url}?${queryParams}` : url
    try {
        const accessToken = await getAccessTokenSilently({
            audience: AUTH0_AUDIENCE,
        });

        return fetch(fullUrl, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            }
        })
    }
    catch {
        return fetch(fullUrl)
    }
}


function update_map() {
    console.log("Updating map...")
    mapCenter.value = mapRef.value.center;
    fetchItemMarkers();
}


watch(() => mapRef.value?.ready, (ready) => {
    if (!ready) return
    update_map();
})


function fetchItemMarkers() {
    const queryParams = [
        "offset=0",
        "limit=50000",
        collected.value !== null && "collected=" + collected.value,
        created_before.value && "created_before=" + created_before.value,
        created_after.value && "created_after=" + created_after.value,
        contains_item_type.value && "contains_item_type=" + contains_item_type.value,
        onlyMine.value && user.value?.sub && "author_id=" + user.value.sub,
        !onlyMine.value && author_id.value && "author_id=" + author_id.value,
    ]
        .filter(Boolean) // Remove params that were not set
        .join('&');

    fetchWithAuth(itemQueryUrl, queryParams)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch data from API');
            }
            return response.json();
        })
        .then(data => {
            itemMarkers.value = [];

            data.forEach(item => {
                const { id, latitude, longitude, bounding_boxes } = item;
                const uniqueTypes = [...new Set(bounding_boxes.map(box => box.item_type))];

                itemMarkers.value.push({
                    id: id,
                    pinOptions: (
                        uniqueTypes.length === 1
                            ? colorMapping[uniqueTypes[0]]
                            : colorMapping["multi"]
                    ),
                    options: {
                        position: { lat: latitude, lng: longitude },
                        title: `Item ${id}`
                    },
                });
            });
        })
        .catch(error => {
            console.error('An error occurred while loading items:', error);
        });
}


function fetchItemDetails(id) {
    fetchWithAuth(`${itemQueryUrl}${id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch item details');
            }
            return response.json();
        })
        .then(data => {
            selectedItem.value = data;
        })
        .catch(error => {
            console.error('An error occurred while fetching item details:', error);
        });
}


function handleMarkerClick(id) {
    fetchItemDetails(id);
}


function closePanel() {
    selectedItem.value = null;
}

function openFilterPanel() {
    isFilterPanelVisible.value = true;
}

function closeFilterPanel() {
    isFilterPanelVisible.value = false;
    update_map();
}

</script>

<template>
    <div class="map_wrapper">
        <GoogleMap ref="mapRef" class="map" :api-key="GOOGLE_MAPS_API_KEY" mapId="DEMO_MAP_ID" :center="mapCenter"
            :zoom="10" @idle="update_map">
            <div v-for="marker of itemMarkers" :key="marker.id">
                <AdvancedMarker :options="marker.options" :pin-options="marker.pinOptions"
                    @click="handleMarkerClick(marker.id)" />
            </div>
        </GoogleMap>

        <!-- Side panel for displaying selected item details -->
        <div v-if="selectedItem" class="item-details-panel bg-light border-start shadow">
            <img :src="photoUrlPrefix + selectedItem.image_path" class="item-details-image w-100 rounded"
                alt="Item Image" />

            <div class="mt-3">
                <h5 class="fw-bold">Item Details</h5>
            </div>

            <div class="card border-0">
                <div class="card-body p-0 pt-2">
                    <ul class="list-group list-group-flush mb-3">
                        <li class="list-group-item">
                            <strong>Created:</strong> {{ new Date(selectedItem.created_at).toLocaleString() }}
                        </li>
                        <li class="list-group-item">
                            <strong>Coordinates:</strong>
                            {{ selectedItem.latitude.toFixed(6) }}, {{ selectedItem.longitude.toFixed(6) }}
                        </li>
                        <li class="list-group-item">
                            <strong>Collected:</strong> {{ selectedItem.collected ? 'Yes' : 'No' }}
                        </li>
                        <li class="list-group-item" v-if="selectedItem.collected">
                            <strong>Collected By:</strong> {{ selectedItem.collected_by }}<br />
                            <strong>Timestamp:</strong> {{ new Date(selectedItem.collected_timestamp).toLocaleString()
                            }}
                        </li>
                        <li class="list-group-item">
                            <strong>Reported by user:</strong> {{ selectedItem.user_id }}<br />
                        </li>
                    </ul>

                    <div>
                        <h6>Bounding Boxes:</h6>
                        <ul class="list-group">
                            <li class="list-group-item" v-for="(box, index) in selectedItem.bounding_boxes"
                                :key="index">
                                <strong>Type:</strong> {{ box.item_type }}<br />
                                <strong>Coords:</strong>
                                ({{ box.x_left }}, {{ box.y_top }}) → ({{ box.x_right }}, {{ box.y_bottom }})
                            </li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- Forum Button -->
            <div class="item-details-forum-btn">
                <RouterLink :to="'/forum/' + selectedItem.id" class="btn btn-outline-primary btn-sm">
                    View in Forum
                </RouterLink>
            </div>

            <!-- Close Button -->
            <button type="button" class="btn btn-light btn-sm item-details-close" aria-label="Close"
                @click="closePanel">
                &times;
            </button>
        </div>




        <!-- Panel + overlay for setting filters -->
        <div>
            <!-- Button to open the filter panel -->
            <button v-if="!isFilterPanelVisible" class="btn btn-primary filter-btn" @click="openFilterPanel">
                Change filters
            </button>

            <!-- Filter Panel -->
            <div v-if="isFilterPanelVisible" class="filter-panel-overlay">
                <!-- Overlay to close the filter panel when clicked -->
                <div class="overlay" @click="closeFilterPanel"></div>

                <div class="filter-panel-content">
                    <div class="mb-3">
                        <label for="enumSelect" class="form-label">Contains type</label>
                        <select id="enumSelect" class="form-select" v-model="contains_item_type">
                            <option v-for="(value, key) in contains_item_type_options" :key="key" :value="value">{{
                                value }}</option>
                        </select>
                    </div>

                    <div class="mb-3">
                        <label for="enumSelect2" class="form-label">Include collected</label>
                        <select id="enumSelect2" class="form-select" v-model="collected">
                            <option :value="null">All</option>
                            <option :value="false">Only not collected</option>
                            <option :value="true">Only collected</option>
                        </select>
                    </div>

                    <div class="mb-3">
                        <label for="dateSelector" class="form-label">Created before</label>
                        <input type="date" id="dateSelector" class="form-control" v-model="created_before" />
                    </div>

                    <div class="mb-3">
                        <label for="dateSelector" class="form-label">Created after</label>
                        <input type="date" id="dateSelector" class="form-control" v-model="created_after" />
                    </div>

                    <div class="mb-3">
                        <label for="textInput" class="form-label">Author ID</label>
                        <input type="text" id="textInput" class="form-control" v-model="author_id"
                            :disabled="onlyMine" />
                    </div>

                    <div class="mb-3">
                        <label class="form-label">
                            <input type="checkbox" v-model="onlyMine" :disabled="!isAuthenticated"
                                class="form-check-input me-2" />
                            Only mine
                        </label>
                    </div>

                    <button class="btn btn-danger" @click="closeFilterPanel">Close</button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.map {
    width: 100%;
    height: 100%;
}

.map_wrapper {
    flex-grow: 1;
    width: 100%;
    overflow: hidden;
}

.side-panel {
    position: fixed;
    right: 0;
    top: 60px;
    width: 30%;
    height: calc(100% - 60px);
    background-color: rgba(0, 0, 0, 0.7);
    color: white;
    padding: 20px;
    overflow-y: auto;
    z-index: 10;
}


.close-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    padding: 5px 10px;
    background-color: red;
    color: white;
    border: none;
    cursor: pointer;
}

.item-details {
    margin-top: 50px;
    white-space: pre-wrap;
    word-wrap: break-word;
}

.filter-panel-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1050;
    /* Bootstrap modal z-index */
}

.overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.7);
}

.filter-panel-content {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    z-index: 1060;
    width: 60%;
    max-width: 600px;
}

.filter-panel-content .form-control {
    margin-bottom: 1rem;
}

.filter-btn {
    position: fixed;
    bottom: 20px;
    left: 20px;
    z-index: 1070;
}

.item-details-panel {
    position: fixed;
    top: 60px;
    right: 0;
    width: 30%;
    height: calc(100% - 60px);
    padding: 20px;
    overflow-y: auto;
    z-index: 1020;
    background-color: #f8f9fa;
    display: flex;
    flex-direction: column;
    position: fixed;
}

.item-details-image {
    max-height: 50%;
    object-fit: contain;
}

.item-details-close {
    position: absolute;
    top: 15px;
    right: 15px;
    font-size: 1.5rem;
    font-weight: bold;
    background-color: #ffffffcc;
    border: 1px solid #ced4da;
    border-radius: 50%;
    width: 36px;
    height: 36px;
    line-height: 1;
    text-align: center;
    z-index: 1021;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.item-details-forum-btn {
    position: absolute;
    bottom: 20px;
    right: 20px;
    z-index: 1021;
}
</style>
