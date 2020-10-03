Vue.component('tour', {
    template: '#tour_component',
    delimiters: ['[[', ']]'],
    props: {
        tour: {
            type: Object,
            required: true
        }
    },
    methods: {
        getTourUrl(tour) {
            return '/tours/' + tour.id + '/' + tour.slug
        },

        heartChange(tour) {
            var $counter = $('.far.fa-stack-1x.counter.fav-counter')
            let count = $counter.text()
            count = count ? parseInt(count) : 0
            tour.is_fav = !tour.is_fav
            if (tour.is_fav) {
                $(".fa-nav-heart").addClass('fa-beat')
                $.get('/add_itinerary_fav/' + tour.id + '/', null, function (res) {
                    if (res['status'] == 'ok') {
                        $counter.text(res['count'])
                    } else {
                        tour.is_fav = !tour.is_fav
                        $.notify({
                            message: res['message']
                        }, {
                            placement: {
                                from: "top",
                                align: "right"
                            },
                            type: 'danger'
                        });
                    }

                })
            } else {
              $(".fa-nav-heart").addClass('fa-beat');
                $.get('/delete_itinerary_fav/' + tour.id + '/', null, function (res) {
                    if (res['status'] == 'ok') {
                        $counter.text(res['count'])
                    } else {
                        tour.is_fav = !tour.is_fav
                        $.notify({
                            message: res['message']
                        }, {
                            placement: {
                                from: "top",
                                align: "right"
                            },
                            type: 'danger'
                        });
                    }
                })
            }
        },

    }
})

Vue.component('star-rating', VueStarRating.default);
Vue.use(window.vuelidate.default);
const { required, minLength, email, sameAs, alphaNum, helpers, requiredIf, minValue } = window.validators;

var app = new Vue({
    router: new VueRouter({
        mode: 'history',
        routes: [
            { path: '/african-safari-tour-packages/:slug' }
        ]
    }),
    delimiters: ['[[', ']]'],
    el: '#all_tour_packages',
    components: {
        VueStarRating
    },
    data: {
        custom_filters: [],
        tourpackages: [],
        is_loading: false,

        isLoading: false,
        errors: [],
        serverError: null,
        current_page: 1,
        pagination: {
            positions_total: null,
            positions_on_page: null,
            showing_from: null,
            showing_to: null,
        },
        ordering: [
            { id: null, title: 'Newest', value: '-id' },
            { id: 1, title: 'Price (high-low)', value: '-min_price' },
            { id: 2, title: 'Price (low-high)', value: 'min_price' },
            //{ id: 1, title: 'Alphabetical (A-Z)', value: 'title' },
            //{ id: 2, title: 'Reverse alphabetical (Z-A)', value: '-title' },
            //{ id: 3, title: 'Highest average rating', value: '-tour_operator__average_rating' },
            //{ id: 4, title: 'Most reviewed', value: 'tour_operator__reviews_count' },
            //{ id: 5, title: 'Most tour packages', value: '-tour_operator__packages_count' },
            //{ id: 6, title: 'Recently reviewed', value: '-tour_operator__last_review_date' },
            //{ id: 7, title: 'Recently added', value: '-id' }
        ],
        selected_order: '-id',
        lazytimer: null,
        is_inited: false,
        filters_conveyor: [],
        slug: server_slug
    },
    validations: {
    },
    methods: {
        changeFilter() {
            if (this.is_inited) {
                this.current_page = 1
            }
            this.lazyLoad()
        },
        removeFilter(filter) {
            this.current_page = 1
            for (let i = this.custom_filters.length - 1; i >= 0; i--) {
                if (this.custom_filters[i].tag == filter.tag && this.custom_filters[i].value == filter.value) {
                    this.custom_filters.splice(i, 1)
                    break
                }
            }
            this.$refs.filter1.removeFilterInComponent(filter)
            this.$refs.filter2.removeFilterInComponent(filter)
        },
        removeSlug() {
            if (this.slug) {
                this.slug = null
                slugRoutePush.bind(this)(this.slug)
            }
        },
        changeSlug(slug) {
            this.slug = slug
            slugRoutePush.bind(this)(this.slug)
        },
        load() {
            var app = this
            this.is_loading = true
            this.tourpackages = []

            const filters = {}

            if (this.current_page > 1) {
                filters.page = this.current_page
            }

            for (let i = 0; i < this.custom_filters.length; i++) {
                const filter = this.custom_filters[i]
                if (filter.tag == 'country') {
                    if (!filters.countries) filters.countries = []
                    filters.countries.push(filter.id)
                }
                if (filter.tag == 'park') {
                    if (!filters.parks) filters.parks = []
                    filters.parks.push(filter.id)
                }
                if (filter.tag == 'days') {
                    filters.days = filter.value
                }
                if (filter.tag == 'min-price') {
                    filters.min_price = filter.value
                }
                if (filter.tag == 'max-price') {
                    filters.max_price = filter.value
                }
                if (filter.tag == 'from-date') {
                    filters.from_date = filter.value
                }
                if (filter.tag == 'to-date') {
                    filters.to_date = filter.value
                }
                if (filter.tag == 'adult-travelers') {
                    filters.adult_travelers = filter.value
                }
                if (filter.tag == 'secondary-focus') {
                    if (!filters.secondary_focus) filters.secondary_focus = []
                    filters.secondary_focus.push(filter.id)
                }
                if (filter.tag == 'safary-preference') {
                    filters.safary_preference = filter.id
                }
                if (filter.tag == 'main-focus') {
                    filters.main_focus = filter.id
                }
                if (filter.tag == 'activity-level') {
                    if (!filters.activity_levels) filters.activity_levels = []
                    filters.activity_levels.push(filter.value)
                }
            }

            if (this.selected_order && this.selected_order != 'id') {
                let ordering = this.ordering.find(x => x.value == this.selected_order)
                if (ordering.id) {
                    filters.ordering = this.selected_order
                }
            }

            this.$router.replace({ query: filters }).catch(function (error) {
                if (!error.message.includes('Avoided redundant navigation to current location')) {
                    console.error(error)
                }
            })
            this.filters_conveyor.push(JSON.stringify(filters))

            filters.slug = this.slug

            axios.get('/api/tour-packages/', { params: filters })
                .then(function (response) {
                    let last_conveyor_index = app.filters_conveyor.length - 1
                    delete response.config.params['slug']
                    let json_params = JSON.stringify(response.config.params)
                    // this condition is necessary to avoid overwriting the response of old query
                    if (app.filters_conveyor[last_conveyor_index] == json_params) {
                        app.tourpackages = response.data.results
                        app.pagination.positions_total = response.data.count
                        app.pagination.positions_on_page = response.data.results.length
                        app.is_loading = false
                        app.filters_conveyor.splice(0, last_conveyor_index)
                    } else {
                        console.log('this request is old', json_params)
                    }
                    app.is_inited = true
                })
        },
        lazyLoad() {
            var app = this;
            var later = function () {
                app.lazytimer = null;
                app.load();
            };
            clearTimeout(app.lazytimer);
            app.lazytimer = setTimeout(later, 50);
        },
        clearFilters() {
            while (this.custom_filters.length) {
                let index = this.custom_filters.length - 1
                let filter = this.custom_filters[index]
                this.removeFilter(filter)
                if (index == this.custom_filters.length - 1) {
                    this.custom_filters.splice(index)
                }
            }
            this.removeSlug()
        },
        initByRoute() {

            let params = this.$route.query
            let filters = []

            if (params.parks) {

                if (!Array.isArray(params.parks)) params.parks = [params.parks]

                for (let i = 0; i < params.parks.length; i++) {
                    let filter = {
                        id: params.parks[i],
                        ref: 'placesFilter',
                        tag: 'park',
                    }
                    filters.push(filter)
                }
            }
            if (params.countries) {

                if (!Array.isArray(params.countries)) params.countries = [params.countries]

                for (let i = 0; i < params.countries.length; i++) {
                    let filter = {
                        id: params.countries[i],
                        ref: 'placesFilter',
                        tag: 'country',
                    }
                    filters.push(filter)
                }
            }
            if (params.from_date) {
                let filter = {
                    ref: 'datepickerFilter',
                    tag: 'from-date',
                    value: params.from_date
                }
                filters.push(filter)
            }
            if (params.to_date) {
                let filter = {
                    ref: 'datepickerFilter',
                    tag: 'to-date',
                    value: params.to_date
                }
                filters.push(filter)
            }
            if (params.min_price) {
                let filter = {
                    ref: 'priceFilter',
                    tag: 'min-price',
                    value: params.min_price
                }
                filters.push(filter)
            }
            if (params.max_price) {
                let filter = {
                    ref: 'priceFilter',
                    tag: 'max-price',
                    value: params.max_price
                }
                filters.push(filter)
            }
            if (params.main_focus) {
                let filter = {
                    ref: 'mainFocusFilter',
                    tag: 'main-focus',
                    value: params.main_focus
                }
                filters.push(filter)
            }
            if (params.safary_preference) {
                let filter = {
                    ref: 'preferenceFilter',
                    tag: 'safary-preference',
                    value: params.safary_preference
                }
                filters.push(filter)
            }
            if (params.secondary_focus) {

                if (!Array.isArray(params.secondary_focus)) params.secondary_focus = [params.secondary_focus]
                let filter = {
                    ids: [],
                    ref: 'secondActivitiesFilter',
                    tag: 'secondary-focus',
                }

                for (let i = 0; i < params.secondary_focus.length; i++) {
                    filter.ids.push(parseInt(params.secondary_focus[i]))
                }

                filters.push(filter)
            }
            if (params.activity_levels) {
                if (!Array.isArray(params.activity_levels)) params.activity_levels = [params.activity_levels]
                let filter = {
                    values: [],
                    ref: 'activityLevelFilter',
                    tag: 'activity-level',
                }
                for (let i = 0; i < params.activity_levels.length; i++) {
                    filter.values.push(params.activity_levels[i])
                }
                filters.push(filter)
            }

            if (!filters.length && !server_slug) {
                // TODO: This is a very very strange decision. I want to remove it.
                // Instead, we should sort the search result.
                let activity = main_focus_activities.find(x => x.name_short == 'Game drives')
                if (activity) {
                    let filter = {
                        ref: 'mainFocusFilter',
                        tag: 'main-focus',
                        value: activity.id
                    }
                    filters.push(filter)
                }
            }

            for (let i = 0; i < filters.length; i++) {
                this.$refs.filter1.synchronize(filters[i])
                this.$refs.filter2.synchronize(filters[i])
            }

            if (params.ordering) {
                this.selected_order = this.ordering.find(x => x.value == params.ordering).value
            } else {
                this.selected_order = this.ordering[0].value
            }

            if (params.page) {
                this.current_page = parseInt(params.page)
            }
            this.$refs.filter1.init()
            this.$refs.filter2.init()
        },

        // handle_submit: function (e, url) {
        //     e.preventDefault();
        //     this.$v.$touch();

        //     if (this.$v.$invalid || !this.i_certify_these_photos) {
        //         return false;
        //     }

        //     this.isLoading = true;
        //     this.serverError = null;
        //     this.errors = null;

        //     axios.post(url, {
        //         title: this.title,
        //         content: this.content,
        //         friend_recommend: this.friend_recommend,
        //         book_lodging: this.book_lodging,
        //         visit_date_month: parseInt(this.visit_date_month),
        //         visit_date_year: parseInt(this.visit_date_year),
        //         days_booked: parseInt(this.days_booked),
        //         quality_wildlife_rating: parseInt(this.quality_wildlife_rating),
        //         quality_lodging_rating: parseInt(this.quality_lodging_rating),
        //         crowdedness_rating: parseInt(this.crowdedness_rating),
        //         overall_rating: parseInt(this.overall_rating),
        //         selected_animals: this.selected_animals,
        //         selected_activities: this.selected_activities,
        //         pearls_of_wisdom: this.pearls_of_wisdom,
        //         i_certify_these_photos: this.i_certify_these_photos,
        //         like_upload_photos: this.like_upload_photos
        //     })
        //         .then(response => {
        //             this.serverError = null;
        //             if (response.data.status === 'success') {
        //                 if (this.like_upload_photos) {
        //                     document.location.href = "/reviews/park/manage-photos/" + response.data.review_park;
        //                 } else {
        //                     document.location.href = "/reviews/create/park/" + response.data.review_park + "/ack";
        //                 }
        //             } else {
        //                 this.isLoading = false;
        //                 if (response.data.serverError) {
        //                     this.serverError = response.data.serverError;
        //                 }
        //                 this.errors = response.data.errors;
        //             }
        //         })
        //         .catch(err => {
        //             this.isLoading = false;
        //             this.serverError = 'Whoops, something went wrong';
        //         });
        // },
        // set_quality_wildlife_rating(rating) {
        //     this.quality_wildlife_rating = rating;
        // },
        // set_quality_lodging_rating(rating) {
        //     this.quality_lodging_rating = rating;
        // },
        // set_crowdedness_rating(rating) {
        //     this.crowdedness_rating = rating;
        // },
        // set_overall_rating(rating) {
        //     this.overall_rating = rating;
        // }
    },
    mounted: function () {
        this.initByRoute()
    },

    watch: {
        selected_order() {
            this.lazyLoad()
        },
        '$route.path'() {
            // If client remove slug and click "Back"
            if (this.$route.params.slug) {
                let restore_slug = restoreSlug(this.$route.params.slug)
                if (restore_slug) {
                    this.slug = restore_slug
                    this.lazyLoad()    
                }
            }
        }
    }
});
