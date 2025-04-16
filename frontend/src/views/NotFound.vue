<template>
    <div class="not-found">
        <h1>404 - Page Not Found</h1>
        <p>The page you're looking for doesn't exist.</p>
        <router-link to="/">Go back home</router-link>
    </div>
</template>

<style scoped>
.not-found {
    text-align: center;
    padding: 50px;
    font-family: Arial, sans-serif;
}

.not-found h1 {
    font-size: 3rem;
    color: #ff6b6b;
}

.not-found p {
    font-size: 1.2rem;
    margin: 20px 0;
}

.not-found a {
    color: #3498db;
    text-decoration: none;
    font-weight: bold;
}
</style>