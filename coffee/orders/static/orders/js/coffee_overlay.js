/* coffee_overlay.js
	depends on jQuery
*/

var CoffeeOverlay = (function ($) {
	'use strict';

	function CoffeeOverlay(coffee_elt) {
		this.$coffee_elt = $(coffee_elt);
		this.$coffee_elt.data('object', this);
		this.over_overlay = false;
	}

	CoffeeOverlay.prototype.attach_events = function() {
		this.$coffee_elt.mouseover(this.start_show_timer.bind(this));
		this.$coffee_elt.mouseout(this.stop_show_timer.bind(this));
	};

	CoffeeOverlay.prototype.start_show_timer = function(e) {
		this.is_timer_active = true;
		this.show_wait_cursor();

		window.setTimeout(function () {
			if (this.is_timer_active) {
				this.show();
				this.reset_cursor();
			}
		}.bind(this), 1000);
	};

	CoffeeOverlay.prototype.stop_show_timer = function() {
		window.setTimeout(function () {
			if (this.over_overlay) return;

			this.is_timer_active = false;
			this.reset_cursor();
			if (!this.over_overlay) {
				$('.overlay', this.$coffee_elt).fadeOut(function () { this.remove(); });
			}
		}.bind(this), 500);
	};

	CoffeeOverlay.prototype.show_wait_cursor = function() {
		this.$coffee_elt.addClass('wait');
	};

	CoffeeOverlay.prototype.reset_cursor = function() {
		this.$coffee_elt.removeClass('wait');
	};

	CoffeeOverlay.prototype.overlay_mouseover = function(e) {
		this.over_overlay = true;
	};

	CoffeeOverlay.prototype.overlay_mouseout = function(e) {
		this.over_overlay = false;
		this.stop_show_timer();
	};

	CoffeeOverlay.prototype.show = function() {
		if (this.over_overlay) return;

		var id = this.$coffee_elt.data('coffeeid');

		$.ajax({
			url: '/orders/coffee/'+id+'/overlay',
			dataType: 'html',
			type: 'get'
		})

		.done(function (data) {

			var $o = $('<div class="overlay">');
			$o.append($(data));
			$o.mouseover(this.overlay_mouseover.bind(this)).mouseout(this.overlay_mouseout.bind(this));
			$o.hide();
			this.$coffee_elt.append($o);
			$o.fadeIn();

		}.bind(this))

		.fail(function (xhr, status, err) {

			this.$coffee_elt.append($('<span class="error overlay">'+(status + ': ' + err)+'</span>'));

		}.bind(this));
	};

	return CoffeeOverlay;

}(jQuery));