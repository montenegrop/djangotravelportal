Vue.component('operator', {
    template: '#operator_component',
    delimiters: ['[[', ']]'],
    props: {
        operator: {
            type: Object,
            required: true
        }
    },
    methods: {
        getTourUrl(operator) {
            return '/c/' + operator.slug
        },

        heartChange(operator) {
            var $counter = $('.far.fa-stack-1x.counter.fav-counter')
            let count = $counter.text()
            count = count ? parseInt(count) : 0
            operator.is_fav = !operator.is_fav
            if (operator.is_fav) {
                $(".fa-nav-heart").addClass('fa-beat')
                $.get('/add_operator_fav/' + operator.id + '/', null, function (res) {
                    if (res['status'] == 'ok') {
                        $counter.text(res['count'])
                    } else {
                        operator.is_fav = !operator.is_fav
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
                $.get('/delete_operator_fav/' + operator.id + '/', null, function (res) {
                    if (res['status'] == 'ok') {
                        $counter.text(res['count'])
                    } else {
                        operator.is_fav = !operator.is_fav
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

    },
    computed: {
        card_size_classes() {
            let classes = ' card p-3 mb-5 bg-white rounded col-l'
            if (this.operator) {
                if (this.operator.is_featured) {
                    return 'shadow-featured border-featured mx-2' + classes
                } else {
                    return 'shadow-sm mx-3 border card-size' + classes
                }
            }
            return classes
        }
    }
})

Vue.component('star-rating', VueStarRating.default);
Vue.use(window.vuelidate.default);
const {required, minLength, email, sameAs, alphaNum, helpers, requiredIf, minValue} = window.validators;

var app = new Vue({
    router: new VueRouter({
        mode: 'history',
        routes: [
            { path: '/african-safari-tour-operators/:slug' }
        ]
    }),
    delimiters: ['[[', ']]'],
    el: '#all_tour_operators',
    components: {
        VueStarRating
    },
    data: {
        // isLoading: false,
        // errors: [],
        // serverError: null,
        // title: '',
        // content: '',
        // friend_recommend: false,
        // book_lodging: false,
        // visit_date_month: -2,
        // current_month: (new Date()).getMonth() + 1,
        // visit_date_year: -2,
        // current_year: (new Date()).getFullYear(),
        // days_booked: -2,
        // quality_wildlife_rating: 0,
        // quality_lodging_rating: 0,
        // crowdedness_rating: 0,
        // overall_rating: 0,
        // selected_animals: [],
        // animals_json: animals_json,
        // selected_activities: [],
        // activities_json: activities_json,
        // pearls_of_wisdom: '',
        // i_certify_these_photos: false,
        // like_upload_photos: false,
        // ===========================
        custom_filters: [],
        touroperators: [],
        is_loading: true,
        current_page: 1,
        pagination: {
            positions_total: null,
            positions_on_page: null,
            showing_from: null,
            showing_to: null,
        },
        ordering: [
            { id: null, title: 'YAScore', value: '-yas_score' },
            { id: 1, title: 'Alphabetical (A-Z)', value: 'name' },
            { id: 2, title: 'Reverse alphabetical (Z-A)', value: '-name' },
            { id: 3, title: 'Highest average rating', value: '-average_rating' },
            { id: 4, title: 'Most reviewed', value: 'reviews_count' },
            { id: 5, title: 'Most tour packages', value: '-packages_count' },
            { id: 6, title: 'Recently reviewed', value: '-last_review_date' },
            { id: 7, title: 'Recently added', value: '-id' }
        ],
        selected_order: '-id',
        lazytimer: null,
        is_inited: false,
        filters_conveyor: [],
        slug: server_slug
    },
    validations: {
        title: {
            required,
        },
        content: {
            required,
            minLength: minLength(150)
        },
        i_certify_these_photos: {
            required,
        },
        days_booked: {
            minValue: minValue(-1)
        },
        visit_date_month: {
            minValue: minValue(-1)
        },
        visit_date_year: {
            minValue: minValue(-1)
        },
        quality_wildlife_rating: {
            minValue: minValue(1)
        },
        quality_lodging_rating: {
            minValue: minValue(1)
        },
        crowdedness_rating: {
            minValue: minValue(1)
        },
        overall_rating: {
            minValue: minValue(1)
        },
        selected_animals: {
            required,
            minLength: minLength(1)
        },
        selected_activities: {
            required,
            minLength: minLength(1)
        },

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
            this.touroperators = []

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
                if (filter.tag == 'luxury-focus') {
                    filters.luxury_focus = filter.id
                }
                if (filter.tag == 'rating') {
                    filters.rating = filter.id
                }
                if (filter.tag == 'languages') {
                    if (!filters.languages) filters.languages = []
                    filters.languages.push(filter.id)
                }
                if (filter.tag == 'headquarters') {
                    if (!filters.headquarters) filters.headquarters = []
                    filters.headquarters.push(filter.id)
                }
                if (filter.tag == 'that') {
                    if (!filters.that) filters.that = []
                    filters.that.push(filter.id)
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

            axios.get('/api/tour-operators/', { params: filters })
                .then(function (response) {
                    let last_conveyor_index = app.filters_conveyor.length - 1
                    delete response.config.params['slug']
                    let json_params = JSON.stringify(response.config.params)
                    // this condition is necessary to avoid overwriting the response of old query
                    if (app.filters_conveyor[last_conveyor_index] == json_params) {
                        app.touroperators = response.data.results
                        app.pagination.positions_total = response.data.count
                        app.pagination.positions_on_page = response.data.results.length
                        app.is_loading = false
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
            if (params.luxury_focus) {
                let filter = {
                    ref: 'luxuryFocusFilter',
                    tag: 'luxury-focus',
                    value: params.luxury_focus
                }
                filters.push(filter)
            }
            if (params.rating) {
                let filter = {
                    ref: 'ratingFilter',
                    tag: 'rating',
                    value: params.rating
                }
                filters.push(filter)
            }
            if (params.languages) {

                if (!Array.isArray(params.languages)) params.languages = [params.languages]
                let filter = {
                    ids: [],
                    ref: 'languagesFilter',
                    tag: 'languages',
                }

                for (let i = 0; i < params.languages.length; i++) {
                    filter.ids.push(parseInt(params.languages[i]))
                }

                filters.push(filter)
            }
            if (params.headquarters) {

                if (!Array.isArray(params.headquarters)) params.headquarters = [params.headquarters]
                let filter = {
                    ids: [],
                    ref: 'headquartersFilter',
                    tag: 'headquarters',
                }

                for (let i = 0; i < params.headquarters.length; i++) {
                    filter.ids.push(parseInt(params.headquarters[i]))
                }

                filters.push(filter)
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
    mounted() {
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
