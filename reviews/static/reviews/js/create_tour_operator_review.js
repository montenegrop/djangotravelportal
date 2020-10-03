Vue.component('star-rating', VueStarRating.default);
Vue.use(window.vuelidate.default);

Vue.config.devtools = true

const { required, minLength, email, sameAs, alphaNum, helpers, requiredIf, minValue, maxLength, between } = window.validators;

const validateIf = (prop, validator) =>
  helpers.withParams({ type: 'validatedIf', prop }, function(value, parentVm) {
    return helpers.ref(prop, this, parentVm) ? validator(value) : true
  })

var reviews_create_app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#reviews_create_tour_operator_review',
    components: [VueStarRating],
    data: {
        isLoading: false,
        errors: [],
        serverError: null,
        review_title: '',
        review_copy: '',
        booking_with_this_company: null,
        visit_date_month: -2,
        current_month: (new Date()).getMonth() + 1,
        visit_date_year: -2,
        current_year: (new Date()).getFullYear(),
        days_booked: null,
        safari_type_id: null,
        pearls_of_wisdom: '',
        pearls_of_wisdom_kilimanjaro: '',
        friend_recommend: null,
        selected_parks: [],
        selected_countries: [],
        selected_animals: [],
        selected_activities: [],
        i_certify_these_photos: false,
        like_upload_photos: false,
        meet_and_greet_rating: 0,
        vehicle_rating: 0,
        responsiveness_rating: 0,
        safari_quality_rating: 0,
        itinerary_quality_rating: 0,
        overall_rating: 0,
        crowdedness_rating: 0,
        reached_summit: null,
        take_medications: null,
        routes_to_climb_json: routes_to_climb_json,
        route_to_climb: 'unselected',
        other_route_to_climb: '',
        find_out: '',
        find_out_website: '',
        kilimanjaro_content: '',
        min_length_150: 150,
        max_length_1000: 1000,
        max_length_15000: 15000,
        max_length_300: 300,
    },
    validations() {
        var min = 0
        var min2 = -2
        if (this.booking_with_this_company) {
            min = 1
            min2 = -1
        }
        else {
            min = 0
            min2 = -2
        }
        return {
            review_title: {
                required,
            },
            review_copy: {
                required,
                minLength: minLength(150),
                maxLength: maxLength(15000),
            },
            booking_with_this_company: {
                required,
            },
            find_out: {
                required,
            },
            find_out_website: {
                required: requiredIf(form => {
                    return (form.find_out == "Website");
                })
            },
            i_certify_these_photos: {
                required,
            },
            visit_date_month: {
                minValue: minValue(min2)
            },
            visit_date_year: {
                minValue: minValue(min2)
            },
            days_booked: {
                required: requiredIf(form => {
                    return form.booking_with_this_company;
                })
            },
            friend_recommend: {
                required: requiredIf(form => {
                    return form.booking_with_this_company;
                })
            },
            safari_type_id: {
                required: requiredIf(form => {
                    return form.booking_with_this_company
                })
            },
            selected_animals: {
                required: false
            },
            selected_activities: {
                required: false
            },
            selected_countries: {
                required: requiredIf(form => {
                    return form.booking_with_this_company
                })
            },
            selected_parks: {
                required: requiredIf(form => {
                    return form.selected_countries.length > 0
                })
            },
            route_to_climb: {
                requiredIf: requiredIf(form => {
                    return this.kilimanjaro_selected && !form.other_route_to_climb;
                }),
            },
            other_route_to_climb: {
                requiredIf: requiredIf(form => {
                    return form.kilimanjaro_selected && !form.route_to_climb;
                })
            },
            kilimanjaro_content: {
                correctLength: validateIf('kilimanjaro_selected', minLength(150)),
                requiredIf: requiredIf(form => {
                    return form.kilimanjaro_selected;
                }),
                maxLength: maxLength(15000),
            },
            reached_summit: {
                requiredIf: requiredIf(form => {
                    return form.kilimanjaro_selected;
                })
            },
            take_medications: {
                requiredIf: requiredIf(form => {
                    return form.kilimanjaro_selected;
                })
            },
            meet_and_greet_rating: {
                minValue: minValue(min)
            },
            vehicle_rating: {
                minValue: minValue(min)
            },
            safari_quality_rating: {
                minValue: minValue(min)
            },
            responsiveness_rating: {
                minValue: minValue(1)
            },
            itinerary_quality_rating: {
                minValue: minValue(1)
            },
            overall_rating: {
                minValue: minValue(1)
            },
            crowdedness_rating: {
                validateIf: validateIf('kilimanjaro_selected', minValue(1)),
            },
        };
    },
    methods: {
        handle_submit: function (e, url) {
            e.preventDefault();
            this.$v.$touch();
            console.log(this.$v)
            if (this.$v.$invalid || !this.i_certify_these_photos) {
                console.log(this.errors)
                return false;
            }



            this.isLoading = true;
            this.serverError = null;
            this.errors = null;

            axios.post(url, {
                review_title: this.review_title,
                review_copy: this.review_copy,
                did_not_go: !this.booking_with_this_company,
                start_date_month: parseInt(this.visit_date_month),
                start_date_year: parseInt(this.visit_date_year),
                days_booked: parseInt(this.days_booked),
                safari_type_id: this.safari_type_id,
                pearls_of_wisdom: this.pearls_of_wisdom,
                pearls_of_wisdom_kilimanjaro: this.pearls_of_wisdom_kilimanjaro,
                friend_recommend: this.friend_recommend,
                selected_countries: this.selected_countries,
                selected_parks: this.selected_parks,
                selected_animals: this.selected_animals,
                selected_activities: this.selected_activities,
                i_certify_theses_photos: this.i_certify_these_photos,
                like_upload_photos: this.like_upload_photos,
                meet_and_greet_rating: parseInt(this.meet_and_greet_rating),
                vehicle_rating: parseInt(this.vehicle_rating),
                responsiveness_rating: parseInt(this.responsiveness_rating),
                safari_quality_rating: parseInt(this.safari_quality_rating),
                itinerary_quality_rating: parseInt(this.itinerary_quality_rating),
                overall_rating: parseInt(this.overall_rating),
                countries_json: countries_json,
                find_out: this.find_out,
                find_out_website: this.find_out_website,
                reached_summit: this.reached_summit,
                take_medications: this.take_medications,
                route_to_climb: this.route_to_climb,
                other_route_to_climb: this.other_route_to_climb,
                is_kilimanjaro: this.kilimanjaro_selected,
                crowdedness_rating_kilimanjaro: this.crowdedness_rating,
                content_kilimanjaro: this.kilimanjaro_content,

            })
                .then(response => {
                    this.serverError = null;
                    if (response.data.status === 'success') {
                        if (this.like_upload_photos) {
                            document.location.href = "/reviews/tour-operator/manage-photos/" + response.data.review_tour_operator;
                        } else {
                            document.location.href = "/reviews/create/tour-operator/" + response.data.review_tour_operator + "/ack";
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
        set_meet_and_greet_rating(rating) {
            this.meet_and_greet_rating = rating;
        },
        set_vehicle_rating(rating) {
            this.vehicle_rating = rating;
        },
        set_responsiveness_rating(rating) {
            this.responsiveness_rating = rating;
        },
        set_safari_quality_rating(rating) {
            this.safari_quality_rating = rating;
        },
        set_itinerary_quality_rating(rating) {
            this.itinerary_quality_rating = rating;
        },
        set_overall_rating(rating) {
            this.overall_rating = rating;
        },
        set_crowdedness_rating(rating) {
            this.crowdedness_rating = rating;
        },
        charactersCounter(dataVariable) {
            var char = dataVariable.length;
            return char;
        },
    },
    mounted: function () {
        this.$refs.tour_form.classList.remove('d-none');
        console.log(this.$v, 999)
    },
    computed: {
        kilimanjaro_selected: function () {
            for (let i = 0; i < countries_json.length; i++) {
                for (let j = 0; j < countries_json[i].parks.length; j++) {
                    if (countries_json[i].parks[j].name == "Kilimanjaro National Park") {
                        return (this.selected_parks.indexOf(countries_json[i].parks[j].id) != -1)
                    }
                }
            }
            return false;
        },
        parks_to_select: function () {
            let selected_countries = [];
            for (let i = 0; i < this.selected_countries.length; i++) {
                selected_countries.push(this.selected_countries[i])

            }

            let countries = countries_json.filter(country => selected_countries.indexOf(country.id) !== -1);
            let parks_to_select = [];
            for (let i = 0; i < countries.length; i++) {
                for (let j = 0; j < countries[i].parks.length; j++) {
                    parks_to_select.push(countries[i].parks[j]);
                }
            }
            return parks_to_select;
        },
    },
});
