
var vm = new Vue({
	el:'#app',
	data:{
		file: '',
			
	},
	
	methods:{
		handleFileUpload:function(){
			this.file = this.$refs.file.files[0];
		},
		submitFile:function(){
			var formData = new FormData();

            /*
                Add the form data we need to submit
            */
            formData.append('name', 'xieweizhong')
            formData.append('age', 40);
            formData.append('ufile', this.file);


        /*
          Make the request to the POST /single-file URL
        */
            axios.post( '/single-file',
                formData,
                {
                headers: {
                    'Content-Type': 'multipart/form-data'
	                }
	              }
	            ).then(function(){
	          console.log('SUCCESS!!');
	        })
	        .catch(function(){
	          console.log('FAILURE!!');
	        });
			}
		
	},

	//初始化页面数据
	created: function () {
    	
		
  	},
	
});
	