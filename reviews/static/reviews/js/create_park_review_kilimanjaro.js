Vue.component('star-rating', VueStarRating.default);
Vue.use(window.vuelidate.default);
const {required, minLength, email, sameAs, alphaNum, helpers, requiredIf, minValue, maxLength} = window.validators;

var reviews_create_app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#reviews_create_park_review',
    components: [VueStarRating],
    data: {
        isLoading: false,
        errors: [],
        serverError: null,
        title: '',
        content: '',
        friend_recommend: null,
        book_lodging: null,
        visit_date_month: -2,
        current_month: (new Date()).getMonth() + 1,
        visit_date_year: -2,
        current_year: (new Date()).getFullYear(),
        days_booked: -2,
        quality_wildlife_rating: 0,
        quality_lodging_rating: 0,
        crowdedness_rating: 0,
        overall_rating: 0,
        selected_animals: [],
        animals_json: animals_json,
        selected_activities: [],
        activities_json: activities_json,
        pearls_of_wisdom: '',
        i_certify_these_photos: false,
        like_upload_photos: false,
        //kilimanjaro
        reached_summit: null,
        take_medications: null,
        route_to_climb: 'unselected',
        other_route_to_climb: '',
        routes_to_climb_json: routes_to_climb_json,
        min_length_150: 150,
        max_length_1000: 1000,
        max_length_15000: 15000,
        max_length_300: 300,
    },
    validations: {
        title: {
            required,
        },
        content: {
            required,
            minLength: minLength(150)
        },
        friend_recommend: {
            required,
        },
        i_certify_these_photos: {
            required,
        },
        reached_summit: {
            required
        },
        take_medications: {
            required
        },
        pearls_of_wisdom: {
            required
        },
        visit_date_month: {
            minValue: minValue(-1)
        },
        visit_date_year: {
            minValue: minValue(-1)
        },
        days_booked: {
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
            required: false
        },
        selected_activities: {
            required: false
        },
        route_to_climb: {
            requiredIf: requiredIf(form => {
                !form.other_route_to_climb;
            }),
            maxLength: maxLength(2)
        },
        other_route_to_climb: {
            requiredIf: requiredIf(form => {
                return !form.route_to_climb;
            })
        },
    },
    methods: {
        handle_submit: function (e, url) {
            e.preventDefault();
            this.$v.$touch();

            if (this.$v.$invalid) {
                return false;
            }

            this.isLoading = true;
            this.serverError = null;
            this.errors = null;


            axios.post(url, {
                title: this.title,
                content: this.content,
                friend_recommend: this.friend_recommend,
                book_lodging: this.book_lodging,
                visit_date_month: parseInt(this.visit_date_month),
                visit_date_year: parseInt(this.visit_date_year),
                days_booked: parseInt(this.days_booked),
                quality_wildlife_rating: parseInt(this.quality_wildlife_rating),
                quality_lodging_rating: parseInt(this.quality_lodging_rating),
                crowdedness_rating: parseInt(this.crowdedness_rating),
                overall_rating: parseInt(this.overall_rating),
                selected_animals: this.selected_animals,
                selected_activities: this.selected_activities,
                pearls_of_wisdom: this.pearls_of_wisdom,
                i_certify_these_photos: this.i_certify_these_photos,
                like_upload_photos: this.like_upload_photos,
                reached_summit: this.reached_summit,
                take_medications: this.take_medications,
                route_to_climb: this.route_to_climb,
                other_route_to_climb: this.other_route_to_climb
            })
                .then(response => {
                    this.serverError = null;

                    if (response.data.status === 'success') {
                        if (this.like_upload_photos) {
			    document.location.href = "/reviews/park/manage-photos/" + response.data.review_park;
			} else {
			    document.location.href = "/reviews/create/park/" + response.data.review_park + "/ack";
			}
                    } else {
                        this.isLoading = false;
                        if (response.data.serverError) {
                            this.serverError = response.data.serverError;
                        }
                        this.errors = response.data.errors;
                    }
                })
                .catch(err => {
                    this.isLoading = false;
                    this.serverError = 'Whoops, something went wrong';
                });
        },
        set_quality_wildlife_rating(rating) {
            this.quality_wildlife_rating = rating;
        },
        set_quality_lodging_rating(rating) {
            this.quality_lodging_rating = rating;
        },
        set_crowdedness_rating(rating) {
            this.crowdedness_rating = rating;
        },
        set_overall_rating(rating) {
            this.overall_rating = rating;
        },
        charactersCounter(dataVariable) {
            var char = dataVariable.length;
            return char;
        },
    },
    mounted: function () {
        this.$refs.park_form.classList.remove('d-none');
    },
    computed: {
        charactersLeft() {
            var char = this.content.length;
            return char;
        },
    },

    watch: {
        //country: function () {
        //    this.filter_park();
        //}
    }
});
