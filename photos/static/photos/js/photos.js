Vue.component('paginate', VuejsPaginate);
Vue.use(VueLoading);

Vue.component('loading', VueLoading)

var photos_app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#photos',
    data: {
        isLoading: false,
        photos_count: 0,
        photos_urls:
            [],
        page_count: 0,
        current_page: 1,
        countries: countries_json,
        country: country_selected,
        sort_by: 'DATE_ASC',
        animals: animals_json,
        animal: animal_selected,
        activities: activities_json,
        has_results: true,
        no_results: false,
        activity: activity_selected,
        gallery: false,
        csrf_token: csrf_token,
        parks: parks_json,
        parks_original: parks_json,
        park: park_selected,
        photos_json: [],
    },
    methods: {
        filter_park() {
            var country = this.countries.find(obj => {
                return obj.slug === this.country
            }
        )
            ;
            this.parks = this.parks_original.filter(function (item) {
                let filtered = true
                if (country) {
                    filtered = country.parks.includes(item.slug)
                }
                return filtered
            });
            var park_found = false;
            for (let i = 0; i < this.parks.length; i++) {
                if (this.park == this.parks[i].slug) {
                    park_found = true;
                    break;
                }
            }
            ;
            if (!park_found) {
                this.park = '';
            }
        },
        changePage(current_page) {
            //document.location.href = this.update_url_parameter(document.location.href, "page", current_page);
            this.refresh_photos();
        },
        submit_search(e) {
            e.preventDefault();
            this.current_page = 1;
            this.refresh_photos();
        },
        refresh_photos() {
            this.isLoading = true;
            var animal = this.animal;
            var country = this.country;
            var park = this.park;
            var current_page = this.current_page;
            var activity = this.activity;
            var csrf_token = this.csrf_token;
            axios.post("/photos/api/photos/", {
                    country: country,
                    csrfmiddlewaretoken: csrf_token,
                    park: park,
                    animal: animal,
                    current_page: current_page,
                    activity: activity,
                }
            ).then(response => {
                if(response.data.photos_json.length == 0
        )
            {
                this.has_results = false;
                this.has_results = false;
                this.no_results = true
            }
        else
            {
                this.has_results = true;
                this.no_results = false;
            }
            this.photos_json = response.data.photos_json;
            this.page_count = response.data.page_count;
            this.photos_count = response.data.photos_count;
            this.isLoading = false;
        })
        },
        reset: function () {
            this.current_page = "";
            this.animal = "";
            this.country = "";
            this.park = "";
            this.activity = "";
        },
        get_url_parameter: function (sParam) {
            var sPageURL = window.location.search.substring(1);
            var sURLVariables = sPageURL.split('&');
            for (var i = 0; i < sURLVariables.length; i++) {
                var sParameterName = sURLVariables[i].split('=');
                if (sParameterName[0] == sParam) {
                    return sParameterName[1];
                }
            }
            return '';
        },
        update_url_parameter: function (url, param, paramVal) {
            var newAdditionalURL = "";
            var tempArray = url.split("?");
            var baseURL = tempArray[0];
            var additionalURL = tempArray[1];
            var temp = "";
            if (additionalURL) {
                tempArray = additionalURL.split("&");
                for (var i = 0; i < tempArray.length; i++) {
                    if (tempArray[i].split('=')[0] != param) {
                        newAdditionalURL += temp + tempArray[i];
                        temp = "&";
                    }
                }
            }

            var rows_txt = temp + "" + param + "=" + paramVal;
            return baseURL + "?" + newAdditionalURL + rows_txt;
        }
    },
    mounted: function () {
        this.current_page = this.get_url_parameter("page");
        this.animal = this.get_url_parameter("animal") || animal_selected;
        this.country = this.get_url_parameter("country");
        this.park = this.get_url_parameter("park");
        this.activity = this.get_url_parameter("activity");
        this.filter_park(false, false);
        this.refresh_photos();
    },


    watch: {
        country: function () {
            this.filter_park();
        }
    }
});

