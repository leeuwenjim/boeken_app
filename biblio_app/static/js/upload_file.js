var Upload = function (file, field_name, method, url, success = null, fail = null, progress = null) {
    this.file = file;
    this.method = method;
    this.url = url;
    this.success = success;
    this.fail = fail;
    this.progress = progress;
    this.field_name = field_name;
};

Upload.prototype.getType = function() {
    return this.file.type;
};
Upload.prototype.getSize = function() {
    return this.file.size;
};
Upload.prototype.getName = function() {
    return this.file.name;
};
Upload.prototype.send = function () {
    var that = this;
    var formData = new FormData();

    // add assoc key values, this will be posts values
    formData.append(this.field_name, this.file, this.getName());
    formData.append("upload_file", true);

    $.ajax({
        type: this.method,
        url: this.url,
        xhr: function () {
            var myXhr = $.ajaxSettings.xhr();
            if (myXhr.upload) {
                myXhr.upload.addEventListener('progress', that.progressHandling, false);
            }
            return myXhr;
        },
        success: function (data) {
            if (that.success) {
                that.success(data);
            }
        },
        error: function (error) {
            if (that.error) {
                that.error(error);
            }
        },
        async: true,
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        timeout: 60000
    });
};

Upload.prototype.progressHandling = (event) => {
    var percent = 0;
    var position = event.loaded || event.position;
    var total = event.total;

    if (event.lengthComputable) {
        percent = Math.ceil(position / total * 100);
    }
    // update progressbars classes so it fits your code
    if (this.progress) {
        this.progress(percent);
    }
};
