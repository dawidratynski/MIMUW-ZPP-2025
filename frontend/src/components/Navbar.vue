<template>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark" style="padding: 10px;">
        <div class="navbar-brand" href="#">CleanTheWorld</div>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarText"
            aria-controls="navbarText" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarText">
            <ul class="navbar-nav me-auto">
                <li class="nav-item active">
                    <RouterLink class="nav-link" to="/">
                        Home
                    </RouterLink>
                </li>
                <li class="nav-item active">
                    <RouterLink class="nav-link" to="/about">
                        About
                    </RouterLink>
                </li>
            </ul>
            <ul class="navbar-nav ms-auto">
                <li class="nav-item">
                    <RouterLink class="nav-link" to="/login">
                        Login
                    </RouterLink>
                </li>
            </ul>
        </div>
    </nav>
</template>
