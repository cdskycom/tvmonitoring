
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

		}]
	},
	methods:{
		isActive:function(m){
			console.log(window.location);
			return m.url == window.location.pathname;
		}
		
	}
	
});
	
