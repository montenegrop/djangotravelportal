import Vue from 'vue'
import components from './components'
import {VueAvatar} from 'vue-avatar-editor-improved'
import VueResource from 'vue-resource'
import VueCookies from 'vue-cookies'

import Paginate from 'vuejs-paginate'
import Loading from 'vue-loading-overlay'

Vue.component('paginate', Paginate)
Vue.use(Loading)
Vue.use(VueResource)
Vue.use(VueCookies)




Vue.config.devtools = true

function instanceVue() {
    const app = new Vue({
        delimiters: ['[[', ']]'],
        components: {
            ...components,
            VueAvatar,
        },
        el: '.vue-instance',
    })
}
window.Vue = Vue
window.instanceVue = instanceVue