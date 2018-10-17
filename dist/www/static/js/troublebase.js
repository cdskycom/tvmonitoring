
var vmMenu = new Vue({
	el:'#menu',
	data:{
		menu:[
		{
			url: '/trouble/dashboard',
			display: '任务概览',
			icon: 'fa fa-dashboard',			
		},
		{
			url: '/trouble/tickets',
			display: '工单管理',
			icon: 'fa fa-edit',

		},
		{
			url: '/trouble/contact',
			display: '联系人',
			icon: 'fa fa-fw fa-user',

		},
		{
			url: '/trouble/wiki',
			display: '知识库',
			icon: 'fa fa-fw fa-wikipedia-w',

		}],
		oldpassword: '',
		newpassword: '',
		confirmpassword: '',
		passvalidateerror: false,  //密码输入校验
		validatemessage: '',
		validateerror: false, //ajax返回结果校验
		message: '',
		messageTitle: ''
	},
	methods:{
		isActive:function(m){
			console.log(window.location);
			return m.url == window.location.pathname;
		}
		
	}
	
});

var vmPass = new Vue({
	el:'#modifypass',
	data:{
		oldpassword: '',
		newpassword: '',
		confirmpassword: '',
		passvalidateerror: false,  //密码输入校验
		validatemessage: '',
		validateerror: false, //ajax返回结果校验
		message: '',
		messageTitle: ''
	},
	methods:{
		doModifyPass:function(){
			var that = this;
			that.passvalidateerror = false;
			that.validateerror = false;
			if(!this.validatePass(this.newpassword,this.confirmpassword)){
				return;
			}
			var oldpassword = CryptoJS.SHA1(userinfo.account + ':' + this.oldpassword).toString();
			var newpassword = CryptoJS.SHA1(userinfo.account + ':' + this.newpassword).toString();

			axios.post('/api/user/modifypassword/' + userinfo.uid, {oldpassword: oldpassword, newpassword: newpassword}).then(function(res){
				
				if(res.data.error){
						that.validateerror = true;
						that.messageTitle = "处理失败";
						
					}else{
						that.validateerror = false;
						that.messageTitle = "处理成功,请重新登录"
								
					}
					that.message = res.data.message;
					
					that.showResultBox();
				
			});
			

		},
		validatePass: function(newpass, confirm){
			that = this;
			if(newpass == confirm){
				this.passvalidateerror = false;
				this.validatemessage = "";
				return true;
			}else{
				this.passvalidateerror = true;
				this.validatemessage = "两次输入的密码不一致";
				return false;
			}
		},
		showResultBox:function(){
			$('#modal-modifypass').modal('hide');
			$('#modal-message-pass').modal('show');
			$('#modal-message-pass').on('hidden.bs.modal',function(e){
				window.location = '/signin'
			});
		},
		
	}
	
});
	
