var app = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        dataForm: {
            uname: '',
            password: '',
            password2: '',
            mobile: '',
            imageCode: '',
            smsCode: '',
            allow: ''
        },
        errorShow: {
            uname: false,
            password: false,
            password2: false,
            mobile: false,
            imageCode: false,
            smsCode: false,
            allow: false
        },
        errorMsg: {
            uname: '请输入5-20个字符的用户',
            password: '请输入8-20位的密码',
            password2: '两次输入的密码不一致',
            mobile: '请输入正确的手机号码',
            imageCode: '请填写图形验证码',
            smsCode: '请填写短信验证码',
            allow: '请勾选用户协议'
        },
        uuid: '',
        imgUrl: ''
    },
    mounted () {
        this.getImgCode()
    },
    methods: {
        getImgCode() {
            this.uuid = generateUUID();
            this.imgUrl = `/image_codes/${this.uuid}/`
        },
        on_submit() { // 提交表单
            this.checkError('uname');
            this.checkError('password');
            this.checkError('password2');
            this.checkError('mobile');
            this.checkError('allow');
            if (this.errorShow.uname || this.errorShow.password || this.errorShow.password2 || this.errorShow.mobile || this.errorShow.allow) {
                window.event.returnValue = false
            }

        },
        checkError(name) { // 提交表单前的错误检查
            if (this.dataForm[name] == '') {
                return this.errorShow[name] = true;
            } else {
                this.errorShow[name] = false;
                switch (name) {
                    case 'uname':
                        let unameRegex = /^[a-zA-Z]\w{1,15}/;
                        if (!unameRegex.test(this.dataForm.uname)) {
                            this.errorShow.uname = true;
                            this.errorMsg.uname = '用户名必须以字母开关2位以上'
                            return
                        }
                        let uurl = `/users/user_repeat/${this.dataForm.uname}/`;
                        axios.get(uurl, {responseType: 'json'})
                            .then(ret => {
                                if (ret.data.count == 1) {
                                    this.errorShow.uname = true;
                                    this.errorMsg.uname = '该用户已经被注册'
                                }
                            });
                        break;
                    case 'password':
                        let passwordRegex = /^\w{6,}/;
                        if (!passwordRegex.test(this.dataForm.password)) {
                            this.errorShow.password = true;
                            this.errorMsg.password = '密码必须6位以上'
                        }
                        break;
                    case 'password2':
                        if(this.dataForm.password != this.dataForm.password2) {
                            this.errorShow.password2 = true;
                        }
                        break;
                    case 'mobile':
                        let mobileRegex = /^1[35896]\d{9}/;
                        if (!mobileRegex.test(this.dataForm.mobile)) {
                            this.errorShow.mobile = true;
                            this.errorMsg.mobile = '手机格式不正确';
                            return
                        }
                        let murl = `/users/phone_repeat/${this.dataForm.mobile}/`;
                        axios(murl, {responseType: 'json'})
                            .then(ret => {
                                if (ret.data.count == 1) {
                                    this.errorShow.mobile = true;
                                    this.errorMsg.mobile = '该手机号已经被注册'
                                }
                            })
                        break;

                }
            }

        }

    }
})