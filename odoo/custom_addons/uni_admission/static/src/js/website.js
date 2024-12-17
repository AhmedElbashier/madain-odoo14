odoo.define('uni_admission.website', function (require) {
	"use strict";

	$(document).ready(function () {
		document.getElementById("image_upload").onchange = function () {
			var reader = new FileReader();

			reader.onload = function (e) {
				// get loaded data and render thumbnail.
				document.getElementById("image_preview").src = e.target.result;
			};

			// read the image file as a data URL.
			reader.readAsDataURL(this.files[0]);
		}
	});

});
