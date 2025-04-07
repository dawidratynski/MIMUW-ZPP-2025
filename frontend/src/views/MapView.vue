<script setup>
import { ref, watch } from 'vue'
import { GoogleMap, AdvancedMarker } from 'vue3-google-map'
import { GOOGLE_MAPS_API_KEY } from '@/env'

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

const contains_item_type_options = {
    any: '',
    paper: 'paper',
    plastic: 'plastic',
    glass: 'glass',
    metal: 'metal',
    unknown: 'unknown',
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
        "limit=1000",
        collected.value !== null && "collected=" + collected.value,
        created_before.value && "created_before=" + created_before.value,
        created_after.value && "created_after=" + created_after.value,
        contains_item_type.value && "contains_item_type=" + contains_item_type.value,
        author_id.value && "author_id=" + author_id.value,
    ]
        .filter(Boolean) // Remove params that were not set
        .join('&');

    fetch(`${itemQueryUrl}?${queryParams}`)
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
    fetch(`${itemQueryUrl}${id}`)
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
        <GoogleMap ref="mapRef" class="map" :api-key="GOOGLE_MAPS_API_KEY" mapId="DEMO_MAP_ID"
            :center="mapCenter" :zoom="10" @idle="update_map">
            <div v-for="marker of itemMarkers" :key="marker.id">
                <AdvancedMarker :options="marker.options" :pin-options="marker.pinOptions"
                    @click="handleMarkerClick(marker.id)" />
            </div>
        </GoogleMap>

        <!-- Side panel for displaying selected item details -->
        <div v-if="selectedItem" class="side-panel">
            <button @click="closePanel" class="close-btn">Close</button>
            <div class="item-details">
                <RouterLink :to="'/forum/' + selectedItem.id">Go to Forum</RouterLink>
                <img :src="photoUrlPrefix + selectedItem.image_path" style="max-width: 100%; height: 40%;" />
                <pre>{{ selectedItem }}</pre>
            </div>
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
                        <input type="text" id="textInput" class="form-control" v-model="author_id" />
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
</style>
