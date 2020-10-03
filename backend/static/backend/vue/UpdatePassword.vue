<template>
    <div>


        <div v-show="showMsg" class="alert alert-dismissible fade show col-11 col-sm-4 bg-army-green text-white ml-auto" role="alert">
            Password updated
            <button type="button" class="close text-dark" aria-label="Close" v-on:click="showMsg=false">
                <i class="nc-icon nc-simple-remove"></i>
            </button>
        </div>


        <form
                id="app"
                @submit="checkForm"
                action="https://vuejs.org/"
                method="post"
        >


            <div class="modal fade" id="updatePassword" tabindex="-1" role="dialog"
                 aria-labelledby="updatePasswordLabel" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="updatePasswordLabel">Update your password</h5>
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                <span aria-hidden="true">&times;</span>
                            </button>
                        </div>

                        <div class="modal-body">
                            <div class="form-group">
                                <label for="currentInputPassword">Current password<span
                                        class="asteriskField">*</span></label>
                                <input id="current-password"
                                       v-model="currentPassword"
                                       type="password"
                                       name="currentPassword" class="form-control" id="currentInputPassword">
                            </div>
                            <div class="form-group">
                                <label for="newInputPassword">New password<span
                                        class="asteriskField">*</span></label>
                                <input id="new-password-1"
                                       v-model="newPassword1"
                                       type="password"
                                       name="newPassword1" class="form-control" id="newInputPassword">
                            </div>
                            <div class="form-group">
                                <label for="confirmInputPassword">Confirm password<span
                                        class="asteriskField">*</span></label>
                                <input id="new-password-2"
                                       v-model="newPassword2"
                                       type="password"
                                       name="newPassword2" class="form-control" id="confirmInputPassword">
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-green-secondary" data-dismiss="modal">Close
                            </button>
                            <button type="button" class="btn btn-green-primary"
                                    v-on:click="checkForm">Save changes
                            </button>
                        </div>

                        <div v-if="errors.length" class="ml-5">
                            <b>Please correct the following error(s):</b>
                            <ul>
                                <li class="text-danger" v-for="error in errors">{{ error }}</li>
                            </ul>
                        </div>
                    </div>

                </div>
            </div>

        </form>
    </div>
</template>

<script>
    export default {
        name: "yas-update-password",
        props: ['url',],

        data() {
            return {
                errors: [],
                currentPassword: '',
                newPassword1: '',
                newPassword2: '',
                showMsg: false,
            }
        },
        methods: {
            checkForm(e) {
                this.errors = [];

                if (!this.currentPassword) {
                    this.errors.push("enter current password");
                }

                if (!this.newPassword1) {
                    this.errors.push("enter new password");
                }

                if (!(this.newPassword1.length < 31)) {
                    this.errors.push("Password too long");
                }

                if (!(this.newPassword1.length > 7)) {
                    this.errors.push("Password too short");
                }

                if (!(this.newPassword1 === this.newPassword2)) {
                    this.errors.push("passwords do not match");
                }


                if (!this.errors.length) {
                    var formData = new FormData();
                    formData.append('new_password', this.newPassword1);
                    formData.append('old_password', this.currentPassword);
                    this.$http.post(this.url, formData, {
                        headers: {
                            'X-CSRFTOKEN': this.$cookies.get('csrftoken')
                        }
                    }).then(response => {
                        const res = response.body.password

                        if (res === 'Invalid old password') {
                            this.errors.push(res);
                            return true
                        }
                        if (res === 'Invalid new password') {
                            this.errors.push('Enter at least 8 characters for new password');
                            return true
                        }
                        if (res === 'Invalid passwords') {
                            this.errors.push(res);
                            jQuery('#updatePassword').modal('hide')
                            return true
                        }
                        jQuery('#updatePassword').modal('hide')
                        this.showMsg = true
                        this.currentPassword = ''
                        this.newPassword1 = ''
                        this.newPassword2 = ''
                        return true
                    });
                }
            }
        },
    }

</script>