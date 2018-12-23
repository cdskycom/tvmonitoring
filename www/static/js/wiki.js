var vm = new Vue({
	el: '#app',
	data: {
		maxSize: 10485760, //文件最大尺寸10M
		file: '',
		filename: '',
		wikitags: [], //案例关联的标签数组
		wikiSubject: '',
		wikiSummary: '',
		attachMentId: '',
		uploadPercentage: 0,
		prohibited: false, //禁止上传文件
		message: '',
		tags: [], //所有标签
		newTag: '',
		validateerror: '',
		validatemessage:'',
		messageTitle: '',
		wikis: {
			currentPage: 1,
			itemsPerPage: 10,
			totalItems: 0,
			totalPage: 1,
			wikiList: [], //当前显示的案例列表
			filterByTag: '',
			tagNameForFilter:''
		},
	},
	computed:{
		wikiurl:function(){
			var url = '/api/getwiki?page=' + this.wikis.currentPage + 
			'&items_perpage=' + this.wikis.itemsPerPage
			if(this.wikis.filterByTag){
				url = url + '&tag=' + this.wikis.filterByTag;
			}
			return url;
		},
		tagFiltered:function(){
			return this.wikis.filterByTag == '' ? false : true
		}
	},
	methods: {
		handleFileUpload: function() {
			this.file = this.$refs.file.files[0];
			this.filename = this.file.name;
			if (this.file.size > this.maxSize) {
				this.prohibited = true;
				this.message = "单个文件不能大于10M"
				return;
			} else {
				this.prohibited = false;
				this.message = ""
			}
		},
		submitFile: function() {
			var formData = new FormData();

			/*
			    Add the form data we need to submit
			*/
			formData.append('uid', userinfo.uid);

			if (this.file != '') {
				formData.append('ufile', this.file);
			}

			that = this;
			/*
			  Make the request to the POST /single-file URL
			*/
			axios.post(
				'/single-file',
				formData,
				{
					headers:{
						'Content-Type': 'multipart/form-data'
					},
					onUploadProgress: function(progressEvent) {
							that.uploadPercentage = parseInt(Math.round((progressEvent.loaded * 100) / progressEvent.total));
						}.bind(that)
				}).then(function(res){
					that.file = '';
					if(res.data.error){
						that.message = res.data.message;
						that.attachMentId = '';
					} else {
						that.message = "文件上传成功!!";
						that.attachMentId = res.data.id;
					}

				}).catch(function(){
					console.log('FAILURE!!');
				});
			// axios.post('/single-file',
			// 		formData, {
			// 			headers: {
			// 				'Content-Type': 'multipart/form-data'
			// 			},
			// 			onUploadProgress: function(progressEvent) {
			// 				that.uploadPercentage = parseInt(Math.round((progressEvent.loaded * 100) / progressEvent.total));
			// 			}.bind(that)
			// 		}).then(function(res) {
			// 		that.file = '';
			// 		if (res.data.error) {

			// 			that.message = res.data.message;
			// 			that.attachMentId = '';

			// 		}else{
			// 			that.message = "文件上传成功!!";
			// 			that.attachMentId = res.data.id;
			// 		}
			// 	})
			// 	.catch(function() {
			// 		console.log('FAILURE!!');
			// 	});
		},
		
		
		addFile: function() {
			this.$refs.file.click();
		},
		//查询文件尺寸
		returnFileSize: function(number) {
			if (number < 1024) {
				return number + 'bytes';
			} else if (number >= 1024 && number < 1048576) {
				return (number / 1024).toFixed(1) + 'KB';
			} else if (number >= 1048576) {
				return (number / 1048576).toFixed(1) + 'MB';
			}
		},
		addTag: function() {
			if (this.newtag != '') {
				that = this;
				axios.post('/addtag', {
					tagname: this.newTag
				}).then(function() {
					that.getAllTags();
				}).catch(function() {
					console.log('FAILURE!!');
				})
			}
		},
		getAllTags: function() {
			that = this;
			axios.get('/tags').then(function(res) {
				that.tags = res.data.tags;
			});
		},
		getWikiByTag: function(tagId, tagName) {
			this.wikis.filterByTag = tagId;
			this.wikis.tagNameForFilter = tagName;
			that = this;
			axios.get(this.wikiurl).then(function(res){
				that.wikis.totalItems = res.data.totalitems;
				that.wikis.totalPage = res.data.totalpage;
				that.wikis.wikiList = res.data.wikis;

			});

		},
		addTagToWiki: function(tagId, key) {
			var tagIndex = -1;
			tagIndex = this.getTagIndex(tagId);
			if (tagIndex > -1) {
				this.wikitags.splice(tagIndex, 1)
			} else {
				this.wikitags.push(tagId)
			}


		},
		getTagIndex: function(id) {
			for (var i = 0; i < this.wikitags.length; i++) {
				if (id == this.wikitags[i]) {
					return i;
				}
			}
			return -1;
		},
		tagSelected: function(id) {
			return this.getTagIndex(id) > -1 ? true : false;
		},
		addWiki: function() {
			that = this;
			axios.post(
				'/addwiki',
				{
					subject: this.wikiSubject,
					summary: this.wikiSummary,
					tags: this.wikitags,
					attachment: this.attachMentId
				}
				).then(function(res){
					if(res.data.error){
					
						that.validateerror = true;
						that.messageTitle = "处理失败";
						
					}else{
						that.validateerror = false;
						that.messageTitle = "处理成功"
						
					}
					that.message = res.data.message;
					that.subject = '';
					that.summary = '';
					that.wikitags = [];
					that.attachMentId = '';
					that.file = '';
					that.filename = '';
					that.showResultBox();
				}).catch(function(error){
					that.validateerror = true;
					that.messageTitle = "处理失败";
					if(error.response){
						that.message = "服务器处理失败" + error.response.status;
					}else{
						that.message = error.message;
					}
					that.showResultBox();
					// return Promise.reject(error);
				});

		},
		showResultBox:function(){
			$('#modal-message').modal('show');
			$('#modal-message').on('hidden.bs.modal', function (e) {
				if(that.validateerror){
					$('#modal-createwiki').modal('show');
				}else{
					location.reload();
				}
			});
		},

		handleitemschange:function(playload){
			that = this;
			this.wikis.itemsPerPage = playload.newitems;
			this.wikis.currentPage = 1;
			
			axios.get(this.wikiurl).then(function(res){
				that.wikis.totalItems = res.data.totalitems;
				that.wikis.totalPage = res.data.totalpage;
				that.wikis.wikiList = res.data.wikis;

			});

		},
		handletopage:function(playload){
			that = this;
			this.wikis.currentPage = playload.page;

			
			axios.get(this.wikiurl).then(function(res){
				that.wikis.wikiList = res.data.wikis;

			});
		},
	

	},

	//初始化页面数据
	created: function(){
		this.getAllTags();
		axios.get(this.wikiurl).then(function(res){
			that.wikis.totalItems = res.data.totalitems;
			that.wikis.totalPage = res.data.totalpage;
			that.wikis.wikiList = res.data.wikis;

		});

	},
	filters:{
		DateTimeFtt: TV_DateTimeFtt.formatter,
	}

});