import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'

import { createApp } from 'vue'
import { createI18n } from 'vue-i18n'
import router from './router'
import App from './App.vue'
import { createAuth0 } from '@auth0/auth0-vue'
import { AUTH0_DOMAIN, AUTH0_CLIENT_ID } from '@/env'

import en from './locales/en.json'
import pl from './locales/pl.json'

const savedLocale = localStorage.getItem('app-locale') || 'pl'

const i18n = createI18n({
  legacy: false,
  locale: savedLocale,
  fallbackLocale: 'pl',
  messages: {
    en,
    pl
  }
})

createApp(App)
  .use(
    createAuth0({
      domain: AUTH0_DOMAIN,
      clientId: AUTH0_CLIENT_ID,
      authorizationParams: {
        redirect_uri: window.location.origin,
      },
    }),
  )
  .use(router)
  .use(i18n)
  .mount('#app')
