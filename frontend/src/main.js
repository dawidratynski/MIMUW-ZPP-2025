import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'

import { createApp } from 'vue'
import router from './router'
import App from './App.vue'
import { createAuth0 } from '@auth0/auth0-vue'
import { AUTH0_DOMAIN, AUTH0_CLIENT_ID } from '@/env'

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
  .mount('#app')
