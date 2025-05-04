<script setup>
import { useAuth0 } from '@auth0/auth0-vue';
import { useI18n } from 'vue-i18n'
import { watch } from 'vue'

const auth0 = useAuth0();

const user = auth0.user;
const isAuthenticated = auth0.isAuthenticated;
const isLoading = auth0.isLoading;

const { locale } = useI18n()


async function login() {
    await auth0.loginWithRedirect();
    await auth0.getAccessTokenSilently();
}

async function logout() {
    await auth0.logout({
        logoutParams: {
            returnTo: window.location.origin
        }
    });
}

watch(locale, (newLocale) => {
    localStorage.setItem('app-locale', newLocale)
})

</script>

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
                        {{ $t('home') }}
                    </RouterLink>
                </li>
                <li class="nav-item active">
                    <RouterLink class="nav-link" to="/about">
                        {{ $t('about') }}
                    </RouterLink>
                </li>
            </ul>
            <ul class="navbar-nav ms-auto">
                <li class="nav-item">
                    <select id="language-select" v-model="locale">
                        <option value="pl">Polski</option>
                        <option value="en">English</option>
                    </select>
                </li>
                <li class="nav-item" v-if="isAuthenticated">
                    <div class="navbar-text"> {{ $t('logged_as') }} {{ user.email }} </div>
                </li>
                <li class="nav-item">
                    <button v-if="isAuthenticated" @click="logout" class="nav-link">{{ $t('log_out') }}</button>
                    <button v-if="!isAuthenticated && !isLoading" @click="login" class="nav-link">{{ $t('log_in') }}</button>
                </li>
            </ul>
        </div>
    </nav>
</template>
