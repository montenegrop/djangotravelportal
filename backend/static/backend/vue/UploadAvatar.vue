<template>
    <div id="avatarProfile" class="text-center">
        <vue-avatar
                v-show="false"
                :image="loadedAvatar"
                :width=150
                :height=150
                :rotation="rotation"
                :scale="scale"
                ref="vueavatar"
                @vue-avatar-editor:image-ready="onImageReady"
        >
        </vue-avatar>
        <img ref="image">
        <a v-show="!editor" type="button" class="center my-1" @click="trigger">Change
            avatar
        </a>
        <button v-show="editor" type="button" class="btn btn-green-primary w-80 center my-1" v-on:click="saveClicked">
            Confirm
        </button>
        <button v-show="editor" type="button" class="btn btn-green-secondary w-80 center my-1" v-on:click="cancelSave">Cancel
        </button>
    </div>
</template>

<script>
    import {VueAvatar} from 'vue-avatar-editor-improved'

    export default {
        name: "yas-upload-avatar",
        components: {VueAvatar},
        props: ['image',],

        data() {
            return {
                editor: false,
                currentAvatar: {},
                firstLoaded: true,
            }
        },
        methods: {
            cancelSave() {
                this.editor = false
                this.$refs.image.src = this.currentAvatar.toDataURL()
            },
            trigger() {
                this.editor = true
                this.$refs.vueavatar.$refs.input.click()
            },
            saveClicked() {
                this.editor = false
                var img = this.$refs.vueavatar.getImageScaled()
                this.currentAvatar = img
                this.$refs.image.src = img.toDataURL()
                var formData = new FormData();
                formData.append('avatar', img.toDataURL());
                this.submit(img.toDataURL());
            },
            onImageReady() {
                console.log('imageready')
                // const uploaded = this.$refs.vueavatar.getImage()
                var img = this.$refs.vueavatar.getImageScaled()
                if (this.firstLoaded) {
                    this.currentAvatar = img
                    this.firstLoaded = false
                }
                console.log(typeof img)
                this.$refs.image.src = img.toDataURL()
            },
            submit(avatar) {
                this.error = ''
                var formData = new FormData();
                formData.append('avatar', avatar);
                try {
                    const x = this.$http.post(`/member/avatar`, formData, {
                        headers: {
                            'X-CSRFTOKEN': this.$cookies.get('csrftoken')
                        }
                    });
                    this.success = 'Avatar uploaded!'
                } catch (e) {
                    if (e.body && e.body.message) {
                        this.error = e.body.message
                    } else {
                        this.error = 'Avatar was not uploaded'
                    }
                }
            }
        },
        computed: {
            loadedAvatar: function () {
                // return '/static/img/avatar/Cheetah.png'
                if (this.firstLoaded) {
                    console.log(this.image)

                    return this.image
                }
            }
        }
    }

</script>
