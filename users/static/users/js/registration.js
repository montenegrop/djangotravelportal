
Vue.use(VueLoading);
Vue.component('loading', VueLoading);
Vue.use(window.vuelidate.default);
const { required, minLength, email, sameAs, alphaNum, helpers } = window.validators;

export default {

}
var app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#registrationModal',
    data: {
        isLoading: false,
        first_name: '',
        last_name: '',
        screen_name: '',
        email: '',
        password1: '',
        password2: '',
        terms: false,
        csrfmiddlewaretoken: '',
        errors: null,
        serverError: null
    },
    validations: {
        screen_name: {
            required,
            minLength: minLength(4)
        },
        first_name: {
            required,
            minLength: minLength(4)
        },
        last_name: {
            required,
            minLength: minLength(4)
        },
        email: {
            required,
            email
        },
        terms: {
            sameAs: sameAs(() => true),
            required
        },
        password1: {
            required,
            minLength: minLength(8),
            strength: value => (/([a-zA-Z_]*[0-9]*\W*)+/g).test(value)
        },
        password2: {
            sameAsPassword: sameAs('password1')
        }
    },

    methods: {

        handleSubmit: function (e) {
            this.$v.$touch();

            if (this.$v.$invalid) {
                return false;
            }
            this.isLoading = true;
            this.serverError = null;
            this.errors = null;
            var obj_ = this;
            grecaptcha.ready(function () {
                grecaptcha.execute(RECAPTCHA_SITE_KEY, { action: 'registration' }).then(function (token) {
                    axios.post("/registration/", {
                        first_name: obj_.first_name,
                        last_name: obj_.last_name,
                        screen_name: obj_.screen_name,
                        email: obj_.email,
                        password1: obj_.password1,
                        password2: obj_.password2,
                        terms: obj_.terms,
                        token: token,
                    }).then(response => {
                        obj_.isLoading = false;
                        obj_.serverError = null;
                        if (response.data.status === 'success') {
                            location.href = '/signup_email'
                        } else {
                            if (response.data.serverError) {
                                obj_.serverError = response.data.serverError;
                            }
                            obj_.errors = response.data.errors;
                        }
                    }).catch(err => {
                        obj_.isLoading = false;
                        obj_.serverError = 'Whoops, something went wrong';
                    });
                });
            });

        },
    },

});
