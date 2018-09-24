
var vm = new Vue({
	el:'#app',
	data:{
		troubleCount: 0,
		acptTroubleCount: 0,
		dealingTroubleCount: 0,
		taskCount: 0,
		tasks: {
			itemsPerPage: 10,
			totalPage: 1,
			currentPage: 1,
			totalItems: 0,
			taskList: [],
			currentTask: '',
			curTaskLogs: '',
			toNextProvider: -1, //派单到下一个厂家的ID
			taskReply: ''
		},
		providers: '',
		validateerror: false,
		validatemessage:'',
		messageTitle: '',  //消息弹窗标题
		message: ''		   //消息弹窗内容
	},
	computed:{
		hasFinishedPermission:function(){
			return userinfo.permission.indexOf('FIN') != -1;
		}
	},
	methods:{
		submit:function(event){
			
		},
		setCurrentTask:function(t){
			// this.tasks.currentTask = t;
		},
		taskDetail:function(t){
			that = this;
			that.tasks.currentTask = t;
			that.tasks.curTaskLogs = '';
			$('#collapseOne').collapse('hide');

		},
		getLogs:function(id){
			if(this.tasks.curTaskLogs == ''){
				that = this;
				var url = baseUrl + 'api/troubleticket/getlogs?' + 'troubleid=' + id;
				axios.get(url).then(function(res){
					that.tasks.curTaskLogs = res.data.logs;
				});
			}

		},
		doTransit:function(){
			that = this;
			var url = baseUrl + 'api/troubleticket/getprovider';
			axios.get(url).then(function(res){
				that.providers = res.data.providers;
				console.log(this.providers);
			});

		},
		//任务工单处理
		dealTask:function(t){
			that = this;
			//回单直接回给派单人所在部门,转派工单则直接使用选择的厂家
			nextprovider = this.tasks.toNextProvider;
			if(t == 'REPLY'){
				nextprovider = this.tasks.currentTask.assigner.support_provider.id;
			}
			axios.post(baseUrl + 'api/troubleticket/dealingtask',{
					dealingtype: t,
					taskid:this.tasks.currentTask.id,
					nextprovider: nextprovider,
					reply: this.tasks.taskReply,
					uid: userinfo.uid
				}).then(function(res){
					if(res.data.error){
					
						that.validateerror = true;
						that.messageTitle = "处理失败";
						
					}else{
						that.validateerror = false;
						that.messageTitle = "处理成功"
						
					}
					that.message = res.data.message;
					$('#modal-message').modal('show');
					$('#modal-message').on('hidden.bs.modal', function (e) {
						location.reload();
					});
				
			});
		},

		handletopage:function(playload){
				that = this;
				this.tasks.currentPage = playload.page;
				var url = baseUrl + 'api/toubleticket/gettask?page=' + this.tasks.currentPage + '&items_perpage=' + 
						this.tasks.itemsPerPage + '&uid=' + userinfo.uid + '&pid=' + userinfo.pid;
				
				axios.get(url).then(function(res){
					that.tasks.taskList = res.data.tasks;
				});

		},
		handleitemschange:function(playload){
			that = this;
			this.tasks.itemsPerPage = playload.newitems;
			this.currentPage = 1;
			var url = baseUrl + 'api/toubleticket/gettask?page=' + this.tasks.currentPage + '&items_perpage=' + 
						this.tasks.itemsPerPage + '&uid=' + userinfo.uid + '&pid=' + userinfo.pid;
			axios.get(url).then(function(res){
				that.tasks.totalItems = res.data.totalitems;
				that.tasks.totalPage = res.data.totalpage;
				that.tasks.taskList = res.data.tasks;

			});

		}
		
	},

	created: function () {
    	var url = baseUrl + 'api/toubleticket/statistic?' + 'uid=' + userinfo.uid + '&pid=' + userinfo.pid;
    	that = this
		axios.get(url).then(function(res){
			that.troubleCount = res.data.troubleCount;
			that.acptTroubleCount = res.data.acptTroubleCount;
			that.dealingTroubleCount = res.data.dealingTroubleCount;
			that.taskCount = res.data.taskCount;
			
		});
		var taskUrl = baseUrl + 'api/toubleticket/gettask?page=' + this.tasks.currentPage + '&items_perpage=' + 
			this.tasks.itemsPerPage + '&uid=' + userinfo.uid + '&pid=' + userinfo.pid;
		axios.get(taskUrl).then(function(res){
			that.tasks.totalItems = res.data.totalitems;
			that.tasks.totalPage = res.data.totalpage;
			that.tasks.taskList = res.data.tasks;
		});
  	},
	filters:{
		//日期格式化过滤器
		DateTimeFtt: TV_DateTimeFtt.formatter,
		//故障级别显示过滤器
		levelStr:function(str){
			switch(str){
				case '0': return '紧急故障';
				case '1': return '一般故障';
				case '2': return '感知问题';
				default: return '未知级别';
			}
		},
		//长文本截取过滤器
		shortcutStr:function(val,length){
			if(val.length > length){
				return val.substr(0,length) + '...';
			}else{
				return val;
			}
		},
		convertType:function(val){
			switch(val){
				case 'CREATE': return '创建工单';
				case 'REPLY': return '回复工单';
				case 'TRANSIT': return '转派工单';
				case 'FINISHED': return '结束工单';
				default: return '位置动作';
			}
		}
		
	}
});
	

	// window.onload = function(){
	// 	if(ID){
	// 		axios.get('/api/users/' + ID).then(res=>{initVM(res.data.user,'edit')});
	// 	}
	// 	else{
	// 		initVM({
	// 			account:'',
	// 			password:'',
	// 			name:'',
	// 			is_admin:0
	// 		},'add')
	// 	}

	// }