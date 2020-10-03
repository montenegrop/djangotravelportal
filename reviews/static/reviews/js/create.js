var reviews_create_app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#reviews_create',
    data: {
        isLoading: false,
        countries_json: countries_json,
        tour_operators_json: tour_operators_json,
        selected_country: selected_country,
        selected_park: selected_park,
        selected_tour_operator: selected_tour_operator,
        review_type: review_type,
    },
    // methods: {
    //     submit_form() {
    //
    //     }
    // },
    mounted: function () {
        this.$refs.create_form.classList.remove('d-none');
    },

    computed: {
        selected_country_saved: function () {
            if (this.selected_country) {
            return this.countries_json.find(country => country.id == this.selected_country)
                } else {
                return this.selected_country
            }
        }
    }
});
