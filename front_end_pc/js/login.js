var vm = new Vue({
    el: '#loginform',
    data: {
        host: 'http://127.0.0.1:8000',
        username: '',
        password: '',
        remember: true,

        error_username: false,
        error_pwd: false,

        error_msg: '',    // 提示信息
    },

    methods: {
        // 检查数据
        check_username: function(){
            if (!this.username) {
                this.error_username = true;
                this.error_msg = '请填写用户名';
            } else {
                this.error_username = false;
                this.error_msg = '';
            }
        },
        check_pwd: function(){
            if (!this.password) {
                this.error_msg = '请填写密码';
                this.error_pwd = true;
            } else {
                this.error_pwd = false;
                this.error_msg = '';
            }
        },

        // 表单提交
        on_submit: function(){
            this.check_username();
            this.check_pwd();

            if (this.error_username === false
                && this.error_pwd === false) {
				//发送登录请求
                axios.post('http://127.0.0.1:8000/users/authorizations/', {
                        username: this.username,
                        password: this.password
                    })
                    .then(response => {
                        // 使用浏览器本地存储保存token
                        sessionStorage.clear();
                        localStorage.clear();
                        if (this.remember) {
                            // 记住登录
                            localStorage.token = response.data.token;
                            localStorage.user_id = response.data.user_id;
                            localStorage.username = response.data.username;
                        } else {
                            // 未记住登录
                            sessionStorage.token = response.data.token;
                            sessionStorage.user_id = response.data.user_id;
                            sessionStorage.username = response.data.username;
                        }
                        // 跳转页面
                        alert("登录成功");
                        location.href = '/index.html';
                    })
                    .catch(error => {
                        if (error.response.status == 400) {
                            this.error_msg = '用户名或密码错误';
                        } else {
                            this.error_msg = '服务器错误';
                        }
                        this.error_pwd = true;
                    })
            }
        },
    }
});